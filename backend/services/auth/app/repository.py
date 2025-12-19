"""
User repository for database operations.
"""
from datetime import datetime, timezone

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from .models import User

import sys
sys.path.insert(0, "/app")
from shared.schemas import UserRole


class UserRepository:
    """User database repository."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(
        self,
        email: str,
        hashed_password: str,
        first_name: str,
        last_name: str,
        phone: str | None = None,
        role: UserRole = UserRole.CUSTOMER,
    ) -> User:
        """Create new user."""
        user = User(
            email=email,
            hashed_password=hashed_password,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            role=role,
        )
        self.session.add(user)
        await self.session.flush()
        await self.session.refresh(user)
        return user
    
    async def get_by_id(self, user_id: int) -> User | None:
        """Get user by ID."""
        result = await self.session.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_email(self, email: str) -> User | None:
        """Get user by email."""
        result = await self.session.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()
    
    async def get_active_by_email(self, email: str) -> User | None:
        """Get active user by email."""
        result = await self.session.execute(
            select(User).where(
                User.email == email,
                User.is_active == True,
            )
        )
        return result.scalar_one_or_none()
    
    async def update(self, user_id: int, **kwargs) -> User | None:
        """Update user fields."""
        await self.session.execute(
            update(User)
            .where(User.id == user_id)
            .values(**kwargs)
        )
        return await self.get_by_id(user_id)
    
    async def update_last_login(self, user_id: int) -> None:
        """Update user's last login timestamp."""
        await self.session.execute(
            update(User)
            .where(User.id == user_id)
            .values(last_login=datetime.now(timezone.utc))
        )
    
    async def get_all(
        self,
        offset: int = 0,
        limit: int = 20,
        role: UserRole | None = None,
        is_active: bool | None = None,
    ) -> tuple[list[User], int]:
        """Get all users with pagination and filters."""
        query = select(User)
        
        if role is not None:
            query = query.where(User.role == role)
        if is_active is not None:
            query = query.where(User.is_active == is_active)
        
        # Count total
        from sqlalchemy import func
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.session.execute(count_query)
        total = total_result.scalar() or 0
        
        # Get paginated results
        query = query.offset(offset).limit(limit).order_by(User.created_at.desc())
        result = await self.session.execute(query)
        users = list(result.scalars().all())
        
        return users, total
    
    async def delete(self, user_id: int) -> bool:
        """Soft delete user (set is_active to False)."""
        result = await self.session.execute(
            update(User)
            .where(User.id == user_id)
            .values(is_active=False)
        )
        return result.rowcount > 0
