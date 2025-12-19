"""
API Gateway configuration.
"""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
    
    app_name: str = "API Gateway"
    debug: bool = False
    
    # Service URLs
    auth_service_url: str = "http://auth:8001"
    catalog_service_url: str = "http://catalog:8002"
    order_service_url: str = "http://order:8003"
    
    # Redis
    redis_url: str = "redis://localhost:6379"
    
    # Rate limiting
    rate_limit_enabled: bool = True
    rate_limit_requests: int = 100
    rate_limit_period: int = 60  # seconds
    
    # Timeouts
    request_timeout: float = 30.0
    
    # CORS
    cors_origins: str = "*"


@lru_cache
def get_settings() -> Settings:
    return Settings()
