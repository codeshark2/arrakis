"""Client factories for external services."""

import os
import logging
from openai import OpenAI

logger = logging.getLogger(__name__)

_OPENAI_CLIENT = None

def get_openai_client():
    """Get or create OpenAI client singleton."""
    global _OPENAI_CLIENT
    if _OPENAI_CLIENT is not None:
        return _OPENAI_CLIENT

    key = os.getenv("OPENAI_API_KEY")
    if not key:
        logger.error("OPENAI_API_KEY is not set. AI Judge cannot run.")
        return None

    try:
        _OPENAI_CLIENT = OpenAI(api_key=key)  # modern init
        logger.info("OpenAI client initialized successfully")
        return _OPENAI_CLIENT
    except Exception as e:
        logger.exception(f"Failed to initialize OpenAI client: {e}")
        return None

def reset_openai_client():
    """Reset OpenAI client (useful for testing)."""
    global _OPENAI_CLIENT
    _OPENAI_CLIENT = None
