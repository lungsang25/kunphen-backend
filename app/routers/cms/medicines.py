from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Medicine
from app.schemas.medicine import MedicineCreate, MedicineOut, MedicineUpdate
from app.services.auth import get_current_admin

router = APIRouter(
    prefix="/medicines",
    tags=["cms-medicines"],
    dependencies=[Depends(get_current_admin)],
)


@router.get("", response_model=list[MedicineOut])
def list_medicines(db: Session = Depends(get_db)):
    return db.scalars(select(Medicine).order_by(Medicine.id)).all()


@router.post("", response_model=MedicineOut, status_code=201)
def create_medicine(body: MedicineCreate, db: Session = Depends(get_db)):
    med = Medicine(**body.model_dump())
    db.add(med)
    db.commit()
    db.refresh(med)
    return med


@router.get("/{medicine_id}", response_model=MedicineOut)
def get_medicine(medicine_id: int, db: Session = Depends(get_db)):
    med = db.get(Medicine, medicine_id)
    if not med:
        raise HTTPException(status_code=404, detail="Medicine not found")
    return med


@router.put("/{medicine_id}", response_model=MedicineOut)
def update_medicine(
    medicine_id: int, body: MedicineUpdate, db: Session = Depends(get_db)
):
    med = db.get(Medicine, medicine_id)
    if not med:
        raise HTTPException(status_code=404, detail="Medicine not found")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(med, field, value)
    db.commit()
    db.refresh(med)
    return med


@router.delete("/{medicine_id}", status_code=204)
def delete_medicine(medicine_id: int, db: Session = Depends(get_db)):
    med = db.get(Medicine, medicine_id)
    if not med:
        raise HTTPException(status_code=404, detail="Medicine not found")
    db.delete(med)
    db.commit()
