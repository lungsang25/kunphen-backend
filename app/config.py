from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/kunphen"
    cors_origins: str = "http://localhost:8080,http://localhost:5173"

    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    aws_region: str = "ap-south-1"
    s3_bucket: str = ""
    s3_upload_prefix: str = "uploads"

    google_client_id: str = ""
    allowed_emails: str = ""

    jwt_secret: str = "dev-secret-change-me"
    jwt_expire_minutes: int = 720

    dev_auth_enabled: bool = False

    # Google Analytics 4 (read side for the Studio dashboard).
    # ga4_property_id is the numeric property id (Admin > Property Settings),
    # NOT the "G-XXXX" measurement id used by the website tag.
    ga4_property_id: str = ""
    # Service-account key, either raw JSON or base64-encoded JSON. Base64 is the
    # safer form for Vercel env vars, which mangle embedded newlines.
    ga4_credentials_json: str = ""

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def allowed_email_list(self) -> list[str]:
        return [e.strip().lower() for e in self.allowed_emails.split(",") if e.strip()]

    @property
    def ga4_configured(self) -> bool:
        return bool(self.ga4_property_id and self.ga4_credentials_json)


settings = Settings()
