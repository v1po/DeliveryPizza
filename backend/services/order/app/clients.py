"""
HTTP client for inter-service communication.
"""
from decimal import Decimal
from typing import Any

import httpx


class CatalogClient:
    """HTTP client for Catalog Service."""
    
    def __init__(self, base_url: str, timeout: float = 10.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
    
    async def get_products_by_ids(
        self,
        product_ids: list[int],
    ) -> list[dict] | None:
        """Get products by IDs from catalog service."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/internal/products/by-ids",
                    json=product_ids,
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        return data.get("data", [])
                return None
        except httpx.RequestError:
            return None
    
    async def get_product(self, product_id: int) -> dict | None:
        """Get single product from catalog service."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/api/v1/products/{product_id}",
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        return data.get("data")
                return None
        except httpx.RequestError:
            return None


class AuthClient:
    """HTTP client for Auth Service."""
    
    def __init__(self, base_url: str, timeout: float = 10.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
    
    async def validate_token(self, token: str) -> dict | None:
        """Validate token and get user info."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/api/v1/auth/validate",
                    headers={"Authorization": f"Bearer {token}"},
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        return data.get("data")
                return None
        except httpx.RequestError:
            return None
