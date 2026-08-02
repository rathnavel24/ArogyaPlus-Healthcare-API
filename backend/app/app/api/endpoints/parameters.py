from fastapi import APIRouter, Depends, HTTPException, Query, status
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
    query = db.query(Parameter).filter(Parameter.status != -1)
    if search:
        query = query.filter(Parameter.name.ilike(f"%{search}%"))
    query = query.order_by(Parameter.name.asc())
    return paginate_query(query, page, page_size)


@admin_router.post("", response_model=ParameterOut, status_code=status.HTTP_201_CREATED)
def create_parameter(
    payload: ParameterCreate, db: Session = Depends(get_db), current_admin: Admin = Depends(get_current_admin)
):
    existing = (
        db.query(Parameter).filter(Parameter.name == payload.name, Parameter.status != -1).first()
    )
    if existing is not None:
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
        duplicate = (
            db.query(Parameter)
            .filter(Parameter.name == update_data["name"], Parameter.id != parameter_id, Parameter.status != -1)
            .first()
        )
        if duplicate is not None:
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

    db.query(TestParameter).filter(TestParameter.parameter_id == parameter_id).delete()
    parameter.status = -1
    db.commit()
    return None
