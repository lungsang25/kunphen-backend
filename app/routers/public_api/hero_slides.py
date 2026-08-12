from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import HeroSlide
from app.schemas.hero_slide import HeroSlideOut

router = APIRouter(prefix="/hero-slides", tags=["public-hero-slides"])


@router.get("", response_model=list[HeroSlideOut])
def list_hero_slides(db: Session = Depends(get_db)):
    return db.scalars(
        select(HeroSlide)
        .where(HeroSlide.is_active.is_(True))
        .order_by(HeroSlide.sort_order, HeroSlide.id)
    ).all()
