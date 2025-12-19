"""
API Gateway main application.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .config import get_settings
from .middleware import RateLimitMiddleware
from .proxy import ServiceProxy

import sys
sys.path.insert(0, "/app")
from shared.redis_client import RedisClient


# Global instances
redis_client: RedisClient | None = None
service_proxy: ServiceProxy | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    global redis_client, service_proxy
    
    settings = get_settings()
    
    # Initialize Redis
    redis_client = RedisClient(settings.redis_url)
    await redis_client.connect()
    
    # Initialize service proxy
    service_proxy = ServiceProxy(
        auth_url=settings.auth_service_url,
        catalog_url=settings.catalog_service_url,
        order_url=settings.order_service_url,
        timeout=settings.request_timeout,
    )
    
    yield
    
    # Cleanup
    if redis_client:
        await redis_client.disconnect()


app = FastAPI(
    title="Food Delivery API Gateway",
    description="API Gateway for Food Delivery microservices",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Settings
settings = get_settings()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "gateway",
        "services": {
            "auth": settings.auth_service_url,
            "catalog": settings.catalog_service_url,
            "order": settings.order_service_url,
        },
    }


# Service status
@app.get("/services/status", tags=["Services"])
async def services_status():
    """Check status of all services."""
    import httpx
    
    statuses = {}
    services = {
        "auth": settings.auth_service_url,
        "catalog": settings.catalog_service_url,
        "order": settings.order_service_url,
    }
    
    async with httpx.AsyncClient(timeout=5.0) as client:
        for name, url in services.items():
            try:
                response = await client.get(f"{url}/health")
                statuses[name] = {
                    "status": "healthy" if response.status_code == 200 else "unhealthy",
                    "url": url,
                }
            except Exception:
                statuses[name] = {
                    "status": "unreachable",
                    "url": url,
                }
    
    return {"services": statuses}


# Proxy routes to services
@app.api_route(
    "/api/{path:path}",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    tags=["Proxy"],
    include_in_schema=False,
)
async def proxy_api(request: Request, path: str):
    """Proxy all /api/* requests to appropriate services."""
    if service_proxy is None:
        return JSONResponse(
            status_code=503,
            content={"success": False, "message": "Gateway not initialized"},
        )
    
    full_path = f"/api/{path}"
    return await service_proxy.proxy_request(request, full_path)


# Add rate limiting after app is created
@app.on_event("startup")
async def add_rate_limiting():
    """Add rate limiting middleware after startup."""
    if redis_client and settings.rate_limit_enabled:
        app.add_middleware(
            RateLimitMiddleware,
            redis_client=redis_client,
            max_requests=settings.rate_limit_requests,
            window_seconds=settings.rate_limit_period,
            enabled=settings.rate_limit_enabled,
        )
