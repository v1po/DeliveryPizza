"""
Service proxy for routing requests to microservices.
"""
from typing import Any

import httpx
from fastapi import Request, Response


class ServiceProxy:
    """HTTP proxy for microservices."""
    
    def __init__(
        self,
        auth_url: str,
        catalog_url: str,
        order_url: str,
        timeout: float = 30.0,
    ):
        self.services = {
            "auth": auth_url.rstrip("/"),
            "catalog": catalog_url.rstrip("/"),
            "order": order_url.rstrip("/"),
        }
        self.timeout = timeout
    
    def _get_service_url(self, path: str) -> tuple[str, str] | None:
        """Determine service and construct URL based on path."""
        path_lower = path.lower()
        
        # Auth service routes
        if path_lower.startswith("/api/v1/auth") or path_lower.startswith("/api/v1/admin/users"):
            return self.services["auth"], path
        
        # Catalog service routes
        if any(path_lower.startswith(p) for p in [
            "/api/v1/categories",
            "/api/v1/products",
            "/api/v1/menu",
        ]):
            return self.services["catalog"], path
        
        # Order service routes
        if path_lower.startswith("/api/v1/orders") or path_lower.startswith("/api/v1/admin/orders"):
            return self.services["order"], path
        
        return None
    
    async def proxy_request(
        self,
        request: Request,
        path: str,
    ) -> Response:
        """Proxy request to appropriate service."""
        service_info = self._get_service_url(path)
        
        if not service_info:
            return Response(
                content='{"success": false, "message": "Service not found"}',
                status_code=404,
                media_type="application/json",
            )
        
        service_url, service_path = service_info
        url = f"{service_url}{service_path}"
        
        # Build headers (forward relevant ones)
        headers = {}
        for key, value in request.headers.items():
            if key.lower() not in ["host", "content-length"]:
                headers[key] = value
        
        # Get request body
        body = await request.body()
        
        # Build query params
        params = dict(request.query_params)
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.request(
                    method=request.method,
                    url=url,
                    headers=headers,
                    content=body if body else None,
                    params=params,
                )
                
                return Response(
                    content=response.content,
                    status_code=response.status_code,
                    headers=dict(response.headers),
                    media_type=response.headers.get("content-type"),
                )
        
        except httpx.TimeoutException:
            return Response(
                content='{"success": false, "message": "Service timeout", "error_code": "TIMEOUT"}',
                status_code=504,
                media_type="application/json",
            )
        except httpx.RequestError as e:
            return Response(
                content=f'{{"success": false, "message": "Service unavailable", "error_code": "SERVICE_UNAVAILABLE"}}',
                status_code=503,
                media_type="application/json",
            )
