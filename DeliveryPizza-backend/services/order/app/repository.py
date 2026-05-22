"""
Order repository for database operations.
"""
import json
import random
import string
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from .models import Order, OrderItem, OrderStatusHistory, PaymentStatus

import sys
sys.path.insert(0, "/app")
from shared.schemas import OrderStatus


def generate_order_number(prefix: str = "ORD") -> str:
    """Generate unique order number."""
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    random_part = "".join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"{prefix}-{timestamp}-{random_part}"


class OrderRepository:
    """Order database repository."""
    
    def __init__(self, session: AsyncSession, order_number_prefix: str = "ORD"):
        self.session = session
        self.order_number_prefix = order_number_prefix
    
    async def create(
        self,
        user_id: int,
        items_data: list[dict],
        **kwargs,
    ) -> Order:
        """Create new order with items."""
        # Generate order number
        order_number = generate_order_number(self.order_number_prefix)
        
        # Create order
        order = Order(
            order_number=order_number,
            user_id=user_id,
            **kwargs,
        )
        self.session.add(order)
        await self.session.flush()
        
        # Create items
        for item_data in items_data:
            item = OrderItem(order_id=order.id, **item_data)
            self.session.add(item)
        
        # Create initial status history
        history = OrderStatusHistory(
            order_id=order.id,
            status=OrderStatus.PENDING,
            changed_by=user_id,
        )
        self.session.add(history)
        
        await self.session.flush()
        await self.session.refresh(order)
        
        # Load relationships
        result = await self.session.execute(
            select(Order)
            .options(selectinload(Order.items))
            .where(Order.id == order.id)
        )
        return result.scalar_one()
    
    async def get_by_id(self, order_id: int) -> Order | None:
        """Get order by ID with items."""
        result = await self.session.execute(
            select(Order)
            .options(
                selectinload(Order.items),
                selectinload(Order.status_history),
            )
            .where(Order.id == order_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_order_number(self, order_number: str) -> Order | None:
        """Get order by order number."""
        result = await self.session.execute(
            select(Order)
            .options(selectinload(Order.items))
            .where(Order.order_number == order_number)
        )
        return result.scalar_one_or_none()
    
    async def get_user_orders(
        self,
        user_id: int,
        offset: int = 0,
        limit: int = 20,
        status: OrderStatus | None = None,
    ) -> tuple[list[Order], int]:
        """Get user's orders with pagination."""
        query = select(Order).where(Order.user_id == user_id)
        
        if status is not None:
            query = query.where(Order.status == status)
        
        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.session.execute(count_query)
        total = total_result.scalar() or 0
        
        # Get paginated
        query = (
            query
            .options(selectinload(Order.items))
            .offset(offset)
            .limit(limit)
            .order_by(Order.created_at.desc())
        )
        result = await self.session.execute(query)
        orders = list(result.scalars().all())
        
        return orders, total
    
    async def get_all_orders(
        self,
        offset: int = 0,
        limit: int = 20,
        status: OrderStatus | None = None,
        user_id: int | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
    ) -> tuple[list[Order], int]:
        """Get all orders with filters (admin)."""
        query = select(Order)
        
        if status is not None:
            query = query.where(Order.status == status)
        if user_id is not None:
            query = query.where(Order.user_id == user_id)
        if date_from is not None:
            query = query.where(Order.created_at >= date_from)
        if date_to is not None:
            query = query.where(Order.created_at <= date_to)
        
        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.session.execute(count_query)
        total = total_result.scalar() or 0
        
        # Get paginated
        query = (
            query
            .options(selectinload(Order.items))
            .offset(offset)
            .limit(limit)
            .order_by(Order.created_at.desc())
        )
        result = await self.session.execute(query)
        orders = list(result.scalars().all())
        
        return orders, total
    
    async def update(self, order_id: int, **kwargs) -> Order | None:
        """Update order fields."""
        await self.session.execute(
            update(Order)
            .where(Order.id == order_id)
            .values(**kwargs)
        )
        return await self.get_by_id(order_id)
    
    async def update_status(
        self,
        order_id: int,
        status: OrderStatus,
        changed_by: int | None = None,
        note: str | None = None,
    ) -> Order | None:
        """Update order status and add history entry."""
        # Update order status
        update_data = {"status": status}
        
        if status == OrderStatus.DELIVERED:
            update_data["delivered_at"] = datetime.now(timezone.utc)
        
        await self.session.execute(
            update(Order)
            .where(Order.id == order_id)
            .values(**update_data)
        )
        
        # Add history entry
        history = OrderStatusHistory(
            order_id=order_id,
            status=status,
            changed_by=changed_by,
            note=note,
        )
        self.session.add(history)
        await self.session.flush()
        
        return await self.get_by_id(order_id)
    
    async def update_payment_status(
        self,
        order_id: int,
        payment_status: PaymentStatus,
    ) -> Order | None:
        """Update order payment status."""
        await self.session.execute(
            update(Order)
            .where(Order.id == order_id)
            .values(payment_status=payment_status)
        )
        return await self.get_by_id(order_id)
    
    async def get_statistics(
        self,
        user_id: int | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
    ) -> dict:
        """Get order statistics."""
        base_query = select(Order)
        
        if user_id is not None:
            base_query = base_query.where(Order.user_id == user_id)
        if date_from is not None:
            base_query = base_query.where(Order.created_at >= date_from)
        if date_to is not None:
            base_query = base_query.where(Order.created_at <= date_to)
        
        # Total orders
        total_query = select(func.count()).select_from(base_query.subquery())
        total_result = await self.session.execute(total_query)
        total_orders = total_result.scalar() or 0
        
        # Pending orders
        pending_query = select(func.count()).select_from(
            base_query.where(Order.status == OrderStatus.PENDING).subquery()
        )
        pending_result = await self.session.execute(pending_query)
        pending_orders = pending_result.scalar() or 0
        
        # Completed orders
        completed_query = select(func.count()).select_from(
            base_query.where(Order.status == OrderStatus.DELIVERED).subquery()
        )
        completed_result = await self.session.execute(completed_query)
        completed_orders = completed_result.scalar() or 0
        
        # Cancelled orders
        cancelled_query = select(func.count()).select_from(
            base_query.where(Order.status == OrderStatus.CANCELLED).subquery()
        )
        cancelled_result = await self.session.execute(cancelled_query)
        cancelled_orders = cancelled_result.scalar() or 0
        
        # Total revenue (from delivered orders)
        revenue_query = select(func.sum(Order.total)).select_from(
            base_query.where(Order.status == OrderStatus.DELIVERED).subquery()
        )
        revenue_result = await self.session.execute(revenue_query)
        total_revenue = revenue_result.scalar() or Decimal("0")
        
        # Average order value
        avg_value = total_revenue / completed_orders if completed_orders > 0 else Decimal("0")
        
        return {
            "total_orders": total_orders,
            "pending_orders": pending_orders,
            "completed_orders": completed_orders,
            "cancelled_orders": cancelled_orders,
            "total_revenue": total_revenue,
            "average_order_value": avg_value,
        }
