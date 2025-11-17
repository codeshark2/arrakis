"""Authentication and authorization middleware."""

import os
import secrets
import hashlib
from typing import Optional
from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader
from ..core.config import settings

# API Key Header
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


class AuthManager:
    """Manages authentication and authorization."""

    def __init__(self):
        """Initialize auth manager."""
        # In production, store API keys in database with proper hashing
        # For now, use environment variable
        self.valid_api_keys = self._load_api_keys()

    def _load_api_keys(self) -> set:
        """
        Load valid API keys from environment or database.

        In production, this should:
        1. Load hashed API keys from database
        2. Support multiple users with different permissions
        3. Include rate limits per key
        4. Track key usage and expiration
        """
        api_keys = set()

        # Load from environment (for development)
        env_key = os.getenv("ARRAKIS_API_KEY")
        if env_key:
            # Hash the key for secure storage
            api_keys.add(self._hash_api_key(env_key))

        # If no keys configured, generate a warning
        if not api_keys:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning("No API keys configured! All authenticated endpoints will fail.")

        return api_keys

    @staticmethod
    def _hash_api_key(api_key: str) -> str:
        """Hash API key for secure storage."""
        return hashlib.sha256(api_key.encode()).hexdigest()

    def verify_api_key(self, api_key: Optional[str]) -> bool:
        """
        Verify if the provided API key is valid.

        Args:
            api_key: The API key to verify

        Returns:
            True if valid, False otherwise
        """
        if not api_key:
            return False

        hashed_key = self._hash_api_key(api_key)
        return hashed_key in self.valid_api_keys

    @staticmethod
    def generate_api_key() -> str:
        """
        Generate a new secure API key.

        Returns:
            A new random API key
        """
        # Generate 32 bytes (256 bits) of random data
        # Convert to hex string (64 characters)
        return secrets.token_urlsafe(32)


# Global auth manager instance
auth_manager = AuthManager()


async def verify_api_key_dependency(api_key: Optional[str] = Security(api_key_header)) -> str:
    """
    FastAPI dependency for API key verification.

    This can be used to protect endpoints:
    @router.get("/protected", dependencies=[Depends(verify_api_key_dependency)])

    Args:
        api_key: API key from request header

    Returns:
        The verified API key

    Raises:
        HTTPException: If API key is invalid or missing
    """
    if not api_key:
        from .security_logging import security_logger
        # Note: We can't get client_ip here without Request object
        security_logger.log_authentication_failure("unknown", "API key missing")

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key is required",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    if not auth_manager.verify_api_key(api_key):
        from .security_logging import security_logger
        security_logger.log_authentication_failure("unknown", "Invalid API key")

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    return api_key


# Optional: API key verification that doesn't require authentication
# Useful for gradual migration
async def optional_api_key_dependency(api_key: Optional[str] = Security(api_key_header)) -> Optional[str]:
    """
    Optional API key verification.

    Use this during migration period to allow both authenticated and unauthenticated requests.
    """
    if api_key and auth_manager.verify_api_key(api_key):
        return api_key
    return None
