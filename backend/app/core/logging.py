"""Logging configuration for Arrakis MVP."""

import time
import logging
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Logging middleware for request/response tracking."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        
        # Log request
        logger.info(f"Request: {request.method} {request.url.path}")
        
        # Process request
        response = await call_next(request)
        
        # Calculate duration
        duration = time.time() - start_time
        
        # Log response
        logger.info(
            f"Response: {request.method} {request.url.path} - "
            f"Status: {response.status_code} - Duration: {duration:.3f}s"
        )
        
        return response


# Metrics counters
class Metrics:
    """Simple metrics tracking."""
    
    def __init__(self):
        self.runs_enqueued = 0
        self.runs_completed = 0
        self.insights_written = 0
        self.judge_failures = 0
        self.fallback_used = 0
    
    def increment(self, metric: str):
        """Increment a metric counter."""
        if hasattr(self, metric):
            setattr(self, metric, getattr(self, metric) + 1)
    
    def get_metrics(self) -> dict:
        """Get current metrics."""
        return {
            "runs_enqueued": self.runs_enqueued,
            "runs_completed": self.runs_completed,
            "insights_written": self.insights_written,
            "judge_failures": self.judge_failures,
            "fallback_used": self.fallback_used,
        }


# Global metrics instance
metrics = Metrics()
