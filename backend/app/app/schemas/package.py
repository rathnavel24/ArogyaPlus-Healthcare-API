from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.test import TestOut


class PackageBase(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    description: str | None = None
    category: str | None = Field(default=None, max_length=100)
    image_url: str | None = Field(default=None, max_length=500)
    lab_price: Decimal = Field(ge=0)
    home_price: Decimal = Field(ge=0)
    original_lab_price: Decimal | None = Field(default=None, ge=0)
    original_home_price: Decimal | None = Field(default=None, ge=0)
    tat: str | None = Field(default=None, max_length=50)
    is_active: bool = True
    is_featured: bool = False
    display_order: int | None = None


class PackageCreate(PackageBase):
    test_ids: list[int] = []


class PackageUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=150)
    description: str | None = None
    category: str | None = Field(default=None, max_length=100)
    image_url: str | None = Field(default=None, max_length=500)
    lab_price: Decimal | None = Field(default=None, ge=0)
    home_price: Decimal | None = Field(default=None, ge=0)
    original_lab_price: Decimal | None = Field(default=None, ge=0)
    original_home_price: Decimal | None = Field(default=None, ge=0)
    tat: str | None = Field(default=None, max_length=50)
    is_active: bool | None = None
    is_featured: bool | None = None
    display_order: int | None = None
    test_ids: list[int] | None = None


class PackageOut(PackageBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
    tests: list[TestOut] = []

    @property
    def test_count(self) -> int:
        return len(self.tests)
