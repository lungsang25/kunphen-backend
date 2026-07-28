from pydantic import BaseModel


class GoogleLoginIn(BaseModel):
    id_token: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    email: str
    name: str = ""
    picture: str = ""


class PresignIn(BaseModel):
    filename: str
    content_type: str


class PresignOut(BaseModel):
    upload_url: str
    public_url: str
    key: str
