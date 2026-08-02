from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.security import get_current_admin
from app.models.admin import Admin
from app.models.parameter import Parameter
from app.models.test import Test
from app.models.test_parameter import TestParameter
from app.schemas.pagination import PaginatedResponse
from app.schemas.test import TestCreate, TestOut, TestParameterLink, TestParameterReorder, TestUpdate
from app.utils import paginate_query

public_router = APIRouter(prefix="/api/tests", tags=["tests"])
admin_router = APIRouter(prefix="/api/admin/tests", tags=["admin-tests"])


def _apply_sort(query, sort: str | None):
    if sort == "price_asc":
        return query.order_by(Test.lab_price.asc())
    if sort == "price_desc":
        return query.order_by(Test.lab_price.desc())
    return query.order_by(Test.name.asc())


@public_router.get("", response_model=PaginatedResponse[TestOut])
def list_tests(
    search: str | None = None,
    category: str | None = None,
    sort: Literal["price_asc", "price_desc"] | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    query = db.query(Test).filter(Test.is_active.is_(True), Test.status != -1)
    if search:
        query = query.filter(Test.name.ilike(f"%{search}%"))
    if category:
        query = query.filter(Test.category == category)
    query = _apply_sort(query, sort)
    return paginate_query(query, page, page_size)


@public_router.get("/{test_id}", response_model=TestOut)
def get_test(test_id: int, db: Session = Depends(get_db)):
    test = db.get(Test, test_id)
    if test is None or not test.is_active or test.status == -1:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Test not found.")
    return test


@admin_router.get("", response_model=PaginatedResponse[TestOut])
def admin_list_tests(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
):
    query = db.query(Test).filter(Test.status != -1).order_by(Test.name.asc())
    return paginate_query(query, page, page_size)


@admin_router.get("/{test_id}", response_model=TestOut)
def admin_get_test(test_id: int, db: Session = Depends(get_db), current_admin: Admin = Depends(get_current_admin)):
    test = db.get(Test, test_id)
    if test is None or test.status == -1:
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
    if test is None or test.status == -1:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Test not found.")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(test, field, value)

    db.commit()
    db.refresh(test)
    return test


@admin_router.delete("/{test_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_test(test_id: int, db: Session = Depends(get_db), current_admin: Admin = Depends(get_current_admin)):
    test = db.get(Test, test_id)
    if test is None or test.status == -1:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Test not found.")
    test.status = -1
    db.commit()
    return None


@admin_router.post("/{test_id}/parameters", response_model=TestOut)
def add_test_parameter(
    test_id: int,
    payload: TestParameterLink,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
):
    test = db.get(Test, test_id)
    if test is None or test.status == -1:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Test not found.")

    parameter = db.get(Parameter, payload.parameter_id)
    if parameter is None or parameter.status == -1:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Parameter not found.")

    existing_link = db.get(TestParameter, (test_id, payload.parameter_id))
    if existing_link is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Parameter is already linked to this test."
        )

    max_position = db.query(func.max(TestParameter.position)).filter(TestParameter.test_id == test_id).scalar()
    next_position = 0 if max_position is None else max_position + 1

    link = TestParameter(test_id=test_id, parameter_id=payload.parameter_id, position=next_position)
    db.add(link)
    db.commit()
    db.refresh(test)
    return test


@admin_router.delete("/{test_id}/parameters/{parameter_id}", response_model=TestOut)
def remove_test_parameter(
    test_id: int,
    parameter_id: int,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
):
    test = db.get(Test, test_id)
    if test is None or test.status == -1:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Test not found.")

    link = db.get(TestParameter, (test_id, parameter_id))
    if link is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Parameter is not linked to this test.")

    db.delete(link)
    db.commit()
    db.refresh(test)
    return test


@admin_router.put("/{test_id}/parameters/reorder", response_model=TestOut)
def reorder_test_parameters(
    test_id: int,
    payload: TestParameterReorder,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
):
    test = db.get(Test, test_id)
    if test is None or test.status == -1:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Test not found.")

    current_links = db.query(TestParameter).filter(TestParameter.test_id == test_id).all()
    current_ids = {link.parameter_id for link in current_links}

    if set(payload.ordered_ids) != current_ids or len(payload.ordered_ids) != len(current_links):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ordered_ids must exactly match the test's currently linked parameters.",
        )

    links_by_parameter_id = {link.parameter_id: link for link in current_links}
    for position, parameter_id in enumerate(payload.ordered_ids):
        links_by_parameter_id[parameter_id].position = position

    db.commit()
    db.refresh(test)
    return test
