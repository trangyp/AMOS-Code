"""AMOS SDK Exceptions.

Custom exception types for SDK error handling.
"""


class AmosError(Exception):
    """Base exception for AMOS SDK."""

    pass


class AuthenticationError(AmosError):
    """Raised when API authentication fails."""

    pass


class RateLimitError(AmosError):
    """Raised when rate limit is exceeded."""

    pass


class ServerError(AmosError):
    """Raised when server returns error."""

    pass


class ValidationError(AmosError):
    """Raised when request validation fails."""

    pass
