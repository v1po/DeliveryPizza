
import re
from typing import Any

from sqlalchemy import delete, func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from .models import Category, Product, ProductModifier, ProductStatus


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text


class CategoryRepository:
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, **kwargs) -> Category:
        if not kwargs.get("slug"):
            kwargs["slug"] = slugify(kwargs["name"])
        
        category = Category(**kwargs)
        self.session.add(category)
        await self.session.flush()
        await self.session.refresh(category)
        return category
    
    async def get_by_id(self, category_id: int) -> Category | None:
        result = await self.session.execute(
            select(Category)
            .options(selectinload(Category.children))
            .where(Category.id == category_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_slug(self, slug: str) -> Category | None:
        result = await self.session.execute(
            select(Category).where(Category.slug == slug)
        )
        return result.scalar_one_or_none()
    
    async def get_all(
        self,
        active_only: bool = True,
        parent_id: int | None = None,
    ) -> list[Category]:
        query = select(Category).options(selectinload(Category.children))
        
        if active_only:
            query = query.where(Category.is_active == True)
        
        if parent_id is not None:
            query = query.where(Category.parent_id == parent_id)
        else:
            query = query.where(Category.parent_id.is_(None))
        
        query = query.order_by(Category.sort_order, Category.name)
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def get_tree(self, active_only: bool = True) -> list[Category]:
        return await self.get_all(active_only=active_only, parent_id=None)
    
    async def update(self, category_id: int, **kwargs) -> Category | None:

        await self.session.execute(
            update(Category)
            .where(Category.id == category_id)
            .values(**kwargs)
        )
        return await self.get_by_id(category_id)
    
    async def delete(self, category_id: int) -> bool:
        result = await self.session.execute(
            delete(Category).where(Category.id == category_id)
        )
        return result.rowcount > 0
    
    async def count_products(self, category_id: int) -> int:
        result = await self.session.execute(
            select(func.count(Product.id))
            .where(Product.category_id == category_id)
        )
        return result.scalar() or 0


class ProductRepository:
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(
        self,
        modifiers: list[dict] | None = None,
        **kwargs,
    ) -> Product:
        if not kwargs.get("slug"):
            kwargs["slug"] = slugify(kwargs["name"])
        
        product = Product(**kwargs)
        self.session.add(product)
        await self.session.flush()
        
        # Add modifiers
        if modifiers:
            for mod_data in modifiers:
                modifier = ProductModifier(product_id=product.id, **mod_data)
                self.session.add(modifier)
        
        await self.session.flush()
        await self.session.refresh(product)
        return product
    
    async def get_by_id(self, product_id: int) -> Product | None:
        result = await self.session.execute(
            select(Product)
            .options(selectinload(Product.modifiers))
            .where(Product.id == product_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_slug(self, slug: str) -> Product | None:

        result = await self.session.execute(
            select(Product)
            .options(selectinload(Product.modifiers))
            .where(Product.slug == slug)
        )
        return result.scalar_one_or_none()
    
    async def get_by_ids(self, product_ids: list[int]) -> list[Product]:
        result = await self.session.execute(
            select(Product)
            .options(selectinload(Product.modifiers))
            .where(Product.id.in_(product_ids))
        )
        return list(result.scalars().all())
    
    async def get_all(
        self,
        offset: int = 0,
        limit: int = 20,
        category_id: int | None = None,
        status: ProductStatus | None = None,
        is_featured: bool | None = None,
        search: str | None = None,
    ) -> tuple[list[Product], int]:
        query = select(Product).options(selectinload(Product.modifiers))
        
        # Filters
        if category_id is not None:
            query = query.where(Product.category_id == category_id)
        if status is not None:
            query = query.where(Product.status == status)
        if is_featured is not None:
            query = query.where(Product.is_featured == is_featured)
        if search:
            search_term = f"%{search}%"
            query = query.where(
                or_(
                    Product.name.ilike(search_term),
                    Product.description.ilike(search_term),
                )
            )
        
        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.session.execute(count_query)
        total = total_result.scalar() or 0
        
        query = query.offset(offset).limit(limit)
        query = query.order_by(Product.sort_order, Product.name)
        result = await self.session.execute(query)
        products = list(result.scalars().all())
        
        return products, total
    
    async def get_featured(self, limit: int = 10) -> list[Product]:
        result = await self.session.execute(
            select(Product)
            .where(
                Product.is_featured == True,
                Product.status == ProductStatus.AVAILABLE,
            )
            .order_by(Product.sort_order)
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def get_by_category(
        self,
        category_id: int,
        available_only: bool = True,
    ) -> list[Product]:
        query = select(Product).where(Product.category_id == category_id)
        
        if available_only:
            query = query.where(Product.status == ProductStatus.AVAILABLE)
        
        query = query.order_by(Product.sort_order, Product.name)
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def update(self, product_id: int, **kwargs) -> Product | None:
        await self.session.execute(
            update(Product)
            .where(Product.id == product_id)
            .values(**kwargs)
        )
        return await self.get_by_id(product_id)
    
    async def delete(self, product_id: int) -> bool:
        result = await self.session.execute(
            delete(Product).where(Product.id == product_id)
        )
        return result.rowcount > 0


class ModifierRepository:

    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, product_id: int, **kwargs) -> ProductModifier:
        """Create new modifier."""
        modifier = ProductModifier(product_id=product_id, **kwargs)
        self.session.add(modifier)
        await self.session.flush()
        await self.session.refresh(modifier)
        return modifier
    
    async def get_by_id(self, modifier_id: int) -> ProductModifier | None:
        """Get modifier by ID."""
        result = await self.session.execute(
            select(ProductModifier).where(ProductModifier.id == modifier_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_product(self, product_id: int) -> list[ProductModifier]:
        """Get modifiers by product."""
        result = await self.session.execute(
            select(ProductModifier)
            .where(ProductModifier.product_id == product_id)
            .order_by(ProductModifier.sort_order)
        )
        return list(result.scalars().all())
    
    async def update(self, modifier_id: int, **kwargs) -> ProductModifier | None:
        """Update modifier."""
        await self.session.execute(
            update(ProductModifier)
            .where(ProductModifier.id == modifier_id)
            .values(**kwargs)
        )
        return await self.get_by_id(modifier_id)
    
    async def delete(self, modifier_id: int) -> bool:
        """Delete modifier."""
        result = await self.session.execute(
            delete(ProductModifier).where(ProductModifier.id == modifier_id)
        )
        return result.rowcount > 0
