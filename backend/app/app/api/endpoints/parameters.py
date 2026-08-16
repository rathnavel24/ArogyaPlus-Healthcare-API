from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.security import get_current_admin
from app.models.admin import Admin
from app.models.parameter import Parameter
from app.models.test_parameter import TestParameter
from app.schemas.pagination import PaginatedResponse
from app.schemas.parameter import ParameterCreate, ParameterOut, ParameterUpdate
from app.utils import paginate_query

admin_router = APIRouter(prefix="/api/admin/parameters", tags=["admin-parameters"])


@admin_router.get("", response_model=PaginatedResponse[ParameterOut])
def admin_list_parameters(
    search: str | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
):
    stmt = select(Parameter).where(Parameter.status != -1)
    if search:
        stmt = stmt.where(Parameter.name.ilike(f"%{search}%"))
    stmt = stmt.order_by(Parameter.name.asc())
    return paginate_query(db, stmt, page, page_size)


@admin_router.post("", response_model=ParameterOut, status_code=status.HTTP_201_CREATED)
def create_parameter(
    payload: ParameterCreate, db: Session = Depends(get_db), current_admin: Admin = Depends(get_current_admin)
):
    existing_id = db.scalar(
        select(Parameter.id).where(func.lower(Parameter.name) == payload.name.lower(), Parameter.status != -1)
    )
    if existing_id is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Parameter name is already taken.")

    parameter = Parameter(**payload.model_dump())
    db.add(parameter)
    db.commit()
    db.refresh(parameter)
    return parameter


@admin_router.put("/{parameter_id}", response_model=ParameterOut)
def update_parameter(
    parameter_id: int,
    payload: ParameterUpdate,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
):
    parameter = db.get(Parameter, parameter_id)
    if parameter is None or parameter.status == -1:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Parameter not found.")

    update_data = payload.model_dump(exclude_unset=True)

    if "name" in update_data:
        duplicate_id = db.scalar(
            select(Parameter.id).where(
                func.lower(Parameter.name) == update_data["name"].lower(),
                Parameter.id != parameter_id,
                Parameter.status != -1,
            )
        )
        if duplicate_id is not None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Parameter name is already taken.")

    for field, value in update_data.items():
        setattr(parameter, field, value)

    db.commit()
    db.refresh(parameter)
    return parameter


@admin_router.delete("/{parameter_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_parameter(
    parameter_id: int, db: Session = Depends(get_db), current_admin: Admin = Depends(get_current_admin)
):
    parameter = db.get(Parameter, parameter_id)
    if parameter is None or parameter.status == -1:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Parameter not found.")

    db.execute(delete(TestParameter).where(TestParameter.parameter_id == parameter_id))
    parameter.status = -1
    db.commit()
    return None
