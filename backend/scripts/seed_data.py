"""
Test data seeder for development.
Run: python -m scripts.seed_data
"""
import asyncio
import sys
from decimal import Decimal

sys.path.insert(0, ".")

from shared.database import DatabaseManager
from shared.security import SecurityManager


async def seed_auth_db():
    """Seed auth database with test users."""
    from services.auth.app.models import User
    from shared.schemas import UserRole
    
    db = DatabaseManager("postgresql+asyncpg://postgres:postgres@localhost:5432/auth_db")
    security = SecurityManager("test-secret-key")
    
    await db.create_tables()
    
    users = [
        {
            "email": "admin@example.com",
            "hashed_password": security.hash_password("Admin123!"),
            "first_name": "Admin",
            "last_name": "User",
            "role": UserRole.ADMIN,
            "is_verified": True,
        },
        {
            "email": "manager@example.com",
            "hashed_password": security.hash_password("Manager123!"),
            "first_name": "Manager",
            "last_name": "User",
            "role": UserRole.MANAGER,
            "is_verified": True,
        },
        {
            "email": "customer@example.com",
            "hashed_password": security.hash_password("Customer123!"),
            "first_name": "Customer",
            "last_name": "User",
            "role": UserRole.CUSTOMER,
            "is_verified": True,
        },
        {
            "email": "courier@example.com",
            "hashed_password": security.hash_password("Courier123!"),
            "first_name": "Courier",
            "last_name": "User",
            "role": UserRole.COURIER,
            "is_verified": True,
        },
    ]
    
    async with db.session() as session:
        for user_data in users:
            user = User(**user_data)
            session.add(user)
        await session.commit()
    
    print("✅ Auth database seeded")


async def seed_catalog_db():
    """Seed catalog database with test data."""
    from services.catalog.app.models import Category, Product, ProductModifier, ProductStatus
    
    db = DatabaseManager("postgresql+asyncpg://postgres:postgres@localhost:5432/catalog_db")
    await db.create_tables()
    
    categories = [
        {"name": "Пицца", "slug": "pizza", "description": "Итальянская пицца на тонком тесте", "sort_order": 1},
        {"name": "Бургеры", "slug": "burgers", "description": "Сочные бургеры с различными начинками", "sort_order": 2},
        {"name": "Суши", "slug": "sushi", "description": "Свежие роллы и суши", "sort_order": 3},
        {"name": "Напитки", "slug": "drinks", "description": "Прохладительные напитки", "sort_order": 4},
        {"name": "Десерты", "slug": "desserts", "description": "Сладкие десерты", "sort_order": 5},
    ]
    
    async with db.session() as session:
        # Create categories
        cat_objects = {}
        for cat_data in categories:
            cat = Category(**cat_data)
            session.add(cat)
            await session.flush()
            cat_objects[cat_data["slug"]] = cat
        
        # Create products
        products = [
            # Пицца
            {
                "name": "Маргарита",
                "slug": "margherita",
                "description": "Классическая пицца с томатным соусом и моцареллой",
                "short_description": "Томаты, моцарелла, базилик",
                "price": Decimal("450"),
                "category_id": cat_objects["pizza"].id,
                "status": ProductStatus.AVAILABLE,
                "is_featured": True,
                "calories": 800,
                "weight": "500г",
                "preparation_time": 25,
            },
            {
                "name": "Пепперони",
                "slug": "pepperoni",
                "description": "Пицца с пикантной колбаской пепперони",
                "short_description": "Пепперони, моцарелла, томатный соус",
                "price": Decimal("550"),
                "category_id": cat_objects["pizza"].id,
                "status": ProductStatus.AVAILABLE,
                "is_featured": True,
                "calories": 950,
                "weight": "550г",
                "preparation_time": 25,
            },
            {
                "name": "Четыре сыра",
                "slug": "four-cheese",
                "description": "Пицца с четырьмя видами сыра",
                "short_description": "Моцарелла, горгонзола, пармезан, эмменталь",
                "price": Decimal("620"),
                "category_id": cat_objects["pizza"].id,
                "status": ProductStatus.AVAILABLE,
                "calories": 1100,
                "weight": "520г",
                "preparation_time": 25,
            },
            # Бургеры
            {
                "name": "Классический бургер",
                "slug": "classic-burger",
                "description": "Сочная говяжья котлета с овощами",
                "short_description": "Говядина, салат, томаты, соус",
                "price": Decimal("350"),
                "category_id": cat_objects["burgers"].id,
                "status": ProductStatus.AVAILABLE,
                "is_featured": True,
                "calories": 650,
                "weight": "300г",
                "preparation_time": 15,
            },
            {
                "name": "Чизбургер",
                "slug": "cheeseburger",
                "description": "Бургер с двойным сыром чеддер",
                "short_description": "Говядина, двойной чеддер, соус",
                "price": Decimal("390"),
                "category_id": cat_objects["burgers"].id,
                "status": ProductStatus.AVAILABLE,
                "calories": 750,
                "weight": "320г",
                "preparation_time": 15,
            },
            # Суши
            {
                "name": "Филадельфия",
                "slug": "philadelphia",
                "description": "Классический ролл с лососем и сливочным сыром",
                "short_description": "Лосось, сливочный сыр, огурец",
                "price": Decimal("420"),
                "category_id": cat_objects["sushi"].id,
                "status": ProductStatus.AVAILABLE,
                "is_featured": True,
                "calories": 350,
                "weight": "250г",
                "preparation_time": 20,
            },
            {
                "name": "Калифорния",
                "slug": "california",
                "description": "Ролл с крабом и авокадо",
                "short_description": "Краб, авокадо, огурец, икра",
                "price": Decimal("380"),
                "category_id": cat_objects["sushi"].id,
                "status": ProductStatus.AVAILABLE,
                "calories": 280,
                "weight": "220г",
                "preparation_time": 20,
            },
            # Напитки
            {
                "name": "Кока-Кола",
                "slug": "coca-cola",
                "description": "Классическая Кока-Кола",
                "short_description": "0.5л",
                "price": Decimal("80"),
                "category_id": cat_objects["drinks"].id,
                "status": ProductStatus.AVAILABLE,
                "calories": 200,
                "weight": "500мл",
                "preparation_time": 1,
            },
            {
                "name": "Свежевыжатый апельсиновый сок",
                "slug": "fresh-orange",
                "description": "Свежевыжатый сок из апельсинов",
                "short_description": "0.3л",
                "price": Decimal("150"),
                "category_id": cat_objects["drinks"].id,
                "status": ProductStatus.AVAILABLE,
                "calories": 120,
                "weight": "300мл",
                "preparation_time": 5,
            },
            # Десерты
            {
                "name": "Тирамису",
                "slug": "tiramisu",
                "description": "Классический итальянский десерт",
                "short_description": "Маскарпоне, кофе, какао",
                "price": Decimal("280"),
                "category_id": cat_objects["desserts"].id,
                "status": ProductStatus.AVAILABLE,
                "is_featured": True,
                "calories": 400,
                "weight": "150г",
                "preparation_time": 5,
            },
        ]
        
        for prod_data in products:
            product = Product(**prod_data)
            session.add(product)
        
        await session.commit()
    
    print("✅ Catalog database seeded")


async def main():
    """Run all seeders."""
    print("🌱 Starting database seeding...")
    
    try:
        await seed_auth_db()
    except Exception as e:
        print(f"❌ Auth seeding failed: {e}")
    
    try:
        await seed_catalog_db()
    except Exception as e:
        print(f"❌ Catalog seeding failed: {e}")
    
    print("🎉 Seeding complete!")
    print("\n📧 Test accounts:")
    print("  admin@example.com / Admin123!")
    print("  manager@example.com / Manager123!")
    print("  customer@example.com / Customer123!")
    print("  courier@example.com / Courier123!")


if __name__ == "__main__":
    asyncio.run(main())
