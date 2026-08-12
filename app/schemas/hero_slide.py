from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class HeroSlideBase(BaseModel):
    image_url: str
    title: str = ""
    subtitle: str = ""
    sort_order: int = 0
    is_active: bool = True


class HeroSlideCreate(HeroSlideBase):
    pass


class HeroSlideUpdate(BaseModel):
    image_url: str | None = None
    title: str | None = None
    subtitle: str | None = None
    sort_order: int | None = None
    is_active: bool | None = None


class HeroSlideOut(HeroSlideBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class HeroSlideReorder(BaseModel):
    # Position in this list becomes the slide's sort_order.
    ids: list[int] = Field(..., min_length=1)
