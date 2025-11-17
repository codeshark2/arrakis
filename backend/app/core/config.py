"""Configuration settings for Arrakis MVP."""

import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # Supabase
    supabase_url: str
    supabase_key: str  # Use anon key for RLS, not service key

    # Backward compatibility - map old env var to new one
    @property
    def supabase_service_key(self) -> str:
        """Deprecated: Use supabase_key instead."""
        return self.supabase_key

    # OpenAI (optional)
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4o"
    openai_web_tool: bool = True

    # Perplexity AI
    perplexity_api_key: Optional[str] = None
    pplx_target_sites: int = 25  # Target 25 websites for analysis

    # API Authentication
    arrakis_api_key: Optional[str] = None

    # Application
    app_name: str = "Arrakis MVP"
    debug: bool = False
    environment: str = "development"
    log_level: str = "INFO"
    cors_origins: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    # Database
    database_url: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
