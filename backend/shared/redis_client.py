"""
Redis client for caching and session management.
"""
import json
from typing import Any

import redis.asyncio as redis


class RedisClient:
    """Async Redis client wrapper with caching utilities."""
    
    def __init__(self, redis_url: str):
        self.redis_url = redis_url
        self.client: redis.Redis | None = None
    
    async def connect(self):
        """Initialize Redis connection."""
        self.client = redis.from_url(
            self.redis_url,
            encoding="utf-8",
            decode_responses=True,
        )
    
    async def disconnect(self):
        """Close Redis connection."""
        if self.client:
            await self.client.close()
    
    async def get(self, key: str) -> str | None:
        """Get value by key."""
        if not self.client:
            return None
        return await self.client.get(key)
    
    async def set(
        self,
        key: str,
        value: str,
        expire: int | None = None,
    ) -> bool:
        """Set value with optional expiration in seconds."""
        if not self.client:
            return False
        await self.client.set(key, value, ex=expire)
        return True
    
    async def delete(self, key: str) -> bool:
        """Delete key."""
        if not self.client:
            return False
        await self.client.delete(key)
        return True
    
    async def exists(self, key: str) -> bool:
        """Check if key exists."""
        if not self.client:
            return False
        return await self.client.exists(key) > 0
    
    async def get_json(self, key: str) -> dict | list | None:
        """Get JSON value by key."""
        value = await self.get(key)
        if value:
            return json.loads(value)
        return None
    
    async def set_json(
        self,
        key: str,
        value: dict | list,
        expire: int | None = None,
    ) -> bool:
        """Set JSON value with optional expiration."""
        return await self.set(key, json.dumps(value), expire)
    
    async def invalidate_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern."""
        if not self.client:
            return 0
        keys = []
        async for key in self.client.scan_iter(match=pattern):
            keys.append(key)
        if keys:
            return await self.client.delete(*keys)
        return 0
    
    # Token blacklist methods
    async def blacklist_token(self, token: str, expire: int) -> bool:
        """Add token to blacklist."""
        return await self.set(f"blacklist:{token}", "1", expire)
    
    async def is_token_blacklisted(self, token: str) -> bool:
        """Check if token is blacklisted."""
        return await self.exists(f"blacklist:{token}")
