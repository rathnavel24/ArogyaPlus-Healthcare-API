from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.security import get_current_admin
from app.models.admin import Admin
from app.models.test import Test
from app.schemas.test import TestCreate, TestOut, TestUpdate

public_router = APIRouter(prefix="/api/tests", tags=["tests"])
admin_router = APIRouter(prefix="/api/admin/tests", tags=["admin-tests"])


def _apply_sort(query, sort: str | None):
    if sort == "price_asc":
        return query.order_by(Test.lab_price.asc())
    if sort == "price_desc":
        return query.order_by(Test.lab_price.desc())
    return query.order_by(Test.name.asc())


@public_router.get("", response_model=list[TestOut])
def list_tests(
    search: str | None = None,
    category: str | None = None,
    sort: Literal["price_asc", "price_desc"] | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(Test).filter(Test.is_active.is_(True))
    if search:
        query = query.filter(Test.name.ilike(f"%{search}%"))
    if category:
        query = query.filter(Test.category == category)
    query = _apply_sort(query, sort)
    return query.all()


@public_router.get("/{test_id}", response_model=TestOut)
def get_test(test_id: int, db: Session = Depends(get_db)):
    test = db.get(Test, test_id)
    if test is None or not test.is_active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Test not found.")
    return test


@admin_router.get("", response_model=list[TestOut])
def admin_list_tests(db: Session = Depends(get_db), current_admin: Admin = Depends(get_current_admin)):
    return db.query(Test).order_by(Test.name.asc()).all()


@admin_router.get("/{test_id}", response_model=TestOut)
def admin_get_test(test_id: int, db: Session = Depends(get_db), current_admin: Admin = Depends(get_current_admin)):
    test = db.get(Test, test_id)
    if test is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Test not found.")
    return test


@admin_router.post("", response_model=TestOut, status_code=status.HTTP_201_CREATED)
def create_test(payload: TestCreate, db: Session = Depends(get_db), current_admin: Admin = Depends(get_current_admin)):
    test = Test(**payload.model_dump())
    db.add(test)
    db.commit()
    db.refresh(test)
    return test


@admin_router.put("/{test_id}", response_model=TestOut)
def update_test(
    test_id: int,
    payload: TestUpdate,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
):
    test = db.get(Test, test_id)
    if test is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Test not found.")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(test, field, value)

    db.commit()
    db.refresh(test)
    return test


@admin_router.delete("/{test_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_test(test_id: int, db: Session = Depends(get_db), current_admin: Admin = Depends(get_current_admin)):
    test = db.get(Test, test_id)
    if test is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Test not found.")
    db.delete(test)
    db.commit()
    return None
