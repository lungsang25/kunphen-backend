from datetime import datetime

from pydantic import BaseModel, ConfigDict


class GalleryImageBase(BaseModel):
    image_url: str
    caption: str = ""
    sort_order: int = 0


class GalleryImageCreate(GalleryImageBase):
    pass


class GalleryImageUpdate(BaseModel):
    image_url: str | None = None
    caption: str | None = None
    sort_order: int | None = None


class GalleryImageOut(GalleryImageBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
