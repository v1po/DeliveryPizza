"""
Order Service configuration.
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
    
    app_name: str = "Order Service"
    debug: bool = False
    
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/order_db"
    redis_url: str = "redis://localhost:6379"
    
    # External services
    catalog_service_url: str = "http://catalog:8002"
    auth_service_url: str = "http://auth:8001"
    
    # Order settings
    order_number_prefix: str = "ORD"
    min_order_amount: float = 10.0
    delivery_fee: float = 5.0
    free_delivery_threshold: float = 50.0


@lru_cache
def get_settings() -> Settings:
    return Settings()
