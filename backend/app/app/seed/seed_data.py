"""
Development seed script for ArogyaPlus Healthcare.

Usage (from backend/app/):
    python -m app.seed.seed_data

Creates the single admin account (from environment variables) and a small
set of sample packages and tests with realistic AED pricing. Safe to run
multiple times - existing records are left untouched.
"""

from app.core.config import settings
from app.core.security import hash_password
from app.db.base import Base  # noqa: F401  (imports all models for metadata.create_all)
from app.db.session import SessionLocal, engine
from app.models.admin import Admin
from app.models.banner import Banner
from app.models.package import Package
from app.models.site_content import SiteContent
from app.models.test import Test

TESTS = [
    {
        "name": "Complete Hemogram (CBC)",
        "description": "Measures red cells, white cells and platelets to give a full picture of blood health.",
        "category": "Hematology",
        "lab_price": 60,
        "home_price": 90,
        "tat": "24 hours",
    },
    {
        "name": "Lipid Profile",
        "description": "Checks cholesterol and triglyceride levels to assess heart disease risk.",
        "category": "Biochemistry",
        "lab_price": 90,
        "home_price": 120,
        "original_lab_price": 150,
        "original_home_price": 190,
        "tat": "24 hours",
    },
    {
        "name": "Liver Function Test",
        "description": "Evaluates liver enzymes and proteins to assess liver health.",
        "category": "Biochemistry",
        "lab_price": 110,
        "home_price": 140,
        "tat": "24 hours",
    },
    {
        "name": "Kidney Function Test",
        "description": "Assesses kidney performance through creatinine, urea and electrolyte levels.",
        "category": "Biochemistry",
        "lab_price": 100,
        "home_price": 130,
        "tat": "24 hours",
    },
    {
        "name": "Thyroid Profile",
        "description": "Measures T3, T4 and TSH to evaluate thyroid gland function.",
        "category": "Hormone",
        "lab_price": 150,
        "home_price": 180,
        "tat": "24 hours",
    },
    {
        "name": "Vitamin D",
        "description": "Measures Vitamin D levels to check for deficiency.",
        "category": "Vitamins",
        "lab_price": 180,
        "home_price": 210,
        "tat": "48 hours",
    },
    {
        "name": "HbA1c",
        "description": "Reflects average blood sugar levels over the past 2-3 months.",
        "category": "Diabetes",
        "lab_price": 90,
        "home_price": 120,
        "original_lab_price": 130,
        "original_home_price": 165,
        "tat": "24 hours",
    },
]

PACKAGES = [
    {
        "name": "Vital Guard Silver Health Check",
        "description": "Essential health screening covering key blood, liver and kidney parameters.",
        "category": "Essential",
        "lab_price": 249,
        "home_price": 299,
        "original_lab_price": 449,
        "original_home_price": 549,
        "tat": "24 hours",
        "test_names": [
            "Complete Hemogram (CBC)",
            "Lipid Profile",
            "Liver Function Test",
            "Kidney Function Test",
        ],
    },
    {
        "name": "Complete Wellness Profile",
        "description": "Comprehensive full-body check-up covering blood, organ, hormone and vitamin health.",
        "category": "Comprehensive",
        "lab_price": 499,
        "home_price": 599,
        "original_lab_price": 999,
        "original_home_price": 1199,
        "tat": "48 hours",
        "featured": True,
        "test_names": [
            "Complete Hemogram (CBC)",
            "Lipid Profile",
            "Liver Function Test",
            "Kidney Function Test",
            "Thyroid Profile",
            "Vitamin D",
        ],
    },
    {
        "name": "Diabetes Health Profile",
        "description": "Focused screening for diabetes risk, management and related complications.",
        "category": "Specialized",
        "lab_price": 199,
        "home_price": 249,
        "tat": "24 hours",
        "test_names": [
            "HbA1c",
            "Lipid Profile",
            "Kidney Function Test",
        ],
    },
]


def seed_admin(db) -> None:
    existing = db.query(Admin).filter(Admin.username == settings.ADMIN_USERNAME).first()
    if existing:
        print(f"Admin '{settings.ADMIN_USERNAME}' already exists - skipped.")
        return

    admin = Admin(
        username=settings.ADMIN_USERNAME,
        email=settings.ADMIN_EMAIL,
        password_hash=hash_password(settings.ADMIN_PASSWORD),
    )
    db.add(admin)
    print(f"Created admin account '{settings.ADMIN_USERNAME}'.")


def seed_tests(db) -> dict[str, Test]:
    tests_by_name: dict[str, Test] = {}
    for data in TESTS:
        existing = db.query(Test).filter(Test.name == data["name"]).first()
        if existing:
            tests_by_name[data["name"]] = existing
            continue
        test = Test(**data)
        db.add(test)
        db.flush()
        tests_by_name[data["name"]] = test
        print(f"Created test '{data['name']}'.")
    return tests_by_name


def seed_packages(db, tests_by_name: dict[str, Test]) -> None:
    for data in PACKAGES:
        existing = db.query(Package).filter(Package.name == data["name"]).first()
        if existing:
            continue

        package = Package(
            name=data["name"],
            description=data["description"],
            category=data["category"],
            lab_price=data["lab_price"],
            home_price=data["home_price"],
            original_lab_price=data.get("original_lab_price"),
            original_home_price=data.get("original_home_price"),
            tat=data.get("tat"),
            is_featured=data.get("featured", False),
        )
        package.tests = [tests_by_name[name] for name in data["test_names"] if name in tests_by_name]
        db.add(package)
        print(f"Created package '{data['name']}'.")


def seed_site_content(db) -> None:
    existing = db.get(SiteContent, 1)
    if existing:
        print("Site content already exists - skipped.")
        return

    content = SiteContent(
        id=1,
        hero_eyebrow="Trusted by 50,000+ Families",
        hero_title="Comprehensive Healthcare, Made Simple.",
        hero_subtitle=(
            "Book trusted health packages and laboratory tests from the comfort of your home "
            "or at our partner locations."
        ),
        hero_stats=[
            {"value": "50,000+", "label": "Families Served"},
            {"value": "12+", "label": "Years of Trust"},
            {"value": "250+", "label": "Tests Available"},
            {"value": "98%", "label": "Happy Patients"},
        ],
        trust_badges=[
            {"title": "NABH Accredited Labs", "subtitle": "Government certified"},
            {"title": "HIPAA Compliant", "subtitle": "Your data is safe"},
            {"title": "Free Home Collection", "subtitle": "At your doorstep"},
            {"title": "Digital Reports in 48h", "subtitle": "With doctor review"},
        ],
        why_title="Healthcare You Can Trust",
        why_desc=(
            "We combine technology, certified labs, and compassionate care to give you the "
            "most complete health picture."
        ),
        why_cards=[
            {
                "icon": "🏅",
                "title": "NABH Certified",
                "description": "Every lab we partner with is government-accredited and quality-audited.",
            },
            {
                "icon": "🏠",
                "title": "Home Collection",
                "description": "Our trained phlebotomist arrives at your home within the time slot you choose.",
            },
            {
                "icon": "⚡",
                "title": "Fast Reports",
                "description": "Digital reports delivered to your email and app within 48 hours of sample pickup.",
            },
            {
                "icon": "👨‍⚕️",
                "title": "Doctor Consultation",
                "description": "Free 15-minute doctor consultation included with every Premium and above package.",
            },
            {
                "icon": "💳",
                "title": "Flexible Payment",
                "description": "Pay by card, bank transfer, or cash. Corporate billing available for businesses.",
            },
            {
                "icon": "🔔",
                "title": "Annual Reminders",
                "description": "We remind you when your annual health check is due - so you never miss one.",
            },
        ],
        cta_title="Start Your Health Journey Today",
        cta_subtitle=(
            "Join thousands of families who trust ArogyaPlus for their health checkups. "
            "Book now and get your results in 48 hours."
        ),
        site_name="ArogyaPlus Healthcare",
        site_tagline="Health Packages",
        footer_text="Your Health, Our Priority. Expert Home Care Services.",
        pkg_section_title="Popular Health Packages",
        pkg_section_desc=(
            "Preventive care and early detection from certified labs - with free home sample "
            "collection and digital reports delivered in 48 hours."
        ),
        steps_title="Booking in Four Simple Steps",
        steps=[
            {
                "icon": "Search",
                "title": "Pick a Package",
                "description": "Browse packages and choose what fits your health goals.",
            },
            {
                "icon": "CalendarCheck",
                "title": "Book a Slot",
                "description": "Select a convenient date and time.",
            },
            {
                "icon": "ClipboardCheck",
                "title": "Sample Collected",
                "description": "A certified professional collects the sample safely.",
            },
            {
                "icon": "FileHeart",
                "title": "Get Your Report",
                "description": "Receive your digital report and review the findings.",
            },
        ],
        testi_title="What Our Patients Say",
        testimonials=[
            {
                "name": "Fatima Al Suwaidi",
                "location": "Dubai Marina, Dubai",
                "rating": 5,
                "feedback": (
                    "The home visit was seamless - the technician arrived on time and my report was "
                    "ready the next day. Highly recommend ArogyaPlus."
                ),
            },
            {
                "name": "Rahul Menon",
                "location": "Business Bay, Dubai",
                "rating": 5,
                "feedback": (
                    "Booking a full health package took less than five minutes online. Clear pricing "
                    "and no surprises at all."
                ),
            },
            {
                "name": "Sara Al Hammadi",
                "location": "Jumeirah, Dubai",
                "rating": 4,
                "feedback": (
                    "Great experience mixing individual tests with a package in one booking. The staff "
                    "were professional and courteous."
                ),
            },
        ],
        certifications_title="Our Certified Labs",
        lab_certifications=[
            {
                "icon": "🏅",
                "title": "CAP Accredited",
                "subtitle": "College of American Pathologists certified partner labs",
            },
            {
                "icon": "🔬",
                "title": "ISO 15189 Certified",
                "subtitle": "Internationally recognized medical laboratory quality standard",
            },
            {
                "icon": "🇦🇪",
                "title": "DHA Approved",
                "subtitle": "Licensed by Dubai Health Authority",
            },
            {
                "icon": "✅",
                "title": "NABL Accredited",
                "subtitle": "National accreditation for testing and calibration labs",
            },
        ],
        faq_title="Frequently Asked Questions",
        faq_items=[
            {
                "question": "How does home sample collection work?",
                "answer": (
                    "Choose the Home Visit option at checkout, pick a convenient time slot, and a "
                    "certified phlebotomist will collect your sample at your doorstep."
                ),
            },
            {
                "question": "How long does it take to get my report?",
                "answer": "Most reports are delivered digitally within 24-48 hours of sample collection, depending on the tests booked.",
            },
            {
                "question": "Do I need to fast before my test?",
                "answer": (
                    "Some tests (like fasting blood sugar or lipid profile) require 8-12 hours of "
                    "fasting. Any preparation instructions are shown on the package or test details."
                ),
            },
            {
                "question": "Can I reschedule or cancel my booking?",
                "answer": "Yes, you can reschedule or cancel from your booking confirmation email up to 12 hours before your slot.",
            },
        ],
        social_facebook="",
        social_instagram="",
        social_twitter="",
        social_linkedin="",
    )
    db.add(content)
    print("Created default site content.")


def seed_banners(db) -> None:
    if db.query(Banner).count() > 0:
        print("Banners already exist - skipped.")
        return
    print("No default banners seeded - add them via the admin panel.")


def run_seed() -> None:
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        seed_admin(db)
        tests_by_name = seed_tests(db)
        seed_packages(db, tests_by_name)
        seed_site_content(db)
        seed_banners(db)
        db.commit()
        print("Seed complete.")
    finally:
        db.close()


if __name__ == "__main__":
    run_seed()
