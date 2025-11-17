"""CORS configuration for Arrakis MVP."""

from fastapi.middleware.cors import CORSMiddleware
from .config import settings
import logging

logger = logging.getLogger(__name__)


def setup_cors(app):
    """
    Configure CORS middleware with security best practices.

    For production, ensure settings.cors_origins only includes trusted domains.
    """
    # Log CORS configuration on startup
    logger.info(f"Configuring CORS for origins: {settings.cors_origins}")

    # Allowed HTTP methods
    allowed_methods = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]

    # Allowed headers
    allowed_headers = [
        "Content-Type",
        "Authorization",
        "X-API-Key",
        "Accept",
        "Origin",
        "User-Agent",
        "DNT",
        "Cache-Control",
        "X-Requested-With"
    ]

    # Exposed headers (headers that browser can access)
    exposed_headers = [
        "X-RateLimit-Limit",
        "X-RateLimit-Remaining",
        "X-RateLimit-Reset",
        "Retry-After"
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=allowed_methods,
        allow_headers=allowed_headers,
        expose_headers=exposed_headers,
        max_age=600,  # Cache preflight requests for 10 minutes
    )
