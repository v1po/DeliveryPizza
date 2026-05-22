"""
Catalog service Pydantic schemas.
"""
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field, field_validator

from .models import ProductStatus

import sys
sys.path.insert(0, "/app")
from shared.schemas import BaseSchema, TimestampMixin


# ==================== Category Schemas ====================

class CategoryBase(BaseModel):
    """Base category schema."""
    name: str = Field(min_length=1, max_length=100)
    description: str | None = None
    image_url: str | None = Field(default=None, max_length=500)
    parent_id: int | None = None
    sort_order: int = 0


class CategoryCreate(CategoryBase):
    """Category creation schema."""
    slug: str | None = Field(default=None, max_length=100)


class CategoryUpdate(BaseModel):
    """Category update schema."""
    name: str | None = Field(default=None, min_length=1, max_length=100)
    slug: str | None = Field(default=None, max_length=100)
    description: str | None = None
    image_url: str | None = Field(default=None, max_length=500)
    parent_id: int | None = None
    sort_order: int | None = None
    is_active: bool | None = None


class CategoryResponse(BaseSchema, TimestampMixin):
    """Category response schema."""
    id: int
    name: str
    slug: str
    description: str | None
    image_url: str | None
    parent_id: int | None
    sort_order: int
    is_active: bool


class CategoryWithChildren(CategoryResponse):
    """Category with children response."""
    children: list["CategoryWithChildren"] = []
    products_count: int = 0


# ==================== Product Modifier Schemas ====================

class ModifierBase(BaseModel):
    """Base modifier schema."""
    name: str = Field(min_length=1, max_length=100)
    price: Decimal = Field(ge=0, default=Decimal("0"))
    is_required: bool = False
    max_quantity: int = Field(ge=1, default=1)
    sort_order: int = 0


class ModifierCreate(ModifierBase):
    """Modifier creation schema."""
    pass


class ModifierUpdate(BaseModel):
    """Modifier update schema."""
    name: str | None = Field(default=None, min_length=1, max_length=100)
    price: Decimal | None = Field(default=None, ge=0)
    is_required: bool | None = None
    max_quantity: int | None = Field(default=None, ge=1)
    sort_order: int | None = None


class ModifierResponse(BaseSchema):
    """Modifier response schema."""
    id: int
    name: str
    price: Decimal
    is_required: bool
    max_quantity: int
    sort_order: int


# ==================== Product Schemas ====================

class ProductBase(BaseModel):
    """Base product schema."""
    name: str = Field(min_length=1, max_length=200)
    description: str | None = None
    short_description: str | None = Field(default=None, max_length=500)
    price: Decimal = Field(gt=0)
    old_price: Decimal | None = Field(default=None, gt=0)
    category_id: int
    image_url: str | None = Field(default=None, max_length=500)
    status: ProductStatus = ProductStatus.AVAILABLE
    is_featured: bool = False
    calories: int | None = Field(default=None, ge=0)
    weight: str | None = Field(default=None, max_length=50)
    preparation_time: int | None = Field(default=None, ge=0)
    ingredients: str | None = None
    allergens: str | None = Field(default=None, max_length=500)
    sort_order: int = 0
    
    @field_validator("old_price")
    @classmethod
    def validate_old_price(cls, v, info):
        if v is not None and "price" in info.data and v <= info.data["price"]:
            raise ValueError("Old price must be greater than current price")
        return v


class ProductCreate(ProductBase):
    """Product creation schema."""
    slug: str | None = Field(default=None, max_length=200)
    modifiers: list[ModifierCreate] = []


class ProductUpdate(BaseModel):
    """Product update schema."""
    name: str | None = Field(default=None, min_length=1, max_length=200)
    slug: str | None = Field(default=None, max_length=200)
    description: str | None = None
    short_description: str | None = Field(default=None, max_length=500)
    price: Decimal | None = Field(default=None, gt=0)
    old_price: Decimal | None = Field(default=None, gt=0)
    category_id: int | None = None
    image_url: str | None = Field(default=None, max_length=500)
    status: ProductStatus | None = None
    is_featured: bool | None = None
    calories: int | None = Field(default=None, ge=0)
    weight: str | None = Field(default=None, max_length=50)
    preparation_time: int | None = Field(default=None, ge=0)
    ingredients: str | None = None
    allergens: str | None = Field(default=None, max_length=500)
    sort_order: int | None = None


class ProductResponse(BaseSchema, TimestampMixin):
    """Product response schema."""
    id: int
    name: str
    slug: str
    description: str | None
    short_description: str | None
    price: Decimal
    old_price: Decimal | None
    category_id: int
    image_url: str | None
    status: ProductStatus
    is_featured: bool
    calories: int | None
    weight: str | None
    preparation_time: int | None
    ingredients: str | None
    allergens: str | None
    sort_order: int
    modifiers: list[ModifierResponse] = []


class ProductListResponse(BaseSchema):
    """Product list item response (lighter version)."""
    id: int
    name: str
    slug: str
    short_description: str | None
    price: Decimal
    old_price: Decimal | None
    category_id: int
    image_url: str | None
    status: ProductStatus
    is_featured: bool
    preparation_time: int | None


# ==================== Menu Schemas ====================

class MenuCategory(BaseModel):
    """Menu category with products."""
    id: int
    name: str
    slug: str
    description: str | None
    image_url: str | None
    products: list[ProductListResponse]


class MenuResponse(BaseModel):
    """Full menu response."""
    categories: list[MenuCategory]
    featured_products: list[ProductListResponse]
