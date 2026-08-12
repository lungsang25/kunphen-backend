from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import HeroSlide
from app.schemas.hero_slide import (
    HeroSlideCreate,
    HeroSlideOut,
    HeroSlideReorder,
    HeroSlideUpdate,
)
from app.services.auth import get_current_admin

router = APIRouter(
    prefix="/hero-slides",
    tags=["cms-hero-slides"],
    dependencies=[Depends(get_current_admin)],
)


@router.get("", response_model=list[HeroSlideOut])
def list_hero_slides(db: Session = Depends(get_db)):
    return db.scalars(
        select(HeroSlide).order_by(HeroSlide.sort_order, HeroSlide.id)
    ).all()


@router.post("", response_model=HeroSlideOut, status_code=201)
def create_hero_slide(body: HeroSlideCreate, db: Session = Depends(get_db)):
    slide = HeroSlide(**body.model_dump())
    db.add(slide)
    db.commit()
    db.refresh(slide)
    return slide


# Declared before /{slide_id} so "reorder" isn't matched as a slide id.
@router.put("/reorder", response_model=list[HeroSlideOut])
def reorder_hero_slides(body: HeroSlideReorder, db: Session = Depends(get_db)):
    slides = db.scalars(select(HeroSlide)).all()
    by_id = {slide.id: slide for slide in slides}
    # A stale tab could send ids that no longer exist, or omit a slide someone else
    # added; either would leave the order half-applied, so reject the whole call.
    if set(body.ids) != set(by_id) or len(body.ids) != len(set(body.ids)):
        raise HTTPException(
            status_code=400, detail="Slide list is out of date — reload and try again"
        )

    for position, slide_id in enumerate(body.ids):
        by_id[slide_id].sort_order = position

    db.commit()
    return db.scalars(
        select(HeroSlide).order_by(HeroSlide.sort_order, HeroSlide.id)
    ).all()


@router.get("/{slide_id}", response_model=HeroSlideOut)
def get_hero_slide(slide_id: int, db: Session = Depends(get_db)):
    slide = db.get(HeroSlide, slide_id)
    if not slide:
        raise HTTPException(status_code=404, detail="Hero slide not found")
    return slide


@router.put("/{slide_id}", response_model=HeroSlideOut)
def update_hero_slide(
    slide_id: int, body: HeroSlideUpdate, db: Session = Depends(get_db)
):
    slide = db.get(HeroSlide, slide_id)
    if not slide:
        raise HTTPException(status_code=404, detail="Hero slide not found")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(slide, field, value)
    db.commit()
    db.refresh(slide)
    return slide


@router.delete("/{slide_id}", status_code=204)
def delete_hero_slide(slide_id: int, db: Session = Depends(get_db)):
    slide = db.get(HeroSlide, slide_id)
    if not slide:
        raise HTTPException(status_code=404, detail="Hero slide not found")
    db.delete(slide)
    db.commit()
