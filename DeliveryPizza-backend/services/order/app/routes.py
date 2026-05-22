"""
Order API routes.
"""
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from .dependencies import (
    CurrentUser,
    get_admin_user,
    get_courier_user,
    get_current_active_user,
    get_manager_user,
    get_order_service,
)
from .models import PaymentStatus
from .schemas import (
    OrderCreate,
    OrderListResponse,
    OrderResponse,
    OrderStatistics,
    OrderStatusHistoryResponse,
    OrderStatusUpdate,
    OrderUpdate,
)
from .service import OrderService

import sys
sys.path.insert(0, "/app")
from shared.schemas import (
    OrderStatus,
    PaginatedResponse,
    PaginationParams,
    ResponseWrapper,
)


router = APIRouter(prefix="/api/v1/orders", tags=["Orders"])


# ==================== Customer endpoints ====================

@router.post(
    "",
    response_model=ResponseWrapper[OrderResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create order",
)
async def create_order(
    data: OrderCreate,
    user: CurrentUser = Depends(get_current_active_user),
    service: OrderService = Depends(get_order_service),
):
    """Create new order."""
    order = await service.create_order(user.id, data)
    return ResponseWrapper(
        message="Order created successfully",
        data=OrderResponse.model_validate(order),
    )


@router.get(
    "/my",
    response_model=ResponseWrapper[PaginatedResponse[OrderListResponse]],
    summary="Get my orders",
)
async def get_my_orders(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    status: OrderStatus | None = None,
    user: CurrentUser = Depends(get_current_active_user),
    service: OrderService = Depends(get_order_service),
):
    """Get current user's orders."""
    pagination = PaginationParams(page=page, size=size)
    orders, total = await service.get_user_orders(
        user_id=user.id,
        offset=pagination.offset,
        limit=pagination.size,
        status=status,
    )
    
    # Convert to list response
    items = []
    for order in orders:
        items.append(OrderListResponse(
            id=order.id,
            order_number=order.order_number,
            status=order.status,
            delivery_type=order.delivery_type,
            total=order.total,
            payment_status=order.payment_status,
            items_count=len(order.items),
            created_at=order.created_at,
        ))
    
    return ResponseWrapper(
        data=PaginatedResponse.create(
            items=items,
            total=total,
            page=page,
            size=size,
        ),
    )


@router.get(
    "/{order_id}",
    response_model=ResponseWrapper[OrderResponse],
    summary="Get order by ID",
)
async def get_order(
    order_id: int,
    user: CurrentUser = Depends(get_current_active_user),
    service: OrderService = Depends(get_order_service),
):
    """Get order by ID."""
    # Check if user is admin/manager - they can see all orders
    user_id = None if user.role in [UserRole.ADMIN, UserRole.MANAGER] else user.id
    order = await service.get_order(order_id, user_id)
    return ResponseWrapper(data=OrderResponse.model_validate(order))


@router.get(
    "/number/{order_number}",
    response_model=ResponseWrapper[OrderResponse],
    summary="Get order by number",
)
async def get_order_by_number(
    order_number: str,
    user: CurrentUser = Depends(get_current_active_user),
    service: OrderService = Depends(get_order_service),
):
    """Get order by order number."""
    user_id = None if user.role in [UserRole.ADMIN, UserRole.MANAGER] else user.id
    order = await service.get_order_by_number(order_number, user_id)
    return ResponseWrapper(data=OrderResponse.model_validate(order))


@router.patch(
    "/{order_id}",
    response_model=ResponseWrapper[OrderResponse],
    summary="Update order",
)
async def update_order(
    order_id: int,
    data: OrderUpdate,
    user: CurrentUser = Depends(get_current_active_user),
    service: OrderService = Depends(get_order_service),
):
    """Update order (only pending orders)."""
    order = await service.update_order(order_id, data, user.id)
    return ResponseWrapper(
        message="Order updated",
        data=OrderResponse.model_validate(order),
    )


@router.post(
    "/{order_id}/cancel",
    response_model=ResponseWrapper[OrderResponse],
    summary="Cancel order",
)
async def cancel_order(
    order_id: int,
    reason: str | None = None,
    user: CurrentUser = Depends(get_current_active_user),
    service: OrderService = Depends(get_order_service),
):
    """Cancel order (only pending orders for customers)."""
    is_admin = user.role in [UserRole.ADMIN, UserRole.MANAGER]
    order = await service.cancel_order(order_id, user.id, reason, is_admin)
    return ResponseWrapper(
        message="Order cancelled",
        data=OrderResponse.model_validate(order),
    )


@router.get(
    "/{order_id}/history",
    response_model=ResponseWrapper[list[OrderStatusHistoryResponse]],
    summary="Get order status history",
)
async def get_order_history(
    order_id: int,
    user: CurrentUser = Depends(get_current_active_user),
    service: OrderService = Depends(get_order_service),
):
    """Get order status history."""
    user_id = None if user.role in [UserRole.ADMIN, UserRole.MANAGER] else user.id
    order = await service.get_order(order_id, user_id)
    
    history = [
        OrderStatusHistoryResponse.model_validate(h)
        for h in order.status_history
    ]
    return ResponseWrapper(data=history)


# ==================== Admin/Manager endpoints ====================

admin_router = APIRouter(prefix="/api/v1/admin/orders", tags=["Admin - Orders"])


@admin_router.get(
    "",
    response_model=ResponseWrapper[PaginatedResponse[OrderListResponse]],
    summary="Get all orders",
)
async def get_all_orders(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    status: OrderStatus | None = None,
    user_id: int | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    admin: CurrentUser = Depends(get_manager_user),
    service: OrderService = Depends(get_order_service),
):
    """Get all orders with filtering (admin/manager)."""
    pagination = PaginationParams(page=page, size=size)
    orders, total = await service.get_all_orders(
        offset=pagination.offset,
        limit=pagination.size,
        status=status,
        user_id=user_id,
        date_from=date_from,
        date_to=date_to,
    )
    
    items = []
    for order in orders:
        items.append(OrderListResponse(
            id=order.id,
            order_number=order.order_number,
            status=order.status,
            delivery_type=order.delivery_type,
            total=order.total,
            payment_status=order.payment_status,
            items_count=len(order.items),
            created_at=order.created_at,
        ))
    
    return ResponseWrapper(
        data=PaginatedResponse.create(
            items=items,
            total=total,
            page=page,
            size=size,
        ),
    )


@admin_router.patch(
    "/{order_id}/status",
    response_model=ResponseWrapper[OrderResponse],
    summary="Update order status",
)
async def update_order_status(
    order_id: int,
    data: OrderStatusUpdate,
    admin: CurrentUser = Depends(get_courier_user),
    service: OrderService = Depends(get_order_service),
):
    """Update order status (admin/manager/courier)."""
    order = await service.update_order_status(
        order_id=order_id,
        data=data,
        changed_by=admin.id,
        is_admin=True,
    )
    return ResponseWrapper(
        message="Order status updated",
        data=OrderResponse.model_validate(order),
    )


@admin_router.patch(
    "/{order_id}/payment",
    response_model=ResponseWrapper[OrderResponse],
    summary="Update payment status",
)
async def update_payment_status(
    order_id: int,
    payment_status: PaymentStatus,
    admin: CurrentUser = Depends(get_manager_user),
    service: OrderService = Depends(get_order_service),
):
    """Update order payment status (admin/manager)."""
    order = await service.update_payment_status(order_id, payment_status)
    return ResponseWrapper(
        message="Payment status updated",
        data=OrderResponse.model_validate(order),
    )


@admin_router.get(
    "/statistics",
    response_model=ResponseWrapper[OrderStatistics],
    summary="Get order statistics",
)
async def get_statistics(
    user_id: int | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    admin: CurrentUser = Depends(get_manager_user),
    service: OrderService = Depends(get_order_service),
):
    """Get order statistics (admin/manager)."""
    stats = await service.get_statistics(
        user_id=user_id,
        date_from=date_from,
        date_to=date_to,
    )
    return ResponseWrapper(data=stats)


# Import UserRole for route checks
from shared.schemas import UserRole
