"""Tests for health check endpoints."""

import pytest


def test_health_check(client):
    """Test the health check endpoint."""
    response = client.get("/api/healthz")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_root_endpoint(client):
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Welcome to Arrakis MVP"
    assert data["version"] == "1.0.0"
    assert "/docs" in data["docs"]
