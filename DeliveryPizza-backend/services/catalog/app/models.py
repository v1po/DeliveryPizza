"""
Catalog SQLAlchemy models.
"""
from datetime import datetime
from decimal import Decimal
from enum import Enum as PyEnum

from sqlalchemy import (
    Boolean,
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


class ProductStatus(str, PyEnum):
    """Product availability status."""
    AVAILABLE = "available"
    OUT_OF_STOCK = "out_of_stock"
    DISCONTINUED = "discontinued"


class Category(Base):
    """Product category model."""
    
    __tablename__ = "categories"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    parent_id: Mapped[int | None] = mapped_column(
        ForeignKey("categories.id", ondelete="SET NULL"),
        nullable=True,
    )
    sort_order: Mapped[int] = mapped_column(default=0, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
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
    parent: Mapped["Category | None"] = relationship(
        "Category",
        remote_side=[id],
        back_populates="children",
    )
    children: Mapped[list["Category"]] = relationship(
        "Category",
        back_populates="parent",
    )
    products: Mapped[list["Product"]] = relationship(
        "Product",
        back_populates="category",
    )
    
    __table_args__ = (
        Index("idx_categories_parent", "parent_id"),
        Index("idx_categories_active_sort", "is_active", "sort_order"),
    )


class Product(Base):
    """Product/menu item model."""
    
    __tablename__ = "products"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(200), unique=True, nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    short_description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )
    old_price: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2),
        nullable=True,
    )
    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id", ondelete="CASCADE"),
        nullable=False,
    )
    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    status: Mapped[ProductStatus] = mapped_column(
        Enum(ProductStatus),
        default=ProductStatus.AVAILABLE,
        nullable=False,
    )
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    calories: Mapped[int | None] = mapped_column(nullable=True)
    weight: Mapped[str | None] = mapped_column(String(50), nullable=True)
    preparation_time: Mapped[int | None] = mapped_column(nullable=True)  # minutes
    ingredients: Mapped[str | None] = mapped_column(Text, nullable=True)
    allergens: Mapped[str | None] = mapped_column(String(500), nullable=True)
    sort_order: Mapped[int] = mapped_column(default=0, nullable=False)
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
    category: Mapped[Category] = relationship("Category", back_populates="products")
    modifiers: Mapped[list["ProductModifier"]] = relationship(
        "ProductModifier",
        back_populates="product",
        cascade="all, delete-orphan",
    )
    
    __table_args__ = (
        Index("idx_products_category", "category_id"),
        Index("idx_products_status", "status"),
        Index("idx_products_featured", "is_featured"),
        Index("idx_products_search", "name", "status"),
    )


class ProductModifier(Base):
    """Product modifier/addon model."""
    
    __tablename__ = "product_modifiers"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0, nullable=False)
    is_required: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    max_quantity: Mapped[int] = mapped_column(default=1, nullable=False)
    sort_order: Mapped[int] = mapped_column(default=0, nullable=False)
    
    # Relationships
    product: Mapped[Product] = relationship("Product", back_populates="modifiers")
    
    __table_args__ = (
        Index("idx_modifiers_product", "product_id"),
    )
