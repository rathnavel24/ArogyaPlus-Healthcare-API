from fastapi import HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.models.admin import Admin
from app.schemas.auth import AdminProfileUpdate


def authenticate_admin(db: Session, username_or_email: str, password: str) -> Admin | None:
    admin = (
        db.query(Admin)
        .filter(or_(Admin.username == username_or_email, Admin.email == username_or_email))
        .first()
    )
    if admin is None:
        return None
    if not verify_password(password, admin.password_hash):
        return None
    return admin


def issue_token_for_admin(admin: Admin) -> str:
    return create_access_token(subject=str(admin.id))


def update_admin_profile(db: Session, admin: Admin, payload: AdminProfileUpdate) -> Admin:
    if payload.new_password:
        if not payload.current_password or not verify_password(payload.current_password, admin.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect.",
            )
        admin.password_hash = hash_password(payload.new_password)

    if payload.email:
        admin.email = payload.email

    db.commit()
    db.refresh(admin)
    return admin
