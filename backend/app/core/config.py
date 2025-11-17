"""Configuration settings for Arrakis MVP."""

import os
from functools import lru_cache
from typing import Optional
from pydantic import field_validator, Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with validation."""

    # Supabase
    supabase_url: str = Field(..., min_length=1, description="Supabase project URL")
    supabase_service_key: str = Field(..., min_length=1, description="Supabase service role key")

    # OpenAI (optional)
    openai_api_key: Optional[str] = Field(None, description="OpenAI API key")
    openai_model: str = Field(default="gpt-4o", description="OpenAI model to use")
    openai_web_tool: bool = Field(default=True, description="Enable web tool for OpenAI")

    # Perplexity AI (optional)
    perplexity_api_key: Optional[str] = Field(None, description="Perplexity AI API key")
    pplx_target_sites: int = Field(
        default=50,
        ge=1,
        le=100,
        description="Target number of websites for analysis"
    )

    # Application
    app_name: str = Field(default="Arrakis MVP", description="Application name")
    debug: bool = Field(default=False, description="Debug mode")
    cors_origins: list[str] = Field(
        default=["http://localhost:3000", "http://127.0.0.1:3000"],
        description="Allowed CORS origins"
    )

    # Rate limiting
    rate_limit_enabled: bool = Field(default=True, description="Enable rate limiting")
    rate_limit_requests: int = Field(default=100, ge=1, description="Requests per window")
    rate_limit_window: int = Field(default=60, ge=1, description="Rate limit window in seconds")

    # Database
    database_url: Optional[str] = Field(None, description="Database connection URL")

    @field_validator('supabase_url')
    @classmethod
    def validate_supabase_url(cls, v: str) -> str:
        """Validate Supabase URL format."""
        if not v.startswith('https://'):
            raise ValueError('Supabase URL must start with https://')
        return v

    @field_validator('cors_origins')
    @classmethod
    def validate_cors_origins(cls, v: list[str]) -> list[str]:
        """Validate CORS origins."""
        if not v:
            raise ValueError('At least one CORS origin must be specified')
        return v

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Ignore extra fields in .env


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.

    This function uses lru_cache to ensure settings are loaded once
    and reused throughout the application lifecycle.

    Returns:
        Settings: Application settings instance
    """
    return Settings()


# For backward compatibility and convenience
settings = get_settings()
