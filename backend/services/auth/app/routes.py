"""
Auth API routes.
"""
from typing import Annotated

from fastapi import APIRouter, Depends, Header, Query, status

from .dependencies import (
    get_admin_user,
    get_auth_service,
    get_current_active_user,
)
from .models import User
from .schemas import (
    LoginRequest,
    LogoutRequest,
    PasswordChange,
    RefreshTokenRequest,
    TokenResponse,
    UserCreate,
    UserResponse,
    UserRoleUpdate,
    UserStatusUpdate,
    UserUpdate,
)
from .service import AuthService

import sys
sys.path.insert(0, "/app")
from shared.schemas import (
    PaginatedResponse,
    PaginationParams,
    ResponseWrapper,
    UserRole,
)


router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])


# ==================== Public endpoints ====================

@router.post(
    "/register",
    response_model=ResponseWrapper[UserResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Register new user",
)
async def register(
    data: UserCreate,
    service: AuthService = Depends(get_auth_service),
):
    """Register a new user account."""
    user = await service.register(data)
    return ResponseWrapper(
        message="User registered successfully",
        data=UserResponse.model_validate(user),
    )


@router.post(
    "/login",
    response_model=ResponseWrapper[TokenResponse],
    summary="User login",
)
async def login(
    data: LoginRequest,
    service: AuthService = Depends(get_auth_service),
):
    """Authenticate user and return access tokens."""
    user, access_token, refresh_token = await service.authenticate(
        email=data.email,
        password=data.password,
    )
    
    return ResponseWrapper(
        message="Login successful",
        data=TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=30 * 60,  # 30 minutes in seconds
        ),
    )


@router.post(
    "/refresh",
    response_model=ResponseWrapper[TokenResponse],
    summary="Refresh access token",
)
async def refresh_token(
    data: RefreshTokenRequest,
    service: AuthService = Depends(get_auth_service),
):
    """Refresh access token using refresh token."""
    access_token, refresh_token = await service.refresh_tokens(data.refresh_token)
    
    return ResponseWrapper(
        message="Token refreshed successfully",
        data=TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=30 * 60,
        ),
    )


@router.post(
    "/logout",
    response_model=ResponseWrapper[None],
    summary="User logout",
)
async def logout(
    data: LogoutRequest,
    authorization: Annotated[str | None, Header()] = None,
    service: AuthService = Depends(get_auth_service),
):
    """Logout user and invalidate tokens."""
    if authorization and authorization.startswith("Bearer "):
        access_token = authorization.split(" ")[1]
        await service.logout(access_token, data.refresh_token)
    
    return ResponseWrapper(message="Logged out successfully")


# ==================== Protected endpoints ====================

@router.get(
    "/me",
    response_model=ResponseWrapper[UserResponse],
    summary="Get current user",
)
async def get_me(
    user: User = Depends(get_current_active_user),
):
    """Get current authenticated user profile."""
    return ResponseWrapper(data=UserResponse.model_validate(user))


@router.patch(
    "/me",
    response_model=ResponseWrapper[UserResponse],
    summary="Update current user",
)
async def update_me(
    data: UserUpdate,
    user: User = Depends(get_current_active_user),
    service: AuthService = Depends(get_auth_service),
):
    """Update current user profile."""
    updated_user = await service.update_user(user.id, data)
    return ResponseWrapper(
        message="Profile updated successfully",
        data=UserResponse.model_validate(updated_user),
    )


@router.post(
    "/me/password",
    response_model=ResponseWrapper[None],
    summary="Change password",
)
async def change_password(
    data: PasswordChange,
    user: User = Depends(get_current_active_user),
    service: AuthService = Depends(get_auth_service),
):
    """Change current user password."""
    await service.change_password(
        user_id=user.id,
        current_password=data.current_password,
        new_password=data.new_password,
    )
    return ResponseWrapper(message="Password changed successfully")


# ==================== Token validation (internal) ====================

@router.get(
    "/validate",
    response_model=ResponseWrapper[UserResponse],
    summary="Validate token",
    include_in_schema=False,  # Internal endpoint
)
async def validate_token(
    user: User = Depends(get_current_active_user),
):
    """Validate access token and return user info (for internal service calls)."""
    return ResponseWrapper(data=UserResponse.model_validate(user))


# ==================== Admin endpoints ====================

admin_router = APIRouter(
    prefix="/api/v1/admin/users",
    tags=["Admin - Users"],
)


@admin_router.get(
    "",
    response_model=ResponseWrapper[PaginatedResponse[UserResponse]],
    summary="List all users",
)
async def list_users(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    role: UserRole | None = None,
    is_active: bool | None = None,
    admin: User = Depends(get_admin_user),
    service: AuthService = Depends(get_auth_service),
):
    """List all users (admin only)."""
    pagination = PaginationParams(page=page, size=size)
    users, total = await service.get_all_users(
        offset=pagination.offset,
        limit=pagination.size,
        role=role,
        is_active=is_active,
    )
    
    return ResponseWrapper(
        data=PaginatedResponse.create(
            items=[UserResponse.model_validate(u) for u in users],
            total=total,
            page=page,
            size=size,
        ),
    )


@admin_router.get(
    "/{user_id}",
    response_model=ResponseWrapper[UserResponse],
    summary="Get user by ID",
)
async def get_user(
    user_id: int,
    admin: User = Depends(get_admin_user),
    service: AuthService = Depends(get_auth_service),
):
    """Get user by ID (admin only)."""
    user = await service.get_user(user_id)
    return ResponseWrapper(data=UserResponse.model_validate(user))


@admin_router.patch(
    "/{user_id}/role",
    response_model=ResponseWrapper[UserResponse],
    summary="Update user role",
)
async def update_user_role(
    user_id: int,
    data: UserRoleUpdate,
    admin: User = Depends(get_admin_user),
    service: AuthService = Depends(get_auth_service),
):
    """Update user role (admin only)."""
    user = await service.update_user_role(user_id, data.role)
    return ResponseWrapper(
        message="User role updated",
        data=UserResponse.model_validate(user),
    )


@admin_router.patch(
    "/{user_id}/status",
    response_model=ResponseWrapper[UserResponse],
    summary="Update user status",
)
async def update_user_status(
    user_id: int,
    data: UserStatusUpdate,
    admin: User = Depends(get_admin_user),
    service: AuthService = Depends(get_auth_service),
):
    """Activate/deactivate user (admin only)."""
    user = await service.update_user_status(user_id, data.is_active)
    return ResponseWrapper(
        message="User status updated",
        data=UserResponse.model_validate(user),
    )
