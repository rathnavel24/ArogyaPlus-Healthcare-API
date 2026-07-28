from datetime import datetime

from sqlalchemy import JSON, DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base


class SiteContent(Base):
    """Singleton row (id is always 1) holding the editable public-site copy."""

    __tablename__ = "site_content"

    id: Mapped[int] = mapped_column(primary_key=True)

    hero_eyebrow: Mapped[str] = mapped_column(String(200), default="", nullable=False)
    hero_title: Mapped[str] = mapped_column(String(300), default="", nullable=False)
    hero_subtitle: Mapped[str] = mapped_column(Text, default="", nullable=False)
    hero_stats: Mapped[list] = mapped_column(JSON, default=list, nullable=False)

    trust_badges: Mapped[list] = mapped_column(JSON, default=list, nullable=False)

    why_title: Mapped[str] = mapped_column(String(200), default="", nullable=False)
    why_desc: Mapped[str] = mapped_column(Text, default="", nullable=False)
    why_cards: Mapped[list] = mapped_column(JSON, default=list, nullable=False)

    cta_title: Mapped[str] = mapped_column(String(200), default="", nullable=False)
    cta_subtitle: Mapped[str] = mapped_column(Text, default="", nullable=False)

    site_name: Mapped[str] = mapped_column(String(100), default="", nullable=False)
    site_tagline: Mapped[str] = mapped_column(String(150), default="", nullable=False)
    footer_text: Mapped[str] = mapped_column(String(300), default="", nullable=False)
    pkg_section_title: Mapped[str] = mapped_column(String(200), default="", nullable=False)
    pkg_section_desc: Mapped[str] = mapped_column(Text, default="", nullable=False)
    steps_title: Mapped[str] = mapped_column(String(200), default="", nullable=False)
    steps: Mapped[list] = mapped_column(JSON, default=list, nullable=False)

    testi_title: Mapped[str] = mapped_column(String(200), default="", nullable=False)
    testimonials: Mapped[list] = mapped_column(JSON, default=list, nullable=False)

    certifications_title: Mapped[str] = mapped_column(String(200), default="", nullable=False)
    lab_certifications: Mapped[list] = mapped_column(JSON, default=list, nullable=False)

    faq_title: Mapped[str] = mapped_column(String(200), default="", nullable=False)
    faq_items: Mapped[list] = mapped_column(JSON, default=list, nullable=False)

    social_facebook: Mapped[str | None] = mapped_column(String(300), nullable=True)
    social_instagram: Mapped[str | None] = mapped_column(String(300), nullable=True)
    social_twitter: Mapped[str | None] = mapped_column(String(300), nullable=True)
    social_linkedin: Mapped[str | None] = mapped_column(String(300), nullable=True)

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
