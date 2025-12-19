"""
Catalog Service main application.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from . import dependencies
from .config import get_settings
from .routes import category_router, internal_router, menu_router, product_router

import sys
sys.path.insert(0, "/app")
from shared.database import DatabaseManager
from shared.exceptions import BaseAPIException
from shared.redis_client import RedisClient


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    settings = get_settings()
    
    # Initialize database
    dependencies.db_manager = DatabaseManager(settings.database_url)
    await dependencies.db_manager.create_tables()
    
    # Initialize Redis
    dependencies.redis_client = RedisClient(settings.redis_url)
    await dependencies.redis_client.connect()
    
    yield
    
    # Cleanup
    if dependencies.redis_client:
        await dependencies.redis_client.disconnect()


app = FastAPI(
    title="Catalog Service",
    description="Product catalog and menu management microservice",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handlers
@app.exception_handler(BaseAPIException)
async def api_exception_handler(request: Request, exc: BaseAPIException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.detail,
            "error_code": getattr(exc, "error_code", None),
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "message": "Internal server error",
            "error_code": "INTERNAL_ERROR",
        },
    )


# Health check
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "catalog"}


# Include routers
app.include_router(category_router)
app.include_router(product_router)
app.include_router(menu_router)
app.include_router(internal_router)
