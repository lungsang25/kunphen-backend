from fastapi import APIRouter, HTTPException

from app.config import settings
from app.schemas.auth import DevLoginIn, GoogleLoginIn, TokenOut
from app.services.auth import create_session_token, verify_google_token

router = APIRouter(prefix="/auth", tags=["cms-auth"])


@router.post("/google", response_model=TokenOut)
def login_with_google(body: GoogleLoginIn):
    info = verify_google_token(body.id_token)
    email = info["email"].lower()
    return TokenOut(
        access_token=create_session_token(email),
        email=email,
        name=info.get("name", ""),
        picture=info.get("picture", ""),
    )


@router.post("/dev", response_model=TokenOut)
def login_dev(body: DevLoginIn):
    if not settings.dev_auth_enabled:
        raise HTTPException(status_code=404, detail="Not found")
    email = body.email.lower()
    return TokenOut(
        access_token=create_session_token(email),
        email=email,
        name="Dev User",
    )
