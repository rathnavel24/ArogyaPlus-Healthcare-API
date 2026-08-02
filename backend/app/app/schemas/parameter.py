from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ParameterBase(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    unit: str | None = Field(default=None, max_length=50)
    reference_range: str | None = Field(default=None, max_length=100)
    method: str | None = Field(default=None, max_length=100)
    description: str | None = None
    is_active: bool = True


class ParameterCreate(ParameterBase):
    pass


class ParameterUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=150)
    unit: str | None = Field(default=None, max_length=50)
    reference_range: str | None = Field(default=None, max_length=100)
    method: str | None = Field(default=None, max_length=100)
    description: str | None = None
    is_active: bool | None = None


class ParameterOut(ParameterBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
