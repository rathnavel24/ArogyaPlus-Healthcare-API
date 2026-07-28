from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.security import get_current_admin
from app.models.admin import Admin
from app.models.site_content import SiteContent
from app.schemas.site_content import SiteContentOut, SiteContentUpdate

public_router = APIRouter(prefix="/api/content", tags=["content"])
admin_router = APIRouter(prefix="/api/admin/content", tags=["admin-content"])

SINGLETON_ID = 1


def _get_or_create(db: Session) -> SiteContent:
    content = db.get(SiteContent, SINGLETON_ID)
    if content is None:
        content = SiteContent(
            id=SINGLETON_ID,
            hero_stats=[],
            trust_badges=[],
            why_cards=[],
            steps=[],
            testimonials=[],
            lab_certifications=[],
            faq_items=[],
        )
        db.add(content)
        db.commit()
        db.refresh(content)
    return content


@public_router.get("", response_model=SiteContentOut)
def get_content(db: Session = Depends(get_db)):
    return _get_or_create(db)


@admin_router.get("", response_model=SiteContentOut)
def admin_get_content(db: Session = Depends(get_db), current_admin: Admin = Depends(get_current_admin)):
    return _get_or_create(db)


@admin_router.put("", response_model=SiteContentOut)
def update_content(
    payload: SiteContentUpdate,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
):
    content = _get_or_create(db)
    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(content, field, value)

    db.commit()
    db.refresh(content)
    return content
