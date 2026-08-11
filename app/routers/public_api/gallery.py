from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import GalleryAlbum
from app.schemas.gallery import GalleryAlbumOut

router = APIRouter(prefix="/gallery", tags=["public-gallery"])


@router.get("", response_model=list[GalleryAlbumOut])
def list_gallery_albums(db: Session = Depends(get_db)):
    return db.scalars(
        select(GalleryAlbum).order_by(GalleryAlbum.sort_order, GalleryAlbum.id)
    ).all()
