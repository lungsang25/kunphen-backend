from fastapi import APIRouter

from app.schemas.auth import GoogleLoginIn, TokenOut
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
