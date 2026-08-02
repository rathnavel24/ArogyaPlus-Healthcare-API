import re
from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

TIME_SLOTS = [
    "07:00 AM", "08:00 AM", "09:00 AM", "10:00 AM", "11:00 AM", "12:00 PM",
    "01:00 PM", "02:00 PM", "03:00 PM", "04:00 PM", "05:00 PM", "06:00 PM",
]

NAME_PATTERN = re.compile(r"^[A-Za-z\s.'-]+$")
PHONE_PATTERN = re.compile(r"^\+?\d{7,15}$")


class BookingItemIn(BaseModel):
    item_type: Literal["package", "test"]
    item_id: int


class BookingItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    item_type: str
    item_id: int
    item_name: str
    price: Decimal
    quantity: int


class BookingCreate(BaseModel):
    customer_name: str = Field(min_length=2, max_length=150)
    age: int = Field(ge=1, le=99)
    gender: Literal["Male", "Female"]
    phone: str = Field(min_length=7, max_length=30)
    email: EmailStr
    address: str | None = None
    preferred_date: date
    time_slot: str
    visit_mode: Literal["home", "lab"]
    items: list[BookingItemIn] = Field(min_length=1)

    @field_validator("customer_name")
    @classmethod
    def name_has_no_numbers(cls, value: str) -> str:
        if not NAME_PATTERN.match(value.strip()):
            raise ValueError("Name must not contain numbers or special characters.")
        return value.strip()

    @field_validator("phone")
    @classmethod
    def phone_digits_only(cls, value: str) -> str:
        cleaned = re.sub(r"[\s\-()]", "", value.strip())
        if not PHONE_PATTERN.match(cleaned):
            raise ValueError(
                "Phone number must be digits only (7-15 digits), optionally prefixed with '+' and a country code."
            )
        return cleaned

    @field_validator("time_slot")
    @classmethod
    def valid_time_slot(cls, value: str) -> str:
        if value not in TIME_SLOTS:
            raise ValueError("Invalid time slot selected.")
        return value

    @field_validator("preferred_date")
    @classmethod
    def date_not_in_past(cls, value: date) -> date:
        if value < date.today():
            raise ValueError("Preferred date cannot be in the past.")
        return value


class BookingStatusUpdate(BaseModel):
    status: Literal["New", "Contacted", "Done"]


class BookingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    booking_reference: str
    customer_name: str
    age: int
    gender: str
    phone: str
    email: str
    address: str | None = None
    preferred_date: date
    time_slot: str
    visit_mode: str
    total_amount: Decimal
    status: str
    created_at: datetime
    updated_at: datetime
    items: list[BookingItemOut] = []


class BookingCreatedOut(BaseModel):
    booking_reference: str
    total_amount: Decimal
    status: str
    message: str = "Your booking has been received. Our team will contact you shortly."
