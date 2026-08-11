from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import GalleryImage
from app.schemas.gallery import GalleryImageOut

router = APIRouter(prefix="/gallery", tags=["public-gallery"])


@router.get("", response_model=list[GalleryImageOut])
def list_gallery_images(db: Session = Depends(get_db)):
    return db.scalars(
        select(GalleryImage).order_by(GalleryImage.sort_order, GalleryImage.id)
    ).all()
