"""
Order service business logic.
"""
import json
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from .clients import CatalogClient
from .models import DeliveryType, Order, PaymentStatus
from .repository import OrderRepository
from .schemas import OrderCreate, OrderItemCreate, OrderStatistics, OrderStatusUpdate, OrderUpdate

import sys
sys.path.insert(0, "/app")
from shared.exceptions import NotFoundException, PermissionDeniedException, ValidationException
from shared.redis_client import RedisClient
from shared.schemas import OrderStatus


class OrderService:
    """Order management service."""
    
    # Valid status transitions
    STATUS_TRANSITIONS = {
        OrderStatus.PENDING: [OrderStatus.CONFIRMED, OrderStatus.CANCELLED],
        OrderStatus.CONFIRMED: [OrderStatus.PREPARING, OrderStatus.CANCELLED],
        OrderStatus.PREPARING: [OrderStatus.READY, OrderStatus.CANCELLED],
        OrderStatus.READY: [OrderStatus.DELIVERING, OrderStatus.CANCELLED],
        OrderStatus.DELIVERING: [OrderStatus.DELIVERED, OrderStatus.CANCELLED],
        OrderStatus.DELIVERED: [],
        OrderStatus.CANCELLED: [],
    }
    
    def __init__(
        self,
        repository: OrderRepository,
        catalog_client: CatalogClient,
        redis: RedisClient,
        min_order_amount: float = 10.0,
        delivery_fee: float = 5.0,
        free_delivery_threshold: float = 50.0,
    ):
        self.repository = repository
        self.catalog_client = catalog_client
        self.redis = redis
        self.min_order_amount = Decimal(str(min_order_amount))
        self.delivery_fee = Decimal(str(delivery_fee))
        self.free_delivery_threshold = Decimal(str(free_delivery_threshold))
    
    async def create_order(
        self,
        user_id: int,
        data: OrderCreate,
    ) -> Order:
        """Create new order."""
        # Validate delivery address for delivery orders
        if data.delivery_type == DeliveryType.DELIVERY and not data.delivery_address:
            raise ValidationException("Delivery address is required for delivery orders")
        
        # Get product information from catalog
        product_ids = [item.product_id for item in data.items]
        products = await self.catalog_client.get_products_by_ids(product_ids)
        
        if not products:
            raise ValidationException("Could not fetch product information")
        
        # Create product lookup
        product_map = {p["id"]: p for p in products}
        
        # Validate all products exist and are available
        for item in data.items:
            product = product_map.get(item.product_id)
            if not product:
                raise NotFoundException(f"Product {item.product_id}")
            if product.get("status") != "available":
                raise ValidationException(f"Product '{product['name']}' is not available")
        
        # Calculate order items and totals
        items_data = []
        subtotal = Decimal("0")
        
        for item in data.items:
            product = product_map[item.product_id]
            product_price = Decimal(str(product["price"]))
            
            # Calculate modifiers total
            modifiers_total = Decimal("0")
            modifiers_json = None
            
            if item.modifiers:
                modifiers_list = []
                for mod in item.modifiers:
                    modifiers_total += mod.price * mod.quantity
                    modifiers_list.append({
                        "id": mod.modifier_id,
                        "name": mod.name,
                        "price": str(mod.price),
                        "quantity": mod.quantity,
                    })
                modifiers_json = json.dumps(modifiers_list)
            
            # Calculate item subtotal
            item_subtotal = (product_price + modifiers_total) * item.quantity
            subtotal += item_subtotal
            
            items_data.append({
                "product_id": item.product_id,
                "product_name": product["name"],
                "product_price": product_price,
                "quantity": item.quantity,
                "modifiers_json": modifiers_json,
                "modifiers_total": modifiers_total,
                "subtotal": item_subtotal,
                "note": item.note,
            })
        
        # Validate minimum order amount
        if subtotal < self.min_order_amount:
            raise ValidationException(
                f"Minimum order amount is {self.min_order_amount}"
            )
        
        # Calculate delivery fee
        delivery_fee = Decimal("0")
        if data.delivery_type == DeliveryType.DELIVERY:
            if subtotal < self.free_delivery_threshold:
                delivery_fee = self.delivery_fee
        
        # Calculate total
        discount = Decimal("0")  # TODO: Implement promo codes
        total = subtotal + delivery_fee - discount
        
        # Estimate delivery time
        estimated_delivery = datetime.now(timezone.utc) + timedelta(minutes=45)
        
        # Create order
        order = await self.repository.create(
            user_id=user_id,
            items_data=items_data,
            delivery_type=data.delivery_type,
            delivery_address=data.delivery_address,
            delivery_lat=data.delivery_lat,
            delivery_lng=data.delivery_lng,
            contact_name=data.contact_name,
            contact_phone=data.contact_phone,
            contact_email=data.contact_email,
            payment_method=data.payment_method,
            customer_note=data.customer_note,
            subtotal=subtotal,
            delivery_fee=delivery_fee,
            discount=discount,
            total=total,
            estimated_delivery=estimated_delivery,
        )
        
        return order
    
    async def get_order(
        self,
        order_id: int,
        user_id: int | None = None,
    ) -> Order:
        """Get order by ID."""
        order = await self.repository.get_by_id(order_id)
        if not order:
            raise NotFoundException("Order")
        
        # Check ownership if user_id provided
        if user_id is not None and order.user_id != user_id:
            raise PermissionDeniedException("You don't have access to this order")
        
        return order
    
    async def get_order_by_number(
        self,
        order_number: str,
        user_id: int | None = None,
    ) -> Order:
        """Get order by order number."""
        order = await self.repository.get_by_order_number(order_number)
        if not order:
            raise NotFoundException("Order")
        
        if user_id is not None and order.user_id != user_id:
            raise PermissionDeniedException("You don't have access to this order")
        
        return order
    
    async def get_user_orders(
        self,
        user_id: int,
        offset: int = 0,
        limit: int = 20,
        status: OrderStatus | None = None,
    ) -> tuple[list[Order], int]:
        """Get user's orders."""
        return await self.repository.get_user_orders(
            user_id=user_id,
            offset=offset,
            limit=limit,
            status=status,
        )
    
    async def get_all_orders(
        self,
        offset: int = 0,
        limit: int = 20,
        status: OrderStatus | None = None,
        user_id: int | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
    ) -> tuple[list[Order], int]:
        """Get all orders (admin)."""
        return await self.repository.get_all_orders(
            offset=offset,
            limit=limit,
            status=status,
            user_id=user_id,
            date_from=date_from,
            date_to=date_to,
        )
    
    async def update_order(
        self,
        order_id: int,
        data: OrderUpdate,
        user_id: int,
    ) -> Order:
        """Update order (limited fields, only pending orders)."""
        order = await self.get_order(order_id, user_id)
        
        if order.status != OrderStatus.PENDING:
            raise ValidationException("Can only update pending orders")
        
        update_data = data.model_dump(exclude_unset=True)
        if update_data:
            order = await self.repository.update(order_id, **update_data)
        
        return order
    
    async def update_order_status(
        self,
        order_id: int,
        data: OrderStatusUpdate,
        changed_by: int,
        is_admin: bool = False,
    ) -> Order:
        """Update order status."""
        order = await self.repository.get_by_id(order_id)
        if not order:
            raise NotFoundException("Order")
        
        # Check if user can update this order
        if not is_admin and order.user_id != changed_by:
            raise PermissionDeniedException("You don't have access to this order")
        
        # Customers can only cancel their own pending orders
        if not is_admin:
            if data.status != OrderStatus.CANCELLED:
                raise PermissionDeniedException("Customers can only cancel orders")
            if order.status != OrderStatus.PENDING:
                raise ValidationException("Can only cancel pending orders")
        
        # Validate status transition
        allowed_transitions = self.STATUS_TRANSITIONS.get(order.status, [])
        if data.status not in allowed_transitions:
            raise ValidationException(
                f"Cannot transition from {order.status.value} to {data.status.value}"
            )
        
        order = await self.repository.update_status(
            order_id=order_id,
            status=data.status,
            changed_by=changed_by,
            note=data.note,
        )
        
        return order
    
    async def update_payment_status(
        self,
        order_id: int,
        payment_status: PaymentStatus,
    ) -> Order:
        """Update order payment status (admin/payment webhook)."""
        order = await self.repository.get_by_id(order_id)
        if not order:
            raise NotFoundException("Order")
        
        order = await self.repository.update_payment_status(order_id, payment_status)
        
        return order
    
    async def cancel_order(
        self,
        order_id: int,
        user_id: int,
        reason: str | None = None,
        is_admin: bool = False,
    ) -> Order:
        """Cancel order."""
        return await self.update_order_status(
            order_id=order_id,
            data=OrderStatusUpdate(
                status=OrderStatus.CANCELLED,
                note=reason,
            ),
            changed_by=user_id,
            is_admin=is_admin,
        )
    
    async def get_statistics(
        self,
        user_id: int | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
    ) -> OrderStatistics:
        """Get order statistics."""
        stats = await self.repository.get_statistics(
            user_id=user_id,
            date_from=date_from,
            date_to=date_to,
        )
        return OrderStatistics(**stats)
