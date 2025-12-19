"""
Catalog Service configuration.
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
    
    app_name: str = "Catalog Service"
    debug: bool = False
    
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/catalog_db"
    redis_url: str = "redis://localhost:6379"
    
    # Cache TTL (seconds)
    cache_ttl_categories: int = 300  # 5 minutes
    cache_ttl_products: int = 60  # 1 minute
    cache_ttl_menu: int = 120  # 2 minutes


@lru_cache
def get_settings() -> Settings:
    return Settings()
