from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Medicine
from app.schemas.medicine import MedicineOut

router = APIRouter(prefix="/medicines", tags=["public-medicines"])


@router.get("", response_model=list[MedicineOut])
def list_medicines(db: Session = Depends(get_db)):
    return db.scalars(select(Medicine).order_by(Medicine.id)).all()


@router.get("/{medicine_id}", response_model=MedicineOut)
def get_medicine(medicine_id: int, db: Session = Depends(get_db)):
    med = db.get(Medicine, medicine_id)
    if not med:
        raise HTTPException(status_code=404, detail="Medicine not found")
    return med
