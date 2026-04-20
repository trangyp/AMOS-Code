"""Error response contracts for AMOS API."""

from datetime import datetime, timezone

UTC = timezone.utc
from enum import Enum
from typing import Any

from amos_universe.contracts.pydantic.base import BaseAMOSModel

from pydantic import Field


class ErrorCode(str, Enum):
    """Standard error codes for AMOS API."""

    # General errors
    UNKNOWN = "unknown"
    VALIDATION_ERROR = "validation_error"
    INTERNAL_ERROR = "internal_error"
    NOT_IMPLEMENTED = "not_implemented"

    # Authentication/authorization
    UNAUTHENTICATED = "unauthenticated"
    PERMISSION_DENIED = "permission_denied"
    INVALID_CREDENTIALS = "invalid_credentials"
    TOKEN_EXPIRED = "token_expired"

    # Resources
    NOT_FOUND = "not_found"
    ALREADY_EXISTS = "already_exists"
    RESOURCE_EXHAUSTED = "resource_exhausted"

    # Rate limiting
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    QUOTA_EXCEEDED = "quota_exceeded"

    # Model/LLM errors
    MODEL_NOT_FOUND = "model_not_found"
    MODEL_NOT_LOADED = "model_not_loaded"
    MODEL_ERROR = "model_error"
    CONTEXT_LENGTH_EXCEEDED = "context_length_exceeded"

    # Repository errors
    REPO_NOT_FOUND = "repo_not_found"
    REPO_ACCESS_DENIED = "repo_access_denied"
    SCAN_FAILED = "scan_failed"
    FIX_FAILED = "fix_failed"

    # Brain/execution errors
    BRAIN_EXECUTION_FAILED = "brain_execution_failed"
    INVALID_STATE = "invalid_state"
    MORPH_FAILED = "morph_failed"
    EQUATION_FAILED = "equation_failed"


class ApiError(BaseAMOSModel):
    """Standard API error response.

    Example:
        {
            "error": {
                "code": "validation_error",
                "message": "Invalid request: 'message' field is required",
                "details": {"field": "message", "issue": "required"},
                "request_id": "req_abc123"
            }
        }
    """

    code: ErrorCode = Field(..., description="Error code")
    message: str = Field(..., description="Human-readable error message")
    details: dict[str, Any] | None = Field(None, description="Additional error details")
    request_id: str | None = Field(None, description="Request identifier for debugging")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), description="When the error occurred"
    )
    documentation_url: str | None = Field(None, description="URL to documentation about this error")


class ValidationError(ApiError):
    """Validation error with field-level details."""

    code: ErrorCode = Field(default=ErrorCode.VALIDATION_ERROR)
    field_errors: list[dict[str, Any]] = Field(
        default_factory=list, description="List of field-level validation errors"
    )


class AuthenticationError(ApiError):
    """Authentication failed error."""

    code: ErrorCode = Field(default=ErrorCode.UNAUTHENTICATED)


class NotFoundError(ApiError):
    """Resource not found error."""

    code: ErrorCode = Field(default=ErrorCode.NOT_FOUND)
    resource_type: str = Field(..., description="Type of resource not found")
    resource_id: str = Field(..., description="ID of resource not found")
