"""AMOS Platform SDK Exceptions."""


class AMOSAPIError(Exception):
    """Base exception for AMOS API errors."""

    pass


class AMOSAuthenticationError(AMOSAPIError):
    """Authentication failed."""

    pass


class AMOSValidationError(AMOSAPIError):
    """Request validation failed."""

    pass


class AMOSNotFoundError(AMOSAPIError):
    """Resource not found."""

    pass


class AMOSRateLimitError(AMOSAPIError):
    """Rate limit exceeded."""

    pass
