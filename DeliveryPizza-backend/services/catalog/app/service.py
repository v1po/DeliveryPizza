"""
Catalog service business logic with caching.
"""
import json

from .models import Category, Product, ProductModifier, ProductStatus
from .repository import CategoryRepository, ModifierRepository, ProductRepository
from .schemas import (
    CategoryCreate,
    CategoryUpdate,
    CategoryWithChildren,
    MenuCategory,
    MenuResponse,
    ModifierCreate,
    ModifierUpdate,
    ProductCreate,
    ProductListResponse,
    ProductUpdate,
)

import sys
sys.path.insert(0, "/app")
from shared.exceptions import AlreadyExistsException, NotFoundException
from shared.redis_client import RedisClient


class CatalogService:
    """Catalog management service with caching."""
    
    def __init__(
        self,
        category_repo: CategoryRepository,
        product_repo: ProductRepository,
        modifier_repo: ModifierRepository,
        redis: RedisClient,
        cache_ttl_categories: int = 300,
        cache_ttl_products: int = 60,
        cache_ttl_menu: int = 120,
    ):
        self.category_repo = category_repo
        self.product_repo = product_repo
        self.modifier_repo = modifier_repo
        self.redis = redis
        self.cache_ttl_categories = cache_ttl_categories
        self.cache_ttl_products = cache_ttl_products
        self.cache_ttl_menu = cache_ttl_menu
    
    # ==================== Categories ====================
    
    async def create_category(self, data: CategoryCreate) -> Category:
        """Create new category."""
        # Check slug uniqueness
        if data.slug:
            existing = await self.category_repo.get_by_slug(data.slug)
            if existing:
                raise AlreadyExistsException("Category with this slug")
        
        category = await self.category_repo.create(**data.model_dump())
        await self._invalidate_category_cache()
        return category
    
    async def get_category(self, category_id: int) -> Category:
        """Get category by ID."""
        category = await self.category_repo.get_by_id(category_id)
        if not category:
            raise NotFoundException("Category")
        return category
    
    async def get_category_by_slug(self, slug: str) -> Category:
        """Get category by slug."""
        category = await self.category_repo.get_by_slug(slug)
        if not category:
            raise NotFoundException("Category")
        return category
    
    async def get_categories(self, active_only: bool = True) -> list[Category]:
        """Get all categories from cache or database."""
        cache_key = f"categories:all:{active_only}"
        
        # Try cache
        cached = await self.redis.get(cache_key)
        if cached:
            # Return from cache (simplified)
            pass
        
        categories = await self.category_repo.get_all(active_only=active_only)
        return categories
    
    async def get_category_tree(
        self,
        active_only: bool = True,
    ) -> list[CategoryWithChildren]:
        """Get category tree with product counts."""
        categories = await self.category_repo.get_tree(active_only=active_only)
        
        result = []
        for cat in categories:
            products_count = await self.category_repo.count_products(cat.id)
            cat_data = CategoryWithChildren.model_validate(cat)
            cat_data.products_count = products_count
            
            # Process children
            children = []
            for child in cat.children:
                if active_only and not child.is_active:
                    continue
                child_count = await self.category_repo.count_products(child.id)
                child_data = CategoryWithChildren.model_validate(child)
                child_data.products_count = child_count
                children.append(child_data)
            
            cat_data.children = children
            result.append(cat_data)
        
        return result
    
    async def update_category(
        self,
        category_id: int,
        data: CategoryUpdate,
    ) -> Category:
        """Update category."""
        category = await self.category_repo.get_by_id(category_id)
        if not category:
            raise NotFoundException("Category")
        
        update_data = data.model_dump(exclude_unset=True)
        
        # Check slug uniqueness
        if "slug" in update_data and update_data["slug"] != category.slug:
            existing = await self.category_repo.get_by_slug(update_data["slug"])
            if existing:
                raise AlreadyExistsException("Category with this slug")
        
        category = await self.category_repo.update(category_id, **update_data)
        await self._invalidate_category_cache()
        return category
    
    async def delete_category(self, category_id: int) -> bool:
        """Delete category."""
        category = await self.category_repo.get_by_id(category_id)
        if not category:
            raise NotFoundException("Category")
        
        result = await self.category_repo.delete(category_id)
        await self._invalidate_category_cache()
        return result
    
    # ==================== Products ====================
    
    async def create_product(self, data: ProductCreate) -> Product:
        """Create new product."""
        # Check category exists
        category = await self.category_repo.get_by_id(data.category_id)
        if not category:
            raise NotFoundException("Category")
        
        # Check slug uniqueness
        if data.slug:
            existing = await self.product_repo.get_by_slug(data.slug)
            if existing:
                raise AlreadyExistsException("Product with this slug")
        
        product_data = data.model_dump(exclude={"modifiers"})
        modifiers_data = [m.model_dump() for m in data.modifiers]
        
        product = await self.product_repo.create(
            modifiers=modifiers_data,
            **product_data,
        )
        
        await self._invalidate_product_cache()
        return product
    
    async def get_product(self, product_id: int) -> Product:
        """Get product by ID."""
        cache_key = f"product:{product_id}"
        
        product = await self.product_repo.get_by_id(product_id)
        if not product:
            raise NotFoundException("Product")
        return product
    
    async def get_product_by_slug(self, slug: str) -> Product:
        """Get product by slug."""
        product = await self.product_repo.get_by_slug(slug)
        if not product:
            raise NotFoundException("Product")
        return product
    
    async def get_products(
        self,
        offset: int = 0,
        limit: int = 20,
        category_id: int | None = None,
        status: ProductStatus | None = None,
        is_featured: bool | None = None,
        search: str | None = None,
    ) -> tuple[list[Product], int]:
        """Get products with filtering."""
        return await self.product_repo.get_all(
            offset=offset,
            limit=limit,
            category_id=category_id,
            status=status,
            is_featured=is_featured,
            search=search,
        )
    
    async def get_products_by_ids(self, product_ids: list[int]) -> list[Product]:
        """Get products by IDs (for order service)."""
        return await self.product_repo.get_by_ids(product_ids)
    
    async def get_featured_products(self, limit: int = 10) -> list[Product]:
        """Get featured products."""
        return await self.product_repo.get_featured(limit)
    
    async def update_product(
        self,
        product_id: int,
        data: ProductUpdate,
    ) -> Product:
        """Update product."""
        product = await self.product_repo.get_by_id(product_id)
        if not product:
            raise NotFoundException("Product")
        
        update_data = data.model_dump(exclude_unset=True)
        
        # Check slug uniqueness
        if "slug" in update_data and update_data["slug"] != product.slug:
            existing = await self.product_repo.get_by_slug(update_data["slug"])
            if existing:
                raise AlreadyExistsException("Product with this slug")
        
        # Check category exists
        if "category_id" in update_data:
            category = await self.category_repo.get_by_id(update_data["category_id"])
            if not category:
                raise NotFoundException("Category")
        
        product = await self.product_repo.update(product_id, **update_data)
        await self._invalidate_product_cache(product_id)
        return product
    
    async def delete_product(self, product_id: int) -> bool:
        """Delete product."""
        product = await self.product_repo.get_by_id(product_id)
        if not product:
            raise NotFoundException("Product")
        
        result = await self.product_repo.delete(product_id)
        await self._invalidate_product_cache(product_id)
        return result
    
    # ==================== Modifiers ====================
    
    async def add_modifier(
        self,
        product_id: int,
        data: ModifierCreate,
    ) -> ProductModifier:
        """Add modifier to product."""
        product = await self.product_repo.get_by_id(product_id)
        if not product:
            raise NotFoundException("Product")
        
        modifier = await self.modifier_repo.create(
            product_id=product_id,
            **data.model_dump(),
        )
        await self._invalidate_product_cache(product_id)
        return modifier
    
    async def update_modifier(
        self,
        modifier_id: int,
        data: ModifierUpdate,
    ) -> ProductModifier:
        """Update modifier."""
        modifier = await self.modifier_repo.get_by_id(modifier_id)
        if not modifier:
            raise NotFoundException("Modifier")
        
        update_data = data.model_dump(exclude_unset=True)
        modifier = await self.modifier_repo.update(modifier_id, **update_data)
        await self._invalidate_product_cache(modifier.product_id)
        return modifier
    
    async def delete_modifier(self, modifier_id: int) -> bool:
        """Delete modifier."""
        modifier = await self.modifier_repo.get_by_id(modifier_id)
        if not modifier:
            raise NotFoundException("Modifier")
        
        product_id = modifier.product_id
        result = await self.modifier_repo.delete(modifier_id)
        await self._invalidate_product_cache(product_id)
        return result
    
    # ==================== Menu ====================
    
    async def get_menu(self) -> MenuResponse:
        """Get full menu with categories and products."""
        cache_key = "menu:full"
        
        # Try cache
        cached = await self.redis.get_json(cache_key)
        if cached:
            return MenuResponse(**cached)
        
        # Build menu
        categories = await self.category_repo.get_all(active_only=True)
        
        menu_categories = []
        for cat in categories:
            products = await self.product_repo.get_by_category(
                cat.id,
                available_only=True,
            )
            
            menu_categories.append(MenuCategory(
                id=cat.id,
                name=cat.name,
                slug=cat.slug,
                description=cat.description,
                image_url=cat.image_url,
                products=[ProductListResponse.model_validate(p) for p in products],
            ))
        
        featured = await self.product_repo.get_featured()
        
        menu = MenuResponse(
            categories=menu_categories,
            featured_products=[ProductListResponse.model_validate(p) for p in featured],
        )
        
        # Cache
        await self.redis.set_json(
            cache_key,
            menu.model_dump(mode="json"),
            expire=self.cache_ttl_menu,
        )
        
        return menu
    
    # ==================== Cache management ====================
    
    async def _invalidate_category_cache(self):
        """Invalidate category cache."""
        await self.redis.invalidate_pattern("categories:*")
        await self.redis.invalidate_pattern("menu:*")
    
    async def _invalidate_product_cache(self, product_id: int | None = None):
        """Invalidate product cache."""
        if product_id:
            await self.redis.delete(f"product:{product_id}")
        await self.redis.invalidate_pattern("products:*")
        await self.redis.invalidate_pattern("menu:*")
