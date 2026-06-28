import logging

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Auth
    admin_password_hash: str = ""
    jwt_secret: str = "change-me"

    # Database
    database_url: str = "postgresql+asyncpg://user:pass@localhost:5432/aicall"

    # Embeddings (GitHub Models)
    github_models_api_key: str = ""
    github_models_endpoint: str = "https://models.inference.ai.azure.com"

    # GitHub live tool
    github_token: str = ""
    github_username: str = ""

    # Cal.com booking
    cal_api_key: str = ""
    cal_event_type_id: int = 6147823

    # Vapi
    vapi_server_secret: str = ""

    # Cloudinary (resume storage)
    cloudinary_cloud_name: str = ""
    cloudinary_api_key: str = ""
    cloudinary_api_secret: str = ""

    # App
    max_upload_size_mb: int = 10
    is_prod: bool = True   # set IS_PROD=false in local .env to disable secure cookies
    log_level: str = "INFO"


settings = Settings()


def configure_logging() -> None:
    """Configure root logger — call once at startup."""
    level = getattr(logging, settings.log_level.upper(), logging.INFO)
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )
    # Silence noisy third-party libs
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
