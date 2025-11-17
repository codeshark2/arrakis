"""Middleware configuration for Arrakis MVP."""

from fastapi import FastAPI
from .logging import LoggingMiddleware
from .rate_limit import RateLimitMiddleware


def setup_middleware(app: FastAPI):
    """Configure all middleware."""
    # Add rate limiting middleware first (before logging)
    app.add_middleware(RateLimitMiddleware)

    # Add logging middleware
    app.add_middleware(LoggingMiddleware)
