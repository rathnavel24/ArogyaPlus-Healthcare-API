from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class TestBase(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    description: str | None = None
    category: str | None = Field(default=None, max_length=100)
    lab_price: Decimal = Field(ge=0)
    home_price: Decimal = Field(ge=0)
    original_lab_price: Decimal | None = Field(default=None, ge=0)
    original_home_price: Decimal | None = Field(default=None, ge=0)
    tat: str | None = Field(default=None, max_length=50)
    is_active: bool = True


class TestCreate(TestBase):
    pass


class TestUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=150)
    description: str | None = None
    category: str | None = Field(default=None, max_length=100)
    lab_price: Decimal | None = Field(default=None, ge=0)
    home_price: Decimal | None = Field(default=None, ge=0)
    original_lab_price: Decimal | None = Field(default=None, ge=0)
    original_home_price: Decimal | None = Field(default=None, ge=0)
    tat: str | None = Field(default=None, max_length=50)
    is_active: bool | None = None


class TestOut(TestBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
