from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.security import get_current_admin
from app.models.admin import Admin
from app.models.banner import Banner
from app.schemas.banner import BannerCreate, BannerOut, BannerUpdate

public_router = APIRouter(prefix="/api/banners", tags=["banners"])
admin_router = APIRouter(prefix="/api/admin/banners", tags=["admin-banners"])


@public_router.get("", response_model=list[BannerOut])
def list_banners(db: Session = Depends(get_db)):
    return (
        db.query(Banner)
        .filter(Banner.is_active.is_(True), Banner.status != -1)
        .order_by(Banner.display_order.asc(), Banner.id.asc())
        .all()
    )


@admin_router.get("", response_model=list[BannerOut])
def admin_list_banners(db: Session = Depends(get_db), current_admin: Admin = Depends(get_current_admin)):
    return (
        db.query(Banner)
        .filter(Banner.status != -1)
        .order_by(Banner.display_order.asc(), Banner.id.asc())
        .all()
    )


@admin_router.post("", response_model=BannerOut, status_code=status.HTTP_201_CREATED)
def create_banner(
    payload: BannerCreate, db: Session = Depends(get_db), current_admin: Admin = Depends(get_current_admin)
):
    banner = Banner(**payload.model_dump())
    db.add(banner)
    db.commit()
    db.refresh(banner)
    return banner


@admin_router.put("/{banner_id}", response_model=BannerOut)
def update_banner(
    banner_id: int,
    payload: BannerUpdate,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
):
    banner = db.get(Banner, banner_id)
    if banner is None or banner.status == -1:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Banner not found.")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(banner, field, value)

    db.commit()
    db.refresh(banner)
    return banner


@admin_router.delete("/{banner_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_banner(banner_id: int, db: Session = Depends(get_db), current_admin: Admin = Depends(get_current_admin)):
    banner = db.get(Banner, banner_id)
    if banner is None or banner.status == -1:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Banner not found.")
    banner.status = -1
    db.commit()
    return None
