from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class BannerBase(BaseModel):
    image_url: str = Field(min_length=1, max_length=2_000_000)
    title: str | None = Field(default=None, max_length=150)
    subtitle: str | None = Field(default=None, max_length=300)
    tags: str | None = Field(default=None, max_length=300)
    link_url: str | None = Field(default=None, max_length=500)
    display_order: int = 1
    is_active: bool = True


class BannerCreate(BannerBase):
    pass


class BannerUpdate(BaseModel):
    image_url: str | None = Field(default=None, min_length=1, max_length=2_000_000)
    title: str | None = Field(default=None, max_length=150)
    subtitle: str | None = Field(default=None, max_length=300)
    tags: str | None = Field(default=None, max_length=300)
    link_url: str | None = Field(default=None, max_length=500)
    display_order: int | None = None
    is_active: bool | None = None


class BannerOut(BannerBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
