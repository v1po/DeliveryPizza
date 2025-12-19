"""
Auth service business logic.
"""
from .models import User
from .repository import UserRepository
from .schemas import UserCreate, UserUpdate

import sys
sys.path.insert(0, "/app")
from shared.exceptions import (
    AlreadyExistsException,
    InvalidCredentialsException,
    NotFoundException,
    TokenBlacklistedException,
    TokenExpiredException,
)
from shared.redis_client import RedisClient
from shared.schemas import UserRole
from shared.security import SecurityManager


class AuthService:
    """Authentication and user management service."""
    
    def __init__(
        self,
        repository: UserRepository,
        security: SecurityManager,
        redis: RedisClient,
    ):
        self.repository = repository
        self.security = security
        self.redis = redis
    
    async def register(self, data: UserCreate) -> User:
        """Register new user."""
        # Check if email already exists
        existing = await self.repository.get_by_email(data.email)
        if existing:
            raise AlreadyExistsException("User with this email")
        
        # Hash password
        hashed_password = self.security.hash_password(data.password)
        
        # Create user
        user = await self.repository.create(
            email=data.email,
            hashed_password=hashed_password,
            first_name=data.first_name,
            last_name=data.last_name,
            phone=data.phone,
        )
        
        return user
    
    async def authenticate(
        self,
        email: str,
        password: str,
    ) -> tuple[User, str, str]:
        """Authenticate user and return tokens."""
        # Get user
        user = await self.repository.get_active_by_email(email)
        if not user:
            raise InvalidCredentialsException()
        
        # Verify password
        if not self.security.verify_password(password, user.hashed_password):
            raise InvalidCredentialsException()
        
        # Update last login
        await self.repository.update_last_login(user.id)
        
        # Create tokens
        access_token, refresh_token = self.security.create_token_pair(
            user_id=user.id,
            email=user.email,
            role=user.role,
        )
        
        return user, access_token, refresh_token
    
    async def refresh_tokens(
        self,
        refresh_token: str,
    ) -> tuple[str, str]:
        """Refresh access token using refresh token."""
        # Check if token is blacklisted
        if await self.redis.is_token_blacklisted(refresh_token):
            raise TokenBlacklistedException()
        
        # Decode token
        payload = self.security.decode_token(refresh_token)
        if not payload:
            raise InvalidCredentialsException("Invalid refresh token")
        
        if payload.type != "refresh":
            raise InvalidCredentialsException("Invalid token type")
        
        # Get user to verify they still exist and are active
        user = await self.repository.get_by_id(payload.sub)
        if not user or not user.is_active:
            raise InvalidCredentialsException("User not found or inactive")
        
        # Blacklist old refresh token
        expire_seconds = self.security.refresh_token_expire_days * 24 * 60 * 60
        await self.redis.blacklist_token(refresh_token, expire_seconds)
        
        # Create new tokens
        return self.security.create_token_pair(
            user_id=user.id,
            email=user.email,
            role=user.role,
        )
    
    async def logout(
        self,
        access_token: str,
        refresh_token: str | None = None,
    ) -> None:
        """Logout user by blacklisting tokens."""
        # Blacklist access token
        access_expire = self.security.access_token_expire_minutes * 60
        await self.redis.blacklist_token(access_token, access_expire)
        
        # Blacklist refresh token if provided
        if refresh_token:
            refresh_expire = self.security.refresh_token_expire_days * 24 * 60 * 60
            await self.redis.blacklist_token(refresh_token, refresh_expire)
    
    async def validate_token(self, token: str) -> User | None:
        """Validate access token and return user."""
        # Check blacklist
        if await self.redis.is_token_blacklisted(token):
            return None
        
        # Decode token
        payload = self.security.decode_token(token)
        if not payload or payload.type != "access":
            return None
        
        # Get user
        return await self.repository.get_by_id(payload.sub)
    
    async def get_user(self, user_id: int) -> User:
        """Get user by ID."""
        user = await self.repository.get_by_id(user_id)
        if not user:
            raise NotFoundException("User")
        return user
    
    async def update_user(self, user_id: int, data: UserUpdate) -> User:
        """Update user profile."""
        user = await self.repository.get_by_id(user_id)
        if not user:
            raise NotFoundException("User")
        
        update_data = data.model_dump(exclude_unset=True)
        if update_data:
            user = await self.repository.update(user_id, **update_data)
        
        return user
    
    async def change_password(
        self,
        user_id: int,
        current_password: str,
        new_password: str,
    ) -> None:
        """Change user password."""
        user = await self.repository.get_by_id(user_id)
        if not user:
            raise NotFoundException("User")
        
        # Verify current password
        if not self.security.verify_password(current_password, user.hashed_password):
            raise InvalidCredentialsException("Current password is incorrect")
        
        # Hash new password
        hashed_password = self.security.hash_password(new_password)
        await self.repository.update(user_id, hashed_password=hashed_password)
    
    async def update_user_role(
        self,
        user_id: int,
        role: UserRole,
    ) -> User:
        """Update user role (admin only)."""
        user = await self.repository.get_by_id(user_id)
        if not user:
            raise NotFoundException("User")
        
        return await self.repository.update(user_id, role=role)
    
    async def update_user_status(
        self,
        user_id: int,
        is_active: bool,
    ) -> User:
        """Update user active status (admin only)."""
        user = await self.repository.get_by_id(user_id)
        if not user:
            raise NotFoundException("User")
        
        return await self.repository.update(user_id, is_active=is_active)
    
    async def get_all_users(
        self,
        offset: int = 0,
        limit: int = 20,
        role: UserRole | None = None,
        is_active: bool | None = None,
    ) -> tuple[list[User], int]:
        """Get all users with pagination (admin only)."""
        return await self.repository.get_all(
            offset=offset,
            limit=limit,
            role=role,
            is_active=is_active,
        )
