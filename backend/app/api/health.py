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
        
        return {
            "ok": True,
            "status": "healthy",
            "metrics": current_metrics,
            "timestamp": "2024-01-01T00:00:00Z"
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "ok": False,
            "status": "unhealthy",
            "error": str(e),
            "timestamp": "2024-01-01T00:00:00Z"
        }


@router.get("/health/readiness")
async def readiness():
    """Readiness check for external service dependencies."""
    openai_ok = bool(os.getenv("OPENAI_API_KEY"))
    pplx_ok = bool(os.getenv("PERPLEXITY_API_KEY"))
    target_sites = int(os.getenv("PPLX_TARGET_SITES", "50"))
    
    return {
        "openai_key_present": openai_ok,
        "perplexity_key_present": pplx_ok,
        "target_sites": target_sites,
        "status": "ready" if openai_ok and pplx_ok else "degraded"
    }
