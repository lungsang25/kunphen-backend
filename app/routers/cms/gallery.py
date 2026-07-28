from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import GalleryImage
from app.schemas.gallery import GalleryImageCreate, GalleryImageOut, GalleryImageUpdate
from app.services.auth import get_current_admin

router = APIRouter(
    prefix="/gallery",
    tags=["cms-gallery"],
    dependencies=[Depends(get_current_admin)],
)


@router.get("", response_model=list[GalleryImageOut])
def list_gallery_images(db: Session = Depends(get_db)):
    return db.scalars(
        select(GalleryImage).order_by(GalleryImage.sort_order, GalleryImage.id)
    ).all()


@router.post("", response_model=GalleryImageOut, status_code=201)
def create_gallery_image(body: GalleryImageCreate, db: Session = Depends(get_db)):
    image = GalleryImage(**body.model_dump())
    db.add(image)
    db.commit()
    db.refresh(image)
    return image


@router.put("/{image_id}", response_model=GalleryImageOut)
def update_gallery_image(
    image_id: int, body: GalleryImageUpdate, db: Session = Depends(get_db)
):
    image = db.get(GalleryImage, image_id)
    if not image:
        raise HTTPException(status_code=404, detail="Gallery image not found")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(image, field, value)
    db.commit()
    db.refresh(image)
    return image


@router.delete("/{image_id}", status_code=204)
def delete_gallery_image(image_id: int, db: Session = Depends(get_db)):
    image = db.get(GalleryImage, image_id)
    if not image:
        raise HTTPException(status_code=404, detail="Gallery image not found")
    db.delete(image)
    db.commit()
