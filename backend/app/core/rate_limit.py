"""Rate limiting middleware for FastAPI."""

import time
from collections import defaultdict
from typing import Dict, Tuple
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from .config import get_settings


class RateLimiter:
    """
    Simple in-memory rate limiter.

    For production use, consider using Redis or a dedicated rate limiting service.
    """

    def __init__(self, requests_per_window: int = 100, window_seconds: int = 60):
        """
        Initialize rate limiter.

        Args:
            requests_per_window: Maximum number of requests allowed per window
            window_seconds: Time window in seconds
        """
        self.requests_per_window = requests_per_window
        self.window_seconds = window_seconds
        # Store: {ip: [(timestamp, count)]}
        self.requests: Dict[str, list] = defaultdict(list)

    def is_allowed(self, client_ip: str) -> Tuple[bool, int]:
        """
        Check if request from client is allowed.

        Args:
            client_ip: Client IP address

        Returns:
            Tuple of (is_allowed, remaining_requests)
        """
        current_time = time.time()
        window_start = current_time - self.window_seconds

        # Remove old requests outside the current window
        self.requests[client_ip] = [
            (timestamp, count)
            for timestamp, count in self.requests[client_ip]
            if timestamp > window_start
        ]

        # Count requests in current window
        total_requests = sum(count for _, count in self.requests[client_ip])

        if total_requests >= self.requests_per_window:
            return False, 0

        # Add current request
        self.requests[client_ip].append((current_time, 1))

        remaining = self.requests_per_window - total_requests - 1
        return True, remaining

    def clear_old_entries(self):
        """Clear entries older than the time window to prevent memory bloat."""
        current_time = time.time()
        window_start = current_time - self.window_seconds

        for ip in list(self.requests.keys()):
            self.requests[ip] = [
                (timestamp, count)
                for timestamp, count in self.requests[ip]
                if timestamp > window_start
            ]
            # Remove empty entries
            if not self.requests[ip]:
                del self.requests[ip]


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware to apply rate limiting to requests."""

    def __init__(self, app, rate_limiter: RateLimiter = None):
        """
        Initialize rate limit middleware.

        Args:
            app: FastAPI application
            rate_limiter: RateLimiter instance (optional)
        """
        super().__init__(app)
        settings = get_settings()

        if rate_limiter is None:
            self.rate_limiter = RateLimiter(
                requests_per_window=settings.rate_limit_requests,
                window_seconds=settings.rate_limit_window
            )
        else:
            self.rate_limiter = rate_limiter

        self.enabled = settings.rate_limit_enabled

    async def dispatch(self, request: Request, call_next):
        """Process request with rate limiting."""
        if not self.enabled:
            return await call_next(request)

        # Skip rate limiting for health checks
        if request.url.path in ["/api/healthz", "/health", "/", "/docs", "/openapi.json"]:
            return await call_next(request)

        # Get client IP
        client_ip = request.client.host if request.client else "unknown"

        # Check if forwarded (behind proxy)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            client_ip = forwarded_for.split(",")[0].strip()

        # Check rate limit
        is_allowed, remaining = self.rate_limiter.is_allowed(client_ip)

        if not is_allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please try again later.",
                headers={
                    "Retry-After": str(self.rate_limiter.window_seconds),
                    "X-RateLimit-Limit": str(self.rate_limiter.requests_per_window),
                    "X-RateLimit-Remaining": "0",
                }
            )

        # Process request
        response = await call_next(request)

        # Add rate limit headers to response
        response.headers["X-RateLimit-Limit"] = str(self.rate_limiter.requests_per_window)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(time.time()) + self.rate_limiter.window_seconds)

        return response
