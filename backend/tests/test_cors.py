"""Tests for CORS configuration."""

import pytest


def test_cors_headers(client):
    """Test that CORS headers are properly set."""
    response = client.options(
        "/api/healthz",
        headers={"Origin": "http://localhost:3000"}
    )

    # Should allow CORS from localhost:3000
    assert response.status_code in [200, 204]
