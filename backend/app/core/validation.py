"""Input validation and sanitization utilities."""

import re
from typing import Any
from fastapi import HTTPException, status


class InputValidator:
    """Utility class for input validation and sanitization."""

    # Maximum lengths for various inputs
    MAX_PROMPT_LENGTH = 2000
    MAX_BRAND_NAME_LENGTH = 200

    # Patterns for validation
    SAFE_TEXT_PATTERN = re.compile(r'^[a-zA-Z0-9\s\.,!?\-\'"()]+$')
    SQL_INJECTION_PATTERNS = [
        r'(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|EXECUTE)\b)',
        r'(--|#|/\*|\*/)',
        r'(\bOR\b.*=.*)',
        r'(\bAND\b.*=.*)',
        r"(';|\"--)",
    ]

    @classmethod
    def sanitize_prompt(cls, prompt: str) -> str:
        """
        Sanitize and validate prompt input.

        Args:
            prompt: User input prompt

        Returns:
            Sanitized prompt string

        Raises:
            HTTPException: If validation fails
        """
        if not prompt or not prompt.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Prompt cannot be empty"
            )

        # Remove leading/trailing whitespace
        prompt = prompt.strip()

        # Check length
        if len(prompt) > cls.MAX_PROMPT_LENGTH:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Prompt too long. Maximum length is {cls.MAX_PROMPT_LENGTH} characters"
            )

        # Check for SQL injection patterns
        for pattern in cls.SQL_INJECTION_PATTERNS:
            if re.search(pattern, prompt, re.IGNORECASE):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid characters detected in prompt"
                )

        # Remove potentially dangerous characters while preserving normal punctuation
        # Allow: letters, numbers, spaces, and common punctuation
        sanitized = re.sub(r'[<>{}[\]\\]', '', prompt)

        return sanitized

    @classmethod
    def sanitize_brand_name(cls, brand_name: str) -> str:
        """
        Sanitize and validate brand name.

        Args:
            brand_name: Brand name input

        Returns:
            Sanitized brand name

        Raises:
            HTTPException: If validation fails
        """
        if not brand_name or not brand_name.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Brand name cannot be empty"
            )

        # Remove leading/trailing whitespace
        brand_name = brand_name.strip()

        # Check length
        if len(brand_name) > cls.MAX_BRAND_NAME_LENGTH:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Brand name too long. Maximum length is {cls.MAX_BRAND_NAME_LENGTH} characters"
            )

        # Remove all special characters except spaces, hyphens, and apostrophes
        sanitized = re.sub(r'[^a-zA-Z0-9\s\-\']', '', brand_name)

        # Remove multiple consecutive spaces
        sanitized = re.sub(r'\s+', ' ', sanitized)

        if not sanitized:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Brand name contains only invalid characters"
            )

        return sanitized

    @classmethod
    def validate_integer(
        cls,
        value: Any,
        min_value: int = None,
        max_value: int = None,
        field_name: str = "value"
    ) -> int:
        """
        Validate integer input with optional range checking.

        Args:
            value: Value to validate
            min_value: Minimum allowed value (inclusive)
            max_value: Maximum allowed value (inclusive)
            field_name: Name of field for error messages

        Returns:
            Validated integer

        Raises:
            HTTPException: If validation fails
        """
        try:
            int_value = int(value)
        except (ValueError, TypeError):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"{field_name} must be a valid integer"
            )

        if min_value is not None and int_value < min_value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"{field_name} must be at least {min_value}"
            )

        if max_value is not None and int_value > max_value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"{field_name} must be at most {max_value}"
            )

        return int_value
