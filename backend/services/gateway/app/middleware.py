"""
Rate limiting middleware using Redis.
"""
import time

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

import sys
sys.path.insert(0, "/app")
from shared.redis_client import RedisClient


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware using sliding window."""
    
    def __init__(
        self,
        app,
        redis_client: RedisClient,
        max_requests: int = 100,
        window_seconds: int = 60,
        enabled: bool = True,
    ):
        super().__init__(app)
        self.redis = redis_client
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.enabled = enabled
    
    def _get_client_id(self, request: Request) -> str:
        """Get client identifier from request."""
        # Try to get from Authorization header (user-based)
        auth_header = request.headers.get("authorization")
        if auth_header:
            # Use hash of token as identifier
            return f"user:{hash(auth_header)}"
        
        # Fall back to IP address
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            ip = forwarded.split(",")[0].strip()
        else:
            ip = request.client.host if request.client else "unknown"
        
        return f"ip:{ip}"
    
    async def dispatch(self, request: Request, call_next):
        """Process request with rate limiting."""
        if not self.enabled:
            return await call_next(request)
        
        # Skip rate limiting for health checks
        if request.url.path == "/health":
            return await call_next(request)
        
        client_id = self._get_client_id(request)
        key = f"ratelimit:{client_id}"
        
        now = int(time.time())
        window_start = now - self.window_seconds
        
        # Use Redis if available
        if self.redis.client:
            try:
                # Remove old entries
                await self.redis.client.zremrangebyscore(key, 0, window_start)
                
                # Count requests in window
                request_count = await self.redis.client.zcard(key)
                
                if request_count >= self.max_requests:
                    return Response(
                        content='{"success": false, "message": "Rate limit exceeded", "error_code": "RATE_LIMITED"}',
                        status_code=429,
                        media_type="application/json",
                        headers={
                            "X-RateLimit-Limit": str(self.max_requests),
                            "X-RateLimit-Remaining": "0",
                            "X-RateLimit-Reset": str(now + self.window_seconds),
                            "Retry-After": str(self.window_seconds),
                        },
                    )
                
                # Add current request
                await self.redis.client.zadd(key, {str(now): now})
                await self.redis.client.expire(key, self.window_seconds)
                
                # Process request
                response = await call_next(request)
                
                # Add rate limit headers
                response.headers["X-RateLimit-Limit"] = str(self.max_requests)
                response.headers["X-RateLimit-Remaining"] = str(
                    self.max_requests - request_count - 1
                )
                response.headers["X-RateLimit-Reset"] = str(now + self.window_seconds)
                
                return response
                
            except Exception:
                # If Redis fails, allow request through
                return await call_next(request)
        
        return await call_next(request)
