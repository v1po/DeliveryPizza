"""
Order service Pydantic schemas.
"""
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, EmailStr, Field

from .models import DeliveryType, PaymentMethod, PaymentStatus

import sys
sys.path.insert(0, "/app")
from shared.schemas import BaseSchema, OrderStatus, TimestampMixin


# ==================== Order Item Schemas ====================

class OrderItemModifier(BaseModel):
    """Order item modifier schema."""
    modifier_id: int
    name: str
    price: Decimal
    quantity: int = 1


class OrderItemCreate(BaseModel):
    """Order item creation schema."""
    product_id: int
    quantity: int = Field(ge=1, default=1)
    modifiers: list[OrderItemModifier] = []
    note: str | None = None


class OrderItemResponse(BaseSchema):
    """Order item response schema."""
    id: int
    product_id: int
    product_name: str
    product_price: Decimal
    quantity: int
    modifiers_json: str | None
    modifiers_total: Decimal
    subtotal: Decimal
    note: str | None


# ==================== Order Schemas ====================

class OrderCreate(BaseModel):
    """Order creation schema."""
    items: list[OrderItemCreate] = Field(min_length=1)
    delivery_type: DeliveryType = DeliveryType.DELIVERY
    delivery_address: str | None = Field(default=None, max_length=500)
    delivery_lat: Decimal | None = None
    delivery_lng: Decimal | None = None
    contact_name: str = Field(min_length=1, max_length=200)
    contact_phone: str = Field(min_length=1, max_length=20)
    contact_email: EmailStr | None = None
    payment_method: PaymentMethod = PaymentMethod.CASH
    customer_note: str | None = None
    promo_code: str | None = None


class OrderUpdate(BaseModel):
    """Order update schema (limited fields)."""
    delivery_address: str | None = None
    contact_name: str | None = None
    contact_phone: str | None = None
    customer_note: str | None = None


class OrderStatusUpdate(BaseModel):
    """Order status update schema."""
    status: OrderStatus
    note: str | None = None


class OrderResponse(BaseSchema, TimestampMixin):
    """Order response schema."""
    id: int
    order_number: str
    user_id: int
    status: OrderStatus
    delivery_type: DeliveryType
    delivery_address: str | None
    delivery_lat: Decimal | None
    delivery_lng: Decimal | None
    contact_name: str
    contact_phone: str
    contact_email: str | None
    subtotal: Decimal
    delivery_fee: Decimal
    discount: Decimal
    total: Decimal
    payment_method: PaymentMethod
    payment_status: PaymentStatus
    customer_note: str | None
    estimated_delivery: datetime | None
    delivered_at: datetime | None
    items: list[OrderItemResponse] = []


class OrderListResponse(BaseSchema):
    """Order list item response (lighter)."""
    id: int
    order_number: str
    status: OrderStatus
    delivery_type: DeliveryType
    total: Decimal
    payment_status: PaymentStatus
    items_count: int
    created_at: datetime


class OrderStatusHistoryResponse(BaseSchema):
    """Order status history response."""
    id: int
    status: OrderStatus
    note: str | None
    changed_by: int | None
    created_at: datetime


# ==================== Statistics ====================

class OrderStatistics(BaseModel):
    """Order statistics schema."""
    total_orders: int
    pending_orders: int
    completed_orders: int
    cancelled_orders: int
    total_revenue: Decimal
    average_order_value: Decimal
