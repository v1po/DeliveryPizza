"""
FastAPI dependencies for order service.
"""
from typing import Annotated

from fastapi import Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from .clients import AuthClient, CatalogClient
from .config import Settings, get_settings
from .repository import OrderRepository
from .service import OrderService

import sys
sys.path.insert(0, "/app")
from shared.database import DatabaseManager
from shared.exceptions import InvalidTokenException, PermissionDeniedException
from shared.redis_client import RedisClient
from shared.schemas import UserRole


# Global instances
db_manager: DatabaseManager | None = None
redis_client: RedisClient | None = None
auth_client: AuthClient | None = None
catalog_client: CatalogClient | None = None


def get_db_manager() -> DatabaseManager:
    if db_manager is None:
        raise RuntimeError("Database manager not initialized")
    return db_manager


def get_redis_client() -> RedisClient:
    if redis_client is None:
        raise RuntimeError("Redis client not initialized")
    return redis_client


def get_auth_client() -> AuthClient:
    if auth_client is None:
        raise RuntimeError("Auth client not initialized")
    return auth_client


def get_catalog_client() -> CatalogClient:
    if catalog_client is None:
        raise RuntimeError("Catalog client not initialized")
    return catalog_client


async def get_session(
    db: DatabaseManager = Depends(get_db_manager),
) -> AsyncSession:
    async for session in db.get_session():
        yield session


async def get_order_service(
    session: AsyncSession = Depends(get_session),
    redis: RedisClient = Depends(get_redis_client),
    catalog: CatalogClient = Depends(get_catalog_client),
    settings: Settings = Depends(get_settings),
) -> OrderService:
    """Get order service instance."""
    repository = OrderRepository(
        session,
        order_number_prefix=settings.order_number_prefix,
    )
    
    return OrderService(
        repository=repository,
        catalog_client=catalog,
        redis=redis,
        min_order_amount=settings.min_order_amount,
        delivery_fee=settings.delivery_fee,
        free_delivery_threshold=settings.free_delivery_threshold,
    )


# User authentication via auth service
class CurrentUser:
    """Current authenticated user."""
    
    def __init__(self, id: int, email: str, role: UserRole):
        self.id = id
        self.email = email
        self.role = role


async def get_current_user(
    authorization: Annotated[str | None, Header()] = None,
    auth: AuthClient = Depends(get_auth_client),
) -> CurrentUser:
    """Get current authenticated user via auth service."""
    if not authorization or not authorization.startswith("Bearer "):
        raise InvalidTokenException()
    
    token = authorization.split(" ")[1]
    user_data = await auth.validate_token(token)
    
    if not user_data:
        raise InvalidTokenException()
    
    return CurrentUser(
        id=user_data["id"],
        email=user_data["email"],
        role=UserRole(user_data["role"]),
    )


async def get_current_active_user(
    user: CurrentUser = Depends(get_current_user),
) -> CurrentUser:
    """Get current active user."""
    return user


def require_roles(*roles: UserRole):
    """Dependency factory for role-based access control."""
    async def role_checker(user: CurrentUser = Depends(get_current_active_user)):
        if user.role not in roles:
            raise PermissionDeniedException(
                f"Required role: {', '.join(r.value for r in roles)}"
            )
        return user
    return role_checker


get_admin_user = require_roles(UserRole.ADMIN)
get_manager_user = require_roles(UserRole.ADMIN, UserRole.MANAGER)
get_courier_user = require_roles(UserRole.ADMIN, UserRole.MANAGER, UserRole.COURIER)
