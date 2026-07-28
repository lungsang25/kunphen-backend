from fastapi import APIRouter, Depends

from app.schemas.auth import PresignIn, PresignOut
from app.services.auth import get_current_admin
from app.services.s3 import create_presigned_upload

router = APIRouter(
    prefix="/uploads",
    tags=["cms-uploads"],
    dependencies=[Depends(get_current_admin)],
)


@router.post("/presign", response_model=PresignOut)
def presign_upload(body: PresignIn):
    return create_presigned_upload(body.filename, body.content_type)
