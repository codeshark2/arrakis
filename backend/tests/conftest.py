"""Pytest configuration and fixtures."""

import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def mock_perplexity_response():
    """Mock Perplexity API response."""
    return {
        "total_sources_analyzed": 25,
        "content": "Test analysis content",
        "total_tokens_used": 1000,
        "crawled_content": [
            {
                "source": "https://example.com/article1",
                "content": "This is a positive article about the brand with great features.",
                "sentiment": "positive"
            },
            {
                "source": "https://example.com/article2",
                "content": "The brand offers excellent service and innovative solutions.",
                "sentiment": "positive"
            },
            {
                "source": "https://test.com/review",
                "content": "A neutral review of the brand's products and services.",
                "sentiment": "neutral"
            }
        ]
    }
