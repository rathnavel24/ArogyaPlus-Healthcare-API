from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class HeroStat(BaseModel):
    value: str = ""
    label: str = ""


class TrustBadge(BaseModel):
    title: str = ""
    subtitle: str = ""


class WhyCard(BaseModel):
    icon: str = ""
    title: str = ""
    description: str = ""


class Step(BaseModel):
    icon: str = ""
    title: str = ""
    description: str = ""


class Testimonial(BaseModel):
    name: str = ""
    location: str = ""
    rating: int = 5
    feedback: str = ""


class LabCertification(BaseModel):
    icon: str = ""
    title: str = ""
    subtitle: str = ""


class FAQItem(BaseModel):
    question: str = ""
    answer: str = ""


class SiteContentBase(BaseModel):
    hero_eyebrow: str = ""
    hero_title: str = ""
    hero_subtitle: str = ""
    hero_stats: list[HeroStat] = Field(default_factory=list)

    trust_badges: list[TrustBadge] = Field(default_factory=list)

    why_title: str = ""
    why_desc: str = ""
    why_cards: list[WhyCard] = Field(default_factory=list)

    cta_title: str = ""
    cta_subtitle: str = ""

    site_name: str = ""
    site_tagline: str = ""
    footer_text: str = ""
    pkg_section_title: str = ""
    pkg_section_desc: str = ""
    steps_title: str = ""
    steps: list[Step] = Field(default_factory=list)

    testi_title: str = ""
    testimonials: list[Testimonial] = Field(default_factory=list)

    certifications_title: str = ""
    lab_certifications: list[LabCertification] = Field(default_factory=list)

    faq_title: str = ""
    faq_items: list[FAQItem] = Field(default_factory=list)

    social_facebook: str | None = None
    social_instagram: str | None = None
    social_twitter: str | None = None
    social_linkedin: str | None = None


class SiteContentUpdate(BaseModel):
    hero_eyebrow: str | None = None
    hero_title: str | None = None
    hero_subtitle: str | None = None
    hero_stats: list[HeroStat] | None = None

    trust_badges: list[TrustBadge] | None = None

    why_title: str | None = None
    why_desc: str | None = None
    why_cards: list[WhyCard] | None = None

    cta_title: str | None = None
    cta_subtitle: str | None = None

    site_name: str | None = None
    site_tagline: str | None = None
    footer_text: str | None = None
    pkg_section_title: str | None = None
    pkg_section_desc: str | None = None
    steps_title: str | None = None
    steps: list[Step] | None = None

    testi_title: str | None = None
    testimonials: list[Testimonial] | None = None

    certifications_title: str | None = None
    lab_certifications: list[LabCertification] | None = None

    faq_title: str | None = None
    faq_items: list[FAQItem] | None = None

    social_facebook: str | None = None
    social_instagram: str | None = None
    social_twitter: str | None = None
    social_linkedin: str | None = None


class SiteContentOut(SiteContentBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    updated_at: datetime
