from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Application
    app_name: str = "FiberHub Egypt"
    app_env: Literal["development", "staging", "production"] = "development"
    debug: bool = False
    api_prefix: str = "/api/v1"
    cors_origins: str = "http://localhost:3000"

    # Database
    database_url: str = "postgresql+asyncpg://fiberhub:fiberhub_dev@localhost:5432/fiberhub"

    @property
    def async_database_url(self) -> str:
        url = self.database_url
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql+asyncpg://", 1)
        elif url.startswith("postgresql://"):
            url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
        return url
    database_echo: bool = False

    # JWT
    jwt_secret_key: str = "change-me-to-a-random-64-char-string-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 30

    # Token expiry
    verification_token_expire_hours: int = 24
    password_reset_token_expire_hours: int = 1

    # S3 / MinIO
    s3_endpoint_url: str | None = None
    s3_access_key: str = ""
    s3_secret_key: str = ""
    s3_bucket_name: str = "fiberhub"
    s3_region: str = "us-east-1"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Email
    smtp_host: str = "localhost"
    smtp_port: int = 1025
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from_email: str = "noreply@fiberhub.eg"
    smtp_from_name: str = "FiberHub Egypt"
    smtp_use_tls: bool = False

    # Frontend
    frontend_url: str = "http://localhost:3000"

    # File uploads
    max_file_size_mb: int = 10
    allowed_file_types: str = ".pdf,.doc,.docx,.xls,.xlsx,.jpg,.jpeg,.png"

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",")]

    @property
    def max_file_size_bytes(self) -> int:
        return self.max_file_size_mb * 1024 * 1024

    @property
    def allowed_file_type_list(self) -> list[str]:
        return [ext.strip().lower() for ext in self.allowed_file_types.split(",")]

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()
