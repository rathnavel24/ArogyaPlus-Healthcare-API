from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.security import get_current_admin
from app.models.admin import Admin
from app.schemas.auth import AdminOut, AdminProfileUpdate, LoginRequest, Token
from app.services.auth_service import authenticate_admin, issue_token_for_admin, update_admin_profile

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=Token)
def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    admin = authenticate_admin(db, credentials.username, credentials.password)
    if admin is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password.",
        )
    token = issue_token_for_admin(admin)
    return Token(access_token=token)


@router.get("/me", response_model=AdminOut)
def get_me(current_admin: Admin = Depends(get_current_admin)):
    return current_admin


@router.patch("/me", response_model=AdminOut)
def update_me(
    payload: AdminProfileUpdate,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
):
    return update_admin_profile(db, current_admin, payload)
