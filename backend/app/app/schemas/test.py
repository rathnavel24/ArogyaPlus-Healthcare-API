from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.parameter import ParameterOut


class TestBase(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    description: str | None = None
    category: str | None = Field(default=None, max_length=100)
    sample_type: str | None = Field(default=None, max_length=100)
    image_url: str | None = Field(default=None, max_length=500)
    lab_price: Decimal = Field(ge=0)
    home_price: Decimal = Field(ge=0)
    original_lab_price: Decimal | None = Field(default=None, ge=0)
    original_home_price: Decimal | None = Field(default=None, ge=0)
    tat: str | None = Field(default=None, max_length=50)
    test_code: str | None = Field(default=None, max_length=50)
    b2b_price: Decimal | None = Field(default=None, ge=0)
    mrp: Decimal | None = Field(default=None, ge=0)
    parameters_count: int | None = None
    tube1: str | None = Field(default=None, max_length=50)
    tube2: str | None = Field(default=None, max_length=50)
    tube3: str | None = Field(default=None, max_length=50)
    tube4: str | None = Field(default=None, max_length=50)
    included_items: str | None = None
    is_active: bool = True
    display_order: int | None = None


class TestCreate(TestBase):
    pass


class TestUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=150)
    description: str | None = None
    category: str | None = Field(default=None, max_length=100)
    sample_type: str | None = Field(default=None, max_length=100)
    image_url: str | None = Field(default=None, max_length=500)
    lab_price: Decimal | None = Field(default=None, ge=0)
    home_price: Decimal | None = Field(default=None, ge=0)
    original_lab_price: Decimal | None = Field(default=None, ge=0)
    original_home_price: Decimal | None = Field(default=None, ge=0)
    tat: str | None = Field(default=None, max_length=50)
    test_code: str | None = Field(default=None, max_length=50)
    b2b_price: Decimal | None = Field(default=None, ge=0)
    mrp: Decimal | None = Field(default=None, ge=0)
    parameters_count: int | None = None
    tube1: str | None = Field(default=None, max_length=50)
    tube2: str | None = Field(default=None, max_length=50)
    tube3: str | None = Field(default=None, max_length=50)
    tube4: str | None = Field(default=None, max_length=50)
    included_items: str | None = None
    is_active: bool | None = None
    display_order: int | None = None


class TestOut(TestBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
    parameters: list[ParameterOut] = []


class TestParameterLink(BaseModel):
    parameter_id: int


class TestParameterReorder(BaseModel):
    ordered_ids: list[int]
