"""Security event logging and monitoring."""

import logging
from typing import Dict, Any
from datetime import datetime
from collections import defaultdict
import json

logger = logging.getLogger(__name__)


class SecurityEventLogger:
    """Logger for security-related events."""

    def __init__(self):
        """Initialize security event logger."""
        self.events = defaultdict(int)  # Track event counts
        self.last_reset = datetime.utcnow()

    def log_authentication_failure(self, client_ip: str, reason: str):
        """Log failed authentication attempt."""
        logger.warning(
            f"Authentication failure from {client_ip}: {reason}",
            extra={
                "event_type": "auth_failure",
                "client_ip": client_ip,
                "reason": reason,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        self.events["auth_failures"] += 1

    def log_rate_limit_violation(self, client_ip: str, endpoint: str, limit: int):
        """Log rate limit violation."""
        logger.warning(
            f"Rate limit exceeded by {client_ip} on {endpoint} (limit: {limit})",
            extra={
                "event_type": "rate_limit_violation",
                "client_ip": client_ip,
                "endpoint": endpoint,
                "limit": limit,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        self.events["rate_limit_violations"] += 1

    def log_validation_error(self, client_ip: str, field: str, error: str):
        """Log input validation error."""
        logger.info(
            f"Validation error from {client_ip} on field '{field}': {error}",
            extra={
                "event_type": "validation_error",
                "client_ip": client_ip,
                "field": field,
                "error": error,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        self.events["validation_errors"] += 1

    def log_suspicious_activity(self, client_ip: str, activity: str, details: Dict[str, Any]):
        """Log suspicious activity."""
        logger.warning(
            f"Suspicious activity from {client_ip}: {activity}",
            extra={
                "event_type": "suspicious_activity",
                "client_ip": client_ip,
                "activity": activity,
                "details": json.dumps(details),
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        self.events["suspicious_activities"] += 1

    def log_api_key_usage(self, api_key_hash: str, endpoint: str):
        """Log API key usage for auditing."""
        logger.debug(
            f"API key {api_key_hash[:8]}... used for {endpoint}",
            extra={
                "event_type": "api_key_usage",
                "api_key_hash": api_key_hash[:8],  # Only log first 8 chars
                "endpoint": endpoint,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        self.events["api_key_uses"] += 1

    def log_database_error(self, operation: str, error: str):
        """Log database errors (without exposing sensitive data)."""
        logger.error(
            f"Database error during {operation}",
            extra={
                "event_type": "database_error",
                "operation": operation,
                "error_type": type(error).__name__,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        self.events["database_errors"] += 1

    def log_external_api_call(self, service: str, success: bool, response_time: float):
        """Log external API calls for monitoring."""
        logger.info(
            f"External API call to {service}: {'success' if success else 'failed'} ({response_time:.2f}s)",
            extra={
                "event_type": "external_api_call",
                "service": service,
                "success": success,
                "response_time": response_time,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        if success:
            self.events[f"api_success_{service}"] += 1
        else:
            self.events[f"api_failure_{service}"] += 1

    def get_statistics(self) -> Dict[str, Any]:
        """Get security event statistics."""
        uptime = (datetime.utcnow() - self.last_reset).total_seconds()
        return {
            "uptime_seconds": uptime,
            "events": dict(self.events),
            "timestamp": datetime.utcnow().isoformat()
        }

    def reset_statistics(self):
        """Reset event counters."""
        self.events.clear()
        self.last_reset = datetime.utcnow()
        logger.info("Security event statistics reset")


# Global security logger instance
security_logger = SecurityEventLogger()


def configure_security_logging():
    """
    Configure security logging format and handlers.

    This should be called during application startup.
    """
    # Configure logging format to include security context
    log_format = (
        '%(asctime)s - %(name)s - %(levelname)s - '
        '%(message)s [%(event_type)s]'
    )

    # In production, configure additional handlers:
    # - File handler for persistent logs
    # - Syslog handler for centralized logging
    # - Alert handler for critical security events

    logger.info("Security logging configured")


# Example usage in middleware or dependencies:
"""
from app.core.security_logging import security_logger

# In authentication dependency:
if not is_valid:
    security_logger.log_authentication_failure(client_ip, "Invalid API key")
    raise HTTPException(...)

# In rate limiting middleware:
if rate_exceeded:
    security_logger.log_rate_limit_violation(client_ip, endpoint, limit)
    raise HTTPException(...)

# In input validation:
try:
    validate_input(data)
except ValidationError as e:
    security_logger.log_validation_error(client_ip, field, str(e))
    raise
"""
