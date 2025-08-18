"""Middleware configuration for Arrakis MVP."""

from fastapi import FastAPI
from .logging import LoggingMiddleware


def setup_middleware(app: FastAPI):
    """Configure all middleware."""
    app.add_middleware(LoggingMiddleware)
