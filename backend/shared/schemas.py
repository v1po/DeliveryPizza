"""
Shared Pydantic schemas used across microservices.
"""
from datetime import datetime
from enum import Enum
from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# Generic type for pagination
T = TypeVar("T")


class OrderStatus(str, Enum):
    """Order status enumeration."""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PREPARING = "preparing"
    READY = "ready"
    DELIVERING = "delivering"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class UserRole(str, Enum):
    """User role enumeration."""
    CUSTOMER = "customer"
    ADMIN = "admin"
    MANAGER = "manager"
    COURIER = "courier"


# Base schemas
class BaseSchema(BaseModel):
    """Base schema with common configuration."""
    model_config = ConfigDict(from_attributes=True)


class TimestampMixin(BaseModel):
    """Mixin for timestamp fields."""
    created_at: datetime
    updated_at: datetime | None = None


# Pagination
class PaginationParams(BaseModel):
    """Pagination parameters."""
    page: int = Field(default=1, ge=1, description="Page number")
    size: int = Field(default=20, ge=1, le=100, description="Items per page")
    
    @property
    def offset(self) -> int:
        return (self.page - 1) * self.size


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response."""
    items: list[T]
    total: int
    page: int
    size: int
    pages: int
    
    @classmethod
    def create(
        cls,
        items: list[T],
        total: int,
        page: int,
        size: int,
    ) -> "PaginatedResponse[T]":
        pages = (total + size - 1) // size if size > 0 else 0
        return cls(
            items=items,
            total=total,
            page=page,
            size=size,
            pages=pages,
        )


# Response wrappers
class ResponseWrapper(BaseModel, Generic[T]):
    """Standard API response wrapper."""
    success: bool = True
    message: str = "Success"
    data: T | None = None


class ErrorResponse(BaseModel):
    """Error response schema."""
    success: bool = False
    message: str
    detail: str | None = None
    error_code: str | None = None


# User schemas (shared between services)
class UserBase(BaseSchema):
    """Base user schema."""
    email: EmailStr
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    phone: str | None = Field(default=None, max_length=20)


class UserPublic(UserBase, TimestampMixin):
    """Public user information."""
    id: int
    role: UserRole
    is_active: bool


class TokenPayload(BaseModel):
    """JWT token payload."""
    sub: int  # user_id
    email: str
    role: UserRole
    exp: datetime
    iat: datetime
    type: str  # "access" or "refresh"
