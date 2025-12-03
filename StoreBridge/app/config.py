"""Application configuration using Pydantic settings."""

from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Environment
    environment: str = "development"

    # Database
    database_url: str = "postgresql://user:password@localhost:5432/storebridge"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Domeggook API
    domeggook_api_key: str = "test_key"
    domeggook_api_url: str = "https://openapi.domeggook.com"

    # Naver Commerce API
    naver_client_id: str = "test_client"
    naver_client_secret: str = "test_secret"
    naver_api_url: str = "https://api.commerce.naver.com"

    # S3 / MinIO
    s3_endpoint_url: Optional[str] = None
    s3_access_key: str = "test_access"
    s3_secret_key: str = "test_secret"
    s3_bucket_name: str = "storebridge-images"
    s3_region: str = "us-east-1"

    # Celery
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/0"

    # Monitoring
    sentry_dsn: Optional[str] = None
    prometheus_port: int = 9090

    # Rate Limiting
    naver_max_tps: int = 2
    naver_burst_max: int = 3
    domeggook_max_rpm: int = 180


settings = Settings()
