"""Rate limiting middleware for DoS protection."""

import time
import logging
from collections import defaultdict
from typing import Dict, Tuple
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from .security import RateLimitConfig

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    In-memory rate limiter.

    For production, use Redis or similar distributed cache.
    This implementation uses a sliding window algorithm.
    """

    def __init__(self):
        """Initialize rate limiter."""
        # Storage: {client_id: {endpoint: [(timestamp, count)]}}
        self.requests: Dict[str, Dict[str, list]] = defaultdict(lambda: defaultdict(list))
        self.cleanup_interval = 60  # Cleanup old entries every 60 seconds
        self.last_cleanup = time.time()

    def is_allowed(self, client_id: str, endpoint: str, limit: int, window: int = 60) -> Tuple[bool, int]:
        """
        Check if request is allowed based on rate limits.

        Args:
            client_id: Client identifier (IP address or API key)
            endpoint: Endpoint being accessed
            limit: Maximum requests allowed in window
            window: Time window in seconds (default 60)

        Returns:
            Tuple of (is_allowed, remaining_requests)
        """
        current_time = time.time()

        # Cleanup old entries periodically
        if current_time - self.last_cleanup > self.cleanup_interval:
            self._cleanup_old_entries(current_time, window)
            self.last_cleanup = current_time

        # Get request history for this client and endpoint
        request_history = self.requests[client_id][endpoint]

        # Remove requests outside the current window
        cutoff_time = current_time - window
        request_history[:] = [ts for ts in request_history if ts > cutoff_time]

        # Check if limit exceeded
        current_count = len(request_history)
        if current_count >= limit:
            return False, 0

        # Add current request
        request_history.append(current_time)

        remaining = limit - (current_count + 1)
        return True, remaining

    def _cleanup_old_entries(self, current_time: float, window: int):
        """Remove old entries to prevent memory growth."""
        cutoff_time = current_time - (window * 2)  # Keep 2x window for safety

        # Remove old entries
        clients_to_remove = []
        for client_id, endpoints in self.requests.items():
            endpoints_to_remove = []
            for endpoint, history in endpoints.items():
                # Clean up old timestamps
                history[:] = [ts for ts in history if ts > cutoff_time]
                if not history:
                    endpoints_to_remove.append(endpoint)

            # Remove empty endpoints
            for endpoint in endpoints_to_remove:
                del endpoints[endpoint]

            # Mark client for removal if no endpoints left
            if not endpoints:
                clients_to_remove.append(client_id)

        # Remove empty clients
        for client_id in clients_to_remove:
            del self.requests[client_id]

        logger.debug(f"Rate limiter cleanup: removed {len(clients_to_remove)} clients")


# Global rate limiter instance
rate_limiter = RateLimiter()


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware to enforce rate limits on API endpoints."""

    def __init__(self, app):
        """Initialize middleware."""
        super().__init__(app)
        self.rate_limiter = rate_limiter

        # Define rate limits per endpoint pattern
        self.endpoint_limits = {
            "/api/analytics/analyze": (RateLimitConfig.ANALYZE_ENDPOINT_LIMIT, 60),  # 10 per minute
            "/api/dashboard": (RateLimitConfig.DASHBOARD_ENDPOINT_LIMIT, 60),  # 60 per minute
            "/api/dashboard/brand": (RateLimitConfig.DASHBOARD_ENDPOINT_LIMIT, 60),  # 60 per minute
        }

    async def dispatch(self, request: Request, call_next):
        """Process request with rate limiting."""
        # Get client identifier (IP address)
        client_ip = self._get_client_ip(request)

        # Check if endpoint has rate limits
        endpoint_key = self._get_endpoint_key(request.url.path)

        if endpoint_key:
            limit, window = self.endpoint_limits[endpoint_key]

            # Check rate limit
            allowed, remaining = self.rate_limiter.is_allowed(
                client_id=client_ip,
                endpoint=endpoint_key,
                limit=limit,
                window=window
            )

            if not allowed:
                # Log security event
                from .security_logging import security_logger
                security_logger.log_rate_limit_violation(client_ip, endpoint_key, limit)

                logger.warning(f"Rate limit exceeded for {client_ip} on {endpoint_key}")
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Rate limit exceeded. Maximum {limit} requests per {window} seconds.",
                    headers={
                        "Retry-After": str(window),
                        "X-RateLimit-Limit": str(limit),
                        "X-RateLimit-Remaining": "0",
                        "X-RateLimit-Reset": str(int(time.time()) + window)
                    }
                )

            # Add rate limit headers to response
            response = await call_next(request)
            response.headers["X-RateLimit-Limit"] = str(limit)
            response.headers["X-RateLimit-Remaining"] = str(remaining)
            response.headers["X-RateLimit-Reset"] = str(int(time.time()) + window)
            return response

        # No rate limit for this endpoint
        return await call_next(request)

    def _get_client_ip(self, request: Request) -> str:
        """
        Get client IP address from request.

        Handles X-Forwarded-For header for proxy/load balancer setups.
        """
        # Check X-Forwarded-For header first (for proxied requests)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # Take the first IP (client IP)
            return forwarded_for.split(",")[0].strip()

        # Check X-Real-IP header
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        # Fall back to direct client IP
        if request.client:
            return request.client.host

        return "unknown"

    def _get_endpoint_key(self, path: str) -> str:
        """
        Get endpoint key for rate limiting.

        Maps request path to rate limit configuration.
        """
        for endpoint_pattern, _ in self.endpoint_limits.items():
            if path.startswith(endpoint_pattern):
                return endpoint_pattern
        return ""
