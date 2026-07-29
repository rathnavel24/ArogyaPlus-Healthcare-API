from typing import Literal

from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.security import get_current_admin
from app.models.admin import Admin
from app.models.package import Package
from app.models.test import Test
from app.schemas.package import PackageCreate, PackageOut, PackageUpdate

public_router = APIRouter(prefix="/api/packages", tags=["packages"])
admin_router = APIRouter(prefix="/api/admin/packages", tags=["admin-packages"])


def _apply_filters(query, search: str | None, category: str | None):
    if search:
        query = query.filter(Package.name.ilike(f"%{search}%"))
    if category:
        query = query.filter(Package.category == category)
    return query


def _apply_sort(query, sort: str | None, visit_mode: str = "lab"):
    price_column = Package.home_price if visit_mode == "home" else Package.lab_price
    if sort == "price_asc":
        return query.order_by(price_column.asc())
    if sort == "price_desc":
        return query.order_by(price_column.desc())
    return query.order_by(Package.name.asc())


@public_router.get("", response_model=list[PackageOut])
def list_packages(
    search: str | None = None,
    category: str | None = None,
    sort: Literal["price_asc", "price_desc"] | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(Package).filter(Package.is_active.is_(True), Package.status != -1)
    query = _apply_filters(query, search, category)
    query = _apply_sort(query, sort)
    return query.all()


@public_router.get("/{package_id}", response_model=PackageOut)
def get_package(package_id: int, db: Session = Depends(get_db)):
    package = db.get(Package, package_id)
    if package is None or not package.is_active or package.status == -1:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Package not found.")
    return package


@admin_router.get("", response_model=list[PackageOut])
def admin_list_packages(db: Session = Depends(get_db), current_admin: Admin = Depends(get_current_admin)):
    return db.query(Package).filter(Package.status != -1).order_by(Package.name.asc()).all()


@admin_router.get("/{package_id}", response_model=PackageOut)
def admin_get_package(
    package_id: int, db: Session = Depends(get_db), current_admin: Admin = Depends(get_current_admin)
):
    package = db.get(Package, package_id)
    if package is None or package.status == -1:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Package not found.")
    return package


@admin_router.post("", response_model=PackageOut, status_code=status.HTTP_201_CREATED)
def create_package(
    payload: PackageCreate, db: Session = Depends(get_db), current_admin: Admin = Depends(get_current_admin)
):
    data = payload.model_dump(exclude={"test_ids"})
    package = Package(**data)

    if payload.test_ids:
        package.tests = db.query(Test).filter(Test.id.in_(payload.test_ids), Test.status != -1).all()

    db.add(package)
    db.commit()
    db.refresh(package)
    return package


@admin_router.put("/{package_id}", response_model=PackageOut)
def update_package(
    package_id: int,
    payload: PackageUpdate,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
):
    package = db.get(Package, package_id)
    if package is None or package.status == -1:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Package not found.")

    update_data = payload.model_dump(exclude_unset=True, exclude={"test_ids"})
    for field, value in update_data.items():
        setattr(package, field, value)

    if payload.test_ids is not None:
        package.tests = db.query(Test).filter(Test.id.in_(payload.test_ids), Test.status != -1).all()

    db.commit()
    db.refresh(package)
    return package


@admin_router.delete("/{package_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_package(
    package_id: int, db: Session = Depends(get_db), current_admin: Admin = Depends(get_current_admin)
):
    package = db.get(Package, package_id)
    if package is None or package.status == -1:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Package not found.")
    package.status = -1
    db.commit()
    return None


@admin_router.patch("/{package_id}/tests", response_model=PackageOut)
def set_package_tests(
    package_id: int,
    test_ids: list[int] = Body(..., embed=True),
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
):
    package = db.get(Package, package_id)
    if package is None or package.status == -1:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Package not found.")

    package.tests = db.query(Test).filter(Test.id.in_(test_ids), Test.status != -1).all()
    db.commit()
    db.refresh(package)
    return package


@admin_router.delete("/{package_id}/tests/{test_id}", response_model=PackageOut)
def remove_package_test(
    package_id: int,
    test_id: int,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
):
    package = db.get(Package, package_id)
    if package is None or package.status == -1:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Package not found.")

    package.tests = [t for t in package.tests if t.id != test_id]
    db.commit()
    db.refresh(package)
    return package
