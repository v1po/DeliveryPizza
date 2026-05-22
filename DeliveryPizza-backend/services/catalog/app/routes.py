"""
Catalog API routes.
"""
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from .dependencies import get_catalog_service
from .models import ProductStatus
from .schemas import (
    CategoryCreate,
    CategoryResponse,
    CategoryUpdate,
    CategoryWithChildren,
    MenuResponse,
    ModifierCreate,
    ModifierResponse,
    ModifierUpdate,
    ProductCreate,
    ProductListResponse,
    ProductResponse,
    ProductUpdate,
)
from .service import CatalogService

import sys
sys.path.insert(0, "/app")
from shared.schemas import PaginatedResponse, PaginationParams, ResponseWrapper


# ==================== Category Routes ====================

category_router = APIRouter(prefix="/api/v1/categories", tags=["Categories"])


@category_router.get(
    "",
    response_model=ResponseWrapper[list[CategoryWithChildren]],
    summary="Get category tree",
)
async def get_categories(
    active_only: bool = True,
    service: CatalogService = Depends(get_catalog_service),
):
    """Get all categories as tree structure."""
    categories = await service.get_category_tree(active_only=active_only)
    return ResponseWrapper(data=categories)


@category_router.get(
    "/{category_id}",
    response_model=ResponseWrapper[CategoryResponse],
    summary="Get category by ID",
)
async def get_category(
    category_id: int,
    service: CatalogService = Depends(get_catalog_service),
):
    """Get category by ID."""
    category = await service.get_category(category_id)
    return ResponseWrapper(data=CategoryResponse.model_validate(category))


@category_router.get(
    "/slug/{slug}",
    response_model=ResponseWrapper[CategoryResponse],
    summary="Get category by slug",
)
async def get_category_by_slug(
    slug: str,
    service: CatalogService = Depends(get_catalog_service),
):
    """Get category by slug."""
    category = await service.get_category_by_slug(slug)
    return ResponseWrapper(data=CategoryResponse.model_validate(category))


@category_router.post(
    "",
    response_model=ResponseWrapper[CategoryResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create category",
)
async def create_category(
    data: CategoryCreate,
    service: CatalogService = Depends(get_catalog_service),
):
    """Create new category (admin only)."""
    category = await service.create_category(data)
    return ResponseWrapper(
        message="Category created",
        data=CategoryResponse.model_validate(category),
    )


@category_router.patch(
    "/{category_id}",
    response_model=ResponseWrapper[CategoryResponse],
    summary="Update category",
)
async def update_category(
    category_id: int,
    data: CategoryUpdate,
    service: CatalogService = Depends(get_catalog_service),
):
    """Update category (admin only)."""
    category = await service.update_category(category_id, data)
    return ResponseWrapper(
        message="Category updated",
        data=CategoryResponse.model_validate(category),
    )


@category_router.delete(
    "/{category_id}",
    response_model=ResponseWrapper[None],
    summary="Delete category",
)
async def delete_category(
    category_id: int,
    service: CatalogService = Depends(get_catalog_service),
):
    """Delete category (admin only)."""
    await service.delete_category(category_id)
    return ResponseWrapper(message="Category deleted")


# ==================== Product Routes ====================

product_router = APIRouter(prefix="/api/v1/products", tags=["Products"])


@product_router.get(
    "",
    response_model=ResponseWrapper[PaginatedResponse[ProductListResponse]],
    summary="Get products",
)
async def get_products(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    category_id: int | None = None,
    status: ProductStatus | None = None,
    is_featured: bool | None = None,
    search: str | None = Query(default=None, max_length=100),
    service: CatalogService = Depends(get_catalog_service),
):
    """Get products with filtering and pagination."""
    pagination = PaginationParams(page=page, size=size)
    products, total = await service.get_products(
        offset=pagination.offset,
        limit=pagination.size,
        category_id=category_id,
        status=status,
        is_featured=is_featured,
        search=search,
    )
    
    return ResponseWrapper(
        data=PaginatedResponse.create(
            items=[ProductListResponse.model_validate(p) for p in products],
            total=total,
            page=page,
            size=size,
        ),
    )


@product_router.get(
    "/featured",
    response_model=ResponseWrapper[list[ProductListResponse]],
    summary="Get featured products",
)
async def get_featured_products(
    limit: int = Query(default=10, ge=1, le=50),
    service: CatalogService = Depends(get_catalog_service),
):
    """Get featured products."""
    products = await service.get_featured_products(limit)
    return ResponseWrapper(
        data=[ProductListResponse.model_validate(p) for p in products],
    )


@product_router.get(
    "/{product_id}",
    response_model=ResponseWrapper[ProductResponse],
    summary="Get product by ID",
)
async def get_product(
    product_id: int,
    service: CatalogService = Depends(get_catalog_service),
):
    """Get product by ID with modifiers."""
    product = await service.get_product(product_id)
    return ResponseWrapper(data=ProductResponse.model_validate(product))


@product_router.get(
    "/slug/{slug}",
    response_model=ResponseWrapper[ProductResponse],
    summary="Get product by slug",
)
async def get_product_by_slug(
    slug: str,
    service: CatalogService = Depends(get_catalog_service),
):
    """Get product by slug."""
    product = await service.get_product_by_slug(slug)
    return ResponseWrapper(data=ProductResponse.model_validate(product))


@product_router.post(
    "",
    response_model=ResponseWrapper[ProductResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create product",
)
async def create_product(
    data: ProductCreate,
    service: CatalogService = Depends(get_catalog_service),
):
    """Create new product (admin only)."""
    product = await service.create_product(data)
    return ResponseWrapper(
        message="Product created",
        data=ProductResponse.model_validate(product),
    )


@product_router.patch(
    "/{product_id}",
    response_model=ResponseWrapper[ProductResponse],
    summary="Update product",
)
async def update_product(
    product_id: int,
    data: ProductUpdate,
    service: CatalogService = Depends(get_catalog_service),
):
    """Update product (admin only)."""
    product = await service.update_product(product_id, data)
    return ResponseWrapper(
        message="Product updated",
        data=ProductResponse.model_validate(product),
    )


@product_router.delete(
    "/{product_id}",
    response_model=ResponseWrapper[None],
    summary="Delete product",
)
async def delete_product(
    product_id: int,
    service: CatalogService = Depends(get_catalog_service),
):
    """Delete product (admin only)."""
    await service.delete_product(product_id)
    return ResponseWrapper(message="Product deleted")


# ==================== Modifier Routes ====================

@product_router.post(
    "/{product_id}/modifiers",
    response_model=ResponseWrapper[ModifierResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Add modifier to product",
)
async def add_modifier(
    product_id: int,
    data: ModifierCreate,
    service: CatalogService = Depends(get_catalog_service),
):
    """Add modifier to product (admin only)."""
    modifier = await service.add_modifier(product_id, data)
    return ResponseWrapper(
        message="Modifier added",
        data=ModifierResponse.model_validate(modifier),
    )


@product_router.patch(
    "/modifiers/{modifier_id}",
    response_model=ResponseWrapper[ModifierResponse],
    summary="Update modifier",
)
async def update_modifier(
    modifier_id: int,
    data: ModifierUpdate,
    service: CatalogService = Depends(get_catalog_service),
):
    """Update modifier (admin only)."""
    modifier = await service.update_modifier(modifier_id, data)
    return ResponseWrapper(
        message="Modifier updated",
        data=ModifierResponse.model_validate(modifier),
    )


@product_router.delete(
    "/modifiers/{modifier_id}",
    response_model=ResponseWrapper[None],
    summary="Delete modifier",
)
async def delete_modifier(
    modifier_id: int,
    service: CatalogService = Depends(get_catalog_service),
):
    """Delete modifier (admin only)."""
    await service.delete_modifier(modifier_id)
    return ResponseWrapper(message="Modifier deleted")


# ==================== Menu Routes ====================

menu_router = APIRouter(prefix="/api/v1/menu", tags=["Menu"])


@menu_router.get(
    "",
    response_model=ResponseWrapper[MenuResponse],
    summary="Get full menu",
)
async def get_menu(
    service: CatalogService = Depends(get_catalog_service),
):
    """Get full menu with all categories and products."""
    menu = await service.get_menu()
    return ResponseWrapper(data=menu)


# ==================== Internal Routes ====================

internal_router = APIRouter(prefix="/internal", tags=["Internal"])


@internal_router.post(
    "/products/by-ids",
    response_model=ResponseWrapper[list[ProductResponse]],
    include_in_schema=False,
)
async def get_products_by_ids(
    product_ids: list[int],
    service: CatalogService = Depends(get_catalog_service),
):
    """Get products by IDs (for order service)."""
    products = await service.get_products_by_ids(product_ids)
    return ResponseWrapper(
        data=[ProductResponse.model_validate(p) for p in products],
    )
