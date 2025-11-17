"""Health check API endpoints for Arrakis MVP."""

import logging
import os
from fastapi import APIRouter
from ..core.logging import metrics

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["health"])


@router.get("/healthz")
async def health_check():
    """Health check endpoint."""
    try:
        # Get current metrics
        current_metrics = metrics.get_metrics()

        from datetime import datetime
        current_time = datetime.utcnow().isoformat() + "Z"

        return {
            "ok": True,
            "status": "healthy",
            "metrics": current_metrics,
            "timestamp": current_time
        }

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        from datetime import datetime
        current_time = datetime.utcnow().isoformat() + "Z"

        # Don't expose internal error details
        return {
            "ok": False,
            "status": "unhealthy",
            "timestamp": current_time
        }


@router.get("/health/readiness")
async def readiness():
    """Readiness check for external service dependencies."""
    # Check if required services are configured (without exposing details)
    pplx_ok = bool(os.getenv("PERPLEXITY_API_KEY"))

    # Only return minimal status information
    # Don't expose which specific API keys are present/missing
    return {
        "status": "ready" if pplx_ok else "not_ready",
        "message": "Service is ready" if pplx_ok else "Service is not fully configured"
    }
