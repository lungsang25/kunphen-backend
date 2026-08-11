from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class GalleryImageIn(BaseModel):
    image_url: str
    caption: str = ""


class GalleryImageOut(GalleryImageIn):
    model_config = ConfigDict(from_attributes=True)

    id: int
    sort_order: int


class GalleryAlbumBase(BaseModel):
    title: str = ""
    sort_order: int = 0


class GalleryAlbumCreate(GalleryAlbumBase):
    # Position in the list is the position in the album; images[0] is the cover, so an
    # album always needs at least one image.
    images: list[GalleryImageIn] = Field(..., min_length=1)


class GalleryAlbumUpdate(BaseModel):
    title: str | None = None
    sort_order: int | None = None
    images: list[GalleryImageIn] | None = Field(default=None, min_length=1)


class GalleryAlbumOut(GalleryAlbumBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
    images: list[GalleryImageOut]
