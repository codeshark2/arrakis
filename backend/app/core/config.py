"""Configuration settings for Arrakis MVP."""

import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # Supabase
    supabase_url: str
    supabase_service_key: str
    
    # OpenAI (optional)
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4o"
    openai_web_tool: bool = True
    
    # Perplexity AI (optional)
    perplexity_api_key: Optional[str] = None
    pplx_target_sites: int = 50  # Target 50 websites for comprehensive analysis
    
    # Application
    app_name: str = "Arrakis MVP"
    debug: bool = False
    cors_origins: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    # Database
    database_url: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
