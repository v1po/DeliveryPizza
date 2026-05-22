"""
FastAPI dependencies for catalog service.
"""
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from .config import Settings, get_settings
from .repository import CategoryRepository, ModifierRepository, ProductRepository
from .service import CatalogService

import sys
sys.path.insert(0, "/app")
from shared.database import DatabaseManager
from shared.redis_client import RedisClient


# Global instances
db_manager: DatabaseManager | None = None
redis_client: RedisClient | None = None


def get_db_manager() -> DatabaseManager:
    if db_manager is None:
        raise RuntimeError("Database manager not initialized")
    return db_manager


def get_redis_client() -> RedisClient:
    if redis_client is None:
        raise RuntimeError("Redis client not initialized")
    return redis_client


async def get_session(
    db: DatabaseManager = Depends(get_db_manager),
) -> AsyncSession:
    async for session in db.get_session():
        yield session


async def get_catalog_service(
    session: AsyncSession = Depends(get_session),
    redis: RedisClient = Depends(get_redis_client),
    settings: Settings = Depends(get_settings),
) -> CatalogService:
    """Get catalog service instance."""
    category_repo = CategoryRepository(session)
    product_repo = ProductRepository(session)
    modifier_repo = ModifierRepository(session)
    
    return CatalogService(
        category_repo=category_repo,
        product_repo=product_repo,
        modifier_repo=modifier_repo,
        redis=redis,
        cache_ttl_categories=settings.cache_ttl_categories,
        cache_ttl_products=settings.cache_ttl_products,
        cache_ttl_menu=settings.cache_ttl_menu,
    )
