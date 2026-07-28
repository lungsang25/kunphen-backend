from datetime import datetime

from pydantic import BaseModel, ConfigDict


class MedicineBase(BaseModel):
    name: str
    tibetan_name: str = ""
    description: str = ""
    full_description: str = ""
    image_url: str = ""
    uses: list[str] = []


class MedicineCreate(MedicineBase):
    pass


class MedicineUpdate(BaseModel):
    name: str | None = None
    tibetan_name: str | None = None
    description: str | None = None
    full_description: str | None = None
    image_url: str | None = None
    uses: list[str] | None = None


class MedicineOut(MedicineBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
