"""
FastAPI dependencies for auth service.
"""
from typing import Annotated

from fastapi import Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from .config import Settings, get_settings
from .repository import UserRepository
from .service import AuthService

import sys
sys.path.insert(0, "/app")
from shared.database import DatabaseManager
from shared.exceptions import InvalidTokenException, PermissionDeniedException
from shared.redis_client import RedisClient
from shared.schemas import UserRole
from shared.security import SecurityManager


# Global instances (initialized in main.py lifespan)
db_manager: DatabaseManager | None = None
redis_client: RedisClient | None = None
security_manager: SecurityManager | None = None


def get_db_manager() -> DatabaseManager:
    """Get database manager."""
    if db_manager is None:
        raise RuntimeError("Database manager not initialized")
    return db_manager


def get_redis_client() -> RedisClient:
    """Get Redis client."""
    if redis_client is None:
        raise RuntimeError("Redis client not initialized")
    return redis_client


def get_security_manager() -> SecurityManager:
    """Get security manager."""
    if security_manager is None:
        raise RuntimeError("Security manager not initialized")
    return security_manager


async def get_session(
    db: DatabaseManager = Depends(get_db_manager),
) -> AsyncSession:
    """Get database session."""
    async for session in db.get_session():
        yield session


async def get_auth_service(
    session: AsyncSession = Depends(get_session),
    redis: RedisClient = Depends(get_redis_client),
    security: SecurityManager = Depends(get_security_manager),
) -> AuthService:
    """Get auth service instance."""
    repository = UserRepository(session)
    return AuthService(repository, security, redis)


async def get_current_user(
    authorization: Annotated[str | None, Header()] = None,
    service: AuthService = Depends(get_auth_service),
):
    """Get current authenticated user."""
    if not authorization or not authorization.startswith("Bearer "):
        raise InvalidTokenException()
    
    token = authorization.split(" ")[1]
    user = await service.validate_token(token)
    
    if not user:
        raise InvalidTokenException()
    
    return user


async def get_current_active_user(
    user = Depends(get_current_user),
):
    """Get current active user."""
    if not user.is_active:
        raise PermissionDeniedException("User account is deactivated")
    return user


def require_roles(*roles: UserRole):
    """Dependency factory for role-based access control."""
    async def role_checker(user = Depends(get_current_active_user)):
        if user.role not in roles:
            raise PermissionDeniedException(
                f"Required role: {', '.join(r.value for r in roles)}"
            )
        return user
    return role_checker


# Role-specific dependencies
get_admin_user = require_roles(UserRole.ADMIN)
get_manager_user = require_roles(UserRole.ADMIN, UserRole.MANAGER)
