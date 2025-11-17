"""Security utilities for input validation and sanitization."""

import re
from typing import Optional
from fastapi import HTTPException, status


class InputValidator:
    """Input validation utilities to prevent injection attacks."""

    # Brand name pattern: alphanumeric, spaces, hyphens, underscores, max 100 chars
    BRAND_NAME_PATTERN = re.compile(r'^[a-zA-Z0-9\s\-_\.]{1,100}$')

    # Prompt pattern: allow most characters but limit length
    PROMPT_MAX_LENGTH = 2000

    # SQL identifier pattern (table names, column names)
    SQL_IDENTIFIER_PATTERN = re.compile(r'^[a-zA-Z_][a-zA-Z0-9_]{0,63}$')

    @staticmethod
    def validate_brand_name(brand_name: str) -> str:
        """
        Validate and sanitize brand name to prevent SQL injection.

        Args:
            brand_name: The brand name to validate

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

        brand_name = brand_name.strip()

        if not InputValidator.BRAND_NAME_PATTERN.match(brand_name):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Brand name contains invalid characters. Only alphanumeric characters, spaces, hyphens, underscores, and dots are allowed."
            )

        return brand_name

    @staticmethod
    def validate_prompt(prompt: str) -> str:
        """
        Validate and sanitize user prompt.

        Args:
            prompt: The user prompt to validate

        Returns:
            Sanitized prompt

        Raises:
            HTTPException: If validation fails
        """
        if not prompt or not prompt.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Prompt cannot be empty"
            )

        prompt = prompt.strip()

        if len(prompt) > InputValidator.PROMPT_MAX_LENGTH:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Prompt exceeds maximum length of {InputValidator.PROMPT_MAX_LENGTH} characters"
            )

        # Remove any null bytes
        prompt = prompt.replace('\x00', '')

        return prompt

    @staticmethod
    def validate_sql_identifier(identifier: str) -> str:
        """
        Validate SQL identifier (table/column name) to prevent injection.

        Args:
            identifier: SQL identifier to validate

        Returns:
            Validated identifier

        Raises:
            HTTPException: If validation fails
        """
        if not identifier or not InputValidator.SQL_IDENTIFIER_PATTERN.match(identifier):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid SQL identifier"
            )

        return identifier

    @staticmethod
    def sanitize_for_log(text: str, max_length: int = 200) -> str:
        """
        Sanitize text for safe logging (prevent log injection).

        Args:
            text: Text to sanitize
            max_length: Maximum length to log

        Returns:
            Sanitized text
        """
        if not text:
            return ""

        # Remove newlines and control characters
        sanitized = re.sub(r'[\r\n\t\x00-\x1f\x7f-\x9f]', ' ', text)

        # Truncate if too long
        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length] + "..."

        return sanitized


class RateLimitConfig:
    """Rate limiting configuration."""

    # Rate limits per minute
    ANALYZE_ENDPOINT_LIMIT = 10  # Max 10 analysis requests per minute per IP
    DASHBOARD_ENDPOINT_LIMIT = 60  # Max 60 dashboard requests per minute per IP

    # Cost limits
    MAX_AI_CALLS_PER_REQUEST = 20  # Maximum AI API calls per single request
    MAX_CONCURRENT_REQUESTS = 5  # Maximum concurrent requests per IP
