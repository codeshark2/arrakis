"""Main FastAPI application for Arrakis MVP."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.config import settings
from .core.cors import setup_cors
from .core.middleware import setup_middleware
from .core.rate_limit import RateLimitMiddleware
from .api import health, analytics, dashboard

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="AI-Powered Brand Intelligence System",
    version="1.0.0",
    debug=settings.debug
)

# Setup middleware (logging, error handling, etc.)
setup_middleware(app)

# Add rate limiting middleware
app.add_middleware(RateLimitMiddleware)

# Setup CORS
setup_cors(app)

# Include API routes
app.include_router(health.router)
app.include_router(analytics.router)
app.include_router(dashboard.router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to Arrakis MVP",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/healthz"
    }


@app.get("/docs")
async def docs():
    """API documentation."""
    return {"message": "API documentation available at /docs"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
