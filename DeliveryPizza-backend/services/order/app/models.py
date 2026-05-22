"""
Order SQLAlchemy models.
"""
from datetime import datetime
from decimal import Decimal
from enum import Enum as PyEnum

from sqlalchemy import (
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

import sys
sys.path.insert(0, "/app")
from shared.database import Base
from shared.schemas import OrderStatus


class PaymentStatus(str, PyEnum):
    """Payment status enumeration."""
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"


class PaymentMethod(str, PyEnum):
    """Payment method enumeration."""
    CASH = "cash"
    CARD = "card"
    ONLINE = "online"


class DeliveryType(str, PyEnum):
    """Delivery type enumeration."""
    DELIVERY = "delivery"
    PICKUP = "pickup"


class Order(Base):
    """Order model."""
    
    __tablename__ = "orders"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    order_number: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
    )
    user_id: Mapped[int] = mapped_column(nullable=False, index=True)
    
    # Order status
    status: Mapped[OrderStatus] = mapped_column(
        Enum(OrderStatus),
        default=OrderStatus.PENDING,
        nullable=False,
    )
    
    # Delivery info
    delivery_type: Mapped[DeliveryType] = mapped_column(
        Enum(DeliveryType),
        default=DeliveryType.DELIVERY,
        nullable=False,
    )
    delivery_address: Mapped[str | None] = mapped_column(Text, nullable=True)
    delivery_lat: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 8),
        nullable=True,
    )
    delivery_lng: Mapped[Decimal | None] = mapped_column(
        Numeric(11, 8),
        nullable=True,
    )
    
    # Contact info
    contact_name: Mapped[str] = mapped_column(String(200), nullable=False)
    contact_phone: Mapped[str] = mapped_column(String(20), nullable=False)
    contact_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    
    # Pricing
    subtotal: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )
    delivery_fee: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        default=Decimal("0"),
        nullable=False,
    )
    discount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        default=Decimal("0"),
        nullable=False,
    )
    total: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )
    
    # Payment
    payment_method: Mapped[PaymentMethod] = mapped_column(
        Enum(PaymentMethod),
        default=PaymentMethod.CASH,
        nullable=False,
    )
    payment_status: Mapped[PaymentStatus] = mapped_column(
        Enum(PaymentStatus),
        default=PaymentStatus.PENDING,
        nullable=False,
    )
    
    # Notes
    customer_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    internal_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # Timing
    estimated_delivery: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    delivered_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        onupdate=func.now(),
        nullable=True,
    )
    
    # Relationships
    items: Mapped[list["OrderItem"]] = relationship(
        "OrderItem",
        back_populates="order",
        cascade="all, delete-orphan",
    )
    status_history: Mapped[list["OrderStatusHistory"]] = relationship(
        "OrderStatusHistory",
        back_populates="order",
        cascade="all, delete-orphan",
    )
    
    __table_args__ = (
        Index("idx_orders_user_status", "user_id", "status"),
        Index("idx_orders_status_created", "status", "created_at"),
        Index("idx_orders_created", "created_at"),
    )


class OrderItem(Base):
    """Order item model."""
    
    __tablename__ = "order_items"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False,
    )
    product_id: Mapped[int] = mapped_column(nullable=False)
    product_name: Mapped[str] = mapped_column(String(200), nullable=False)
    product_price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )
    quantity: Mapped[int] = mapped_column(default=1, nullable=False)
    modifiers_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    modifiers_total: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        default=Decimal("0"),
        nullable=False,
    )
    subtotal: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # Relationships
    order: Mapped[Order] = relationship("Order", back_populates="items")
    
    __table_args__ = (
        Index("idx_order_items_order", "order_id"),
    )


class OrderStatusHistory(Base):
    """Order status history model."""
    
    __tablename__ = "order_status_history"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False,
    )
    status: Mapped[OrderStatus] = mapped_column(
        Enum(OrderStatus),
        nullable=False,
    )
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    changed_by: Mapped[int | None] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    
    # Relationships
    order: Mapped[Order] = relationship("Order", back_populates="status_history")
    
    __table_args__ = (
        Index("idx_status_history_order", "order_id"),
    )
