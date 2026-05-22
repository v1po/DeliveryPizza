"""
Auth service Pydantic schemas.
"""
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, field_validator

import sys
sys.path.insert(0, "/app")
from shared.schemas import BaseSchema, TimestampMixin, UserRole


# Registration
class UserCreate(BaseModel):
    """User registration schema."""
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    phone: str | None = Field(default=None, max_length=20)
    
    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v


class UserResponse(BaseSchema, TimestampMixin):
    """User response schema."""
    id: int
    email: EmailStr
    first_name: str
    last_name: str
    phone: str | None
    role: UserRole
    is_active: bool
    is_verified: bool
    last_login: datetime | None


class UserUpdate(BaseModel):
    """User update schema."""
    first_name: str | None = Field(default=None, min_length=1, max_length=100)
    last_name: str | None = Field(default=None, min_length=1, max_length=100)
    phone: str | None = Field(default=None, max_length=20)


class PasswordChange(BaseModel):
    """Password change schema."""
    current_password: str
    new_password: str = Field(min_length=8, max_length=128)
    
    @field_validator("new_password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v


# Authentication
class LoginRequest(BaseModel):
    """Login request schema."""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Token response schema."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


class RefreshTokenRequest(BaseModel):
    """Refresh token request schema."""
    refresh_token: str


class LogoutRequest(BaseModel):
    """Logout request schema."""
    refresh_token: str | None = None


# Admin
class UserRoleUpdate(BaseModel):
    """User role update schema (admin only)."""
    role: UserRole


class UserStatusUpdate(BaseModel):
    """User status update schema (admin only)."""
    is_active: bool
