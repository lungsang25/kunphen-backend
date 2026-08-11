from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import GalleryAlbum, GalleryImage
from app.schemas.gallery import GalleryAlbumCreate, GalleryAlbumOut, GalleryAlbumUpdate
from app.services.auth import get_current_admin

router = APIRouter(
    prefix="/gallery",
    tags=["cms-gallery"],
    dependencies=[Depends(get_current_admin)],
)


def _build_images(images) -> list[GalleryImage]:
    """Turn the ordered payload list into child rows, numbering them by position."""
    return [
        GalleryImage(image_url=img.image_url, caption=img.caption, sort_order=i)
        for i, img in enumerate(images)
    ]


@router.get("", response_model=list[GalleryAlbumOut])
def list_gallery_albums(db: Session = Depends(get_db)):
    return db.scalars(
        select(GalleryAlbum).order_by(GalleryAlbum.sort_order, GalleryAlbum.id)
    ).all()


@router.get("/{album_id}", response_model=GalleryAlbumOut)
def get_gallery_album(album_id: int, db: Session = Depends(get_db)):
    album = db.get(GalleryAlbum, album_id)
    if not album:
        raise HTTPException(status_code=404, detail="Gallery album not found")
    return album


@router.post("", response_model=GalleryAlbumOut, status_code=201)
def create_gallery_album(body: GalleryAlbumCreate, db: Session = Depends(get_db)):
    album = GalleryAlbum(
        title=body.title,
        sort_order=body.sort_order,
        images=_build_images(body.images),
    )
    db.add(album)
    db.commit()
    db.refresh(album)
    return album


@router.put("/{album_id}", response_model=GalleryAlbumOut)
def update_gallery_album(
    album_id: int, body: GalleryAlbumUpdate, db: Session = Depends(get_db)
):
    album = db.get(GalleryAlbum, album_id)
    if not album:
        raise HTTPException(status_code=404, detail="Gallery album not found")

    data = body.model_dump(exclude_unset=True)
    # The image list is replaced wholesale so positions stay contiguous; delete-orphan
    # cleans up the rows that dropped out.
    if "images" in data:
        del data["images"]
        album.images = _build_images(body.images)
    for field, value in data.items():
        setattr(album, field, value)

    db.commit()
    db.refresh(album)
    return album


@router.delete("/{album_id}", status_code=204)
def delete_gallery_album(album_id: int, db: Session = Depends(get_db)):
    album = db.get(GalleryAlbum, album_id)
    if not album:
        raise HTTPException(status_code=404, detail="Gallery album not found")
    db.delete(album)
    db.commit()
