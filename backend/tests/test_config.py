"""Tests for configuration settings."""

import pytest
import os
from pydantic import ValidationError


def test_settings_requires_supabase():
    """Test that settings require Supabase configuration."""
    from app.core.config import Settings

    # Should raise validation error if required fields are missing
    with pytest.raises(ValidationError):
        Settings(
            supabase_url="",
            supabase_service_key=""
        )


def test_settings_defaults():
    """Test default configuration values."""
    from app.core.config import Settings

    # Create settings with minimal required fields
    settings = Settings(
        supabase_url="https://test.supabase.co",
        supabase_service_key="test_key"
    )

    assert settings.app_name == "Arrakis MVP"
    assert settings.debug is False
    assert "http://localhost:3000" in settings.cors_origins
    assert settings.openai_model == "gpt-4o"
    assert settings.pplx_target_sites == 50
