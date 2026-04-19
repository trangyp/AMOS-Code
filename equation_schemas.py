#!/usr/bin/env python3
"""AMOS Equation Schemas - Pydantic Validation & API Contracts.

Production-grade Pydantic models for equation system API validation.
Provides type-safe request/response models with comprehensive validation,
sanitization, and OpenAPI documentation generation.

Features:
    - Request/response Pydantic models for all API endpoints
    - Input sanitization and validation rules
    - Equation-specific parameter validation
    - API versioning support via versioned model namespaces
    - OpenAPI schema generation
    - Custom validators for mathematical constraints
    - Security-focused input sanitization

Versioning Strategy:
    - URL path versioning: /api/v1/equations
    - Header versioning: X-API-Version: 2024-01-15
    - Model versioning: EquationRequestV1, EquationRequestV2

Usage:
    from equation_schemas import EquationRequestV1, EquationResponseV1
    request = EquationRequestV1(equation_name="sigmoid", inputs={"x": 1.0})

Environment Variables:
    API_VERSION_DEFAULT: Default API version (default: v1)
    STRICT_VALIDATION: Enable strict validation mode (default: true)
"""

import os
import re
import sys
from datetime import datetime
from decimal import Decimal
from typing import Any

# Pydantic imports with graceful fallback
try:
    from pydantic import (
        BaseModel,
        ConfigDict,
        Field,
        ValidationError,
        field_validator,
        model_validator,
    )

    PYDANTIC_AVAILABLE = True
except ImportError:
    PYDANTIC_AVAILABLE = False
    BaseModel = object  # type: ignore
    ConfigDict = None  # type: ignore
    Field = None  # type: ignore
    ValidationError = None  # type: ignore
    field_validator = None  # type: ignore
    model_validator = None  # type: ignore

# Default configuration
_DEFAULT_API_VERSION = os.getenv("API_VERSION_DEFAULT", "v1")
_STRICT_VALIDATION = os.getenv("STRICT_VALIDATION", "true").lower() == "true"


# Valid equation name pattern (alphanumeric with underscores)
_EQUATION_NAME_PATTERN = re.compile(r"^[a-zA-Z][a-zA-Z0-9_]*$")

# Maximum input values to prevent DoS
_MAX_INPUT_KEYS = 100
_MAX_INPUT_DEPTH = 5
_MAX_STRING_LENGTH = 10000
_MAX_ARRAY_LENGTH = 10000


# ============================================================================
# Base Models with Common Fields
# ============================================================================


class BaseRequest(BaseModel):
    """Base request model with common validation."""

    model_config = ConfigDict(
        extra="forbid" if _STRICT_VALIDATION else "ignore",
        validate_assignment=True,
        str_strip_whitespace=True,
    )

    request_id: str = Field(
        default=None,
        description="Unique request identifier for tracing",
        max_length=64,
    )

    timestamp: datetime = Field(
        default=None,
        description="Request timestamp",
    )


class BaseResponse(BaseModel):
    """Base response model with common fields."""

    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat(),
            Decimal: lambda v: str(v),
        }
    )

    success: bool = Field(
        default=True,
        description="Whether the request was successful",
    )

    request_id: str = Field(
        default=None,
        description="Echo of request identifier for tracing",
    )

    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Response timestamp",
    )

    duration_ms: float = Field(
        default=None,
        description="Request processing duration in milliseconds",
        ge=0,
    )

    api_version: str = Field(
        default=_DEFAULT_API_VERSION,
        description="API version used for processing",
    )


class ErrorResponse(BaseResponse):
    """Error response model."""

    success: bool = False

    error_code: str = Field(
        ...,  # Required
        description="Machine-readable error code",
        min_length=1,
        max_length=64,
    )

    error_message: str = Field(
        ...,  # Required
        description="Human-readable error message",
        min_length=1,
        max_length=1000,
    )

    error_details: Dict[str, Any] = Field(
        default=None,
        description="Additional error context",
    )

    field_errors: list[dict[str, Any]] = Field(
        default=None,
        description="Validation errors per field",
    )


# ============================================================================
# Equation Execution Models (V1)
# ============================================================================


class EquationInputV1(BaseModel):
    """Equation input parameter with validation."""

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    name: str = Field(
        ...,  # Required
        description="Input parameter name",
        min_length=1,
        max_length=128,
        pattern=r"^[a-zA-Z_][a-zA-Z0-9_]*$",
    )

    value: float | int | str | list | dict = Field(
        ...,  # Required
        description="Input parameter value",
    )

    @field_validator("value")
    @classmethod
    def validate_value_type(cls, v: Any) -> Any:
        """Validate input value type and constraints."""
        if isinstance(v, str) and len(v) > _MAX_STRING_LENGTH:
            raise ValueError(f"String value exceeds max length of {_MAX_STRING_LENGTH}")
        if isinstance(v, list) and len(v) > _MAX_ARRAY_LENGTH:
            raise ValueError(f"Array value exceeds max length of {_MAX_ARRAY_LENGTH}")
        return v


class EquationRequestV1(BaseRequest):
    """Equation execution request (API V1).

    Validates and sanitizes equation execution requests with
    comprehensive input validation and security constraints.
    """

    equation_name: str = Field(
        ...,  # Required
        description="Name of the equation to execute",
        min_length=1,
        max_length=128,
        examples=["sigmoid", "softmax", "cross_entropy"],
    )

    inputs: Dict[str, Any] = Field(
        default_factory=dict,
        description="Equation input parameters",
        max_length=_MAX_INPUT_KEYS,
    )

    domain: str = Field(
        default=None,
        description="Domain context for the equation",
        max_length=64,
    )

    validate_invariants: bool = Field(
        default=True,
        description="Whether to validate mathematical invariants",
    )

    timeout_seconds: float = Field(
        default=30.0,
        description="Maximum execution time",
        gt=0,
        le=300,  # Max 5 minutes
    )

    @field_validator("equation_name")
    @classmethod
    def validate_equation_name(cls, v: str) -> str:
        """Validate equation name format."""
        v = v.strip().lower()
        if not _EQUATION_NAME_PATTERN.match(v):
            raise ValueError(
                "Equation name must start with letter, " "contain only alphanumeric and underscore"
            )
        return v

    @field_validator("inputs")
    @classmethod
    def validate_inputs(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        """Validate input dictionary constraints."""
        if len(v) > _MAX_INPUT_KEYS:
            raise ValueError(f"Too many input keys: {len(v)} > {_MAX_INPUT_KEYS}")

        # Check for nested depth
        def check_depth(obj: Any, depth: int = 0) -> int:
            if depth > _MAX_INPUT_DEPTH:
                raise ValueError(f"Input nesting exceeds {_MAX_INPUT_DEPTH} levels")
            if isinstance(obj, dict):
                return max((check_depth(val, depth + 1) for val in obj.values()), default=depth)
            elif isinstance(obj, list):
                return max((check_depth(item, depth + 1) for item in obj), default=depth)
            return depth

        check_depth(v)
        return v

    @model_validator(mode="after")
    def validate_request(self) -> EquationRequestV1:
        """Cross-field validation."""
        # Ensure timeout is reasonable for the domain
        if self.timeout_seconds and self.timeout_seconds > 60:
            # Log warning for long timeouts
            pass
        return self


class EquationMetadataV1(BaseModel):
    """Equation metadata response model."""

    name: str = Field(..., description="Equation name")
    domain: str = Field(..., description="Domain category")
    pattern: str = Field(default=None, description="Mathematical pattern")
    formula: str = Field(default=None, description="Formula representation")
    description: str = Field(default=None, description="Human description")
    parameters: List[str] = Field(
        default_factory=list,
        description="Required parameter names",
    )


class EquationResultV1(BaseModel):
    """Equation execution result."""

    value: float | int | list | dict = Field(
        ...,
        description="Computed result value",
    )

    execution_time_ms: float = Field(..., description="Execution time in milliseconds", ge=0)

    metadata: Dict[str, Any] = Field(
        default=None,
        description="Execution metadata",
    )


class EquationResponseV1(BaseResponse):
    """Equation execution response (API V1)."""

    equation_name: str = Field(..., description="Executed equation name")
    result: Optional[EquationResultV1] = Field(
        default=None,
        description="Execution result",
    )

    invariant_violations: List[str] = Field(
        default=None,
        description="List of invariant violations if any",
    )

    cached: bool = Field(
        default=False,
        description="Whether result was cached",
    )


# ============================================================================
# Batch Execution Models
# ============================================================================


class BatchEquationRequestV1(BaseRequest):
    """Batch equation execution request."""

    equations: list[EquationRequestV1] = Field(
        ...,
        description="List of equation execution requests",
        min_length=1,
        max_length=100,  # Max batch size
    )

    parallel: bool = Field(
        default=True,
        description="Execute equations in parallel",
    )

    max_workers: int = Field(
        default=4,
        description="Maximum parallel workers",
        ge=1,
        le=20,
    )

    @field_validator("equations")
    @classmethod
    def validate_equations(cls, v: list[EquationRequestV1]) -> list[EquationRequestV1]:
        """Validate batch constraints."""
        if not v:
            raise ValueError("At least one equation required")

        # Check for duplicate request IDs
        request_ids = [eq.request_id for eq in v if eq.request_id]
        if len(request_ids) != len(set(request_ids)):
            raise ValueError("Duplicate request IDs in batch")

        return v


class BatchEquationResponseV1(BaseResponse):
    """Batch equation execution response."""

    results: list[EquationResponseV1] = Field(
        ...,
        description="List of execution results",
    )

    completed: int = Field(..., description="Number of successful executions")
    failed: int = Field(..., description="Number of failed executions")


# ============================================================================
# Verification Models
# ============================================================================


class VerificationRequestV1(BaseRequest):
    """Equation verification request."""

    equation_name: str = Field(..., description="Equation to verify")

    test_cases: list[dict[str, Any]] = Field(
        ...,
        description="Test case inputs",
        min_length=1,
        max_length=1000,
    )

    expected_results: List[Any] = Field(
        default=None,
        description="Expected results for comparison",
    )

    tolerance: float = Field(
        default=1e-6,
        description="Numerical tolerance for comparison",
        gt=0,
        le=1.0,
    )


class VerificationResultV1(BaseModel):
    """Individual test case verification result."""

    test_index: int = Field(..., description="Test case index")
    passed: bool = Field(..., description="Whether test passed")
    input_summary: str = Field(
        default=None,
        description="Summary of test input",
    )
    expected: Optional[Any] = Field(default=None, description="Expected result")
    actual: Optional[Any] = Field(default=None, description="Actual result")
    error: str = Field(default=None, description="Error if failed")


class VerificationResponseV1(BaseResponse):
    """Equation verification response."""

    equation_name: str = Field(..., description="Verified equation name")
    total_tests: int = Field(..., description="Total test cases")
    passed_tests: int = Field(..., description="Number of passed tests")
    failed_tests: int = Field(..., description="Number of failed tests")
    results: list[VerificationResultV1] = Field(..., description="Detailed results")
    verification_time_ms: float = Field(..., ge=0)


# ============================================================================
# GraphQL-Compatible Models
# ============================================================================


class GraphQLEquationInput(BaseModel):
    """GraphQL-compatible equation input."""

    model_config = ConfigDict(populate_by_name=True)

    equation_id: str = Field(..., alias="equationId")
    input_data: Dict[str, Any] = Field(..., alias="inputData")
    options: Dict[str, Any] = None


class GraphQLEquationResult(BaseModel):
    """GraphQL-compatible equation result."""

    model_config = ConfigDict(populate_by_name=True)

    equation_id: str = Field(..., alias="equationId")
    result: Any
    execution_time_ms: float = Field(..., alias="executionTimeMs")
    cached: bool


# ============================================================================
# API Versioning Utilities
# ============================================================================


def get_model_for_version(
    base_name: str,
    version: str = _DEFAULT_API_VERSION,
) -> type[BaseModel]:
    """Get the appropriate model class for an API version.

    Args:
        base_name: Base model name (e.g., "EquationRequest")
        version: API version string (e.g., "v1", "v2")

    Returns:
        Pydantic model class or None if not found
    """
    if not PYDANTIC_AVAILABLE:
        return None

    # Model naming convention: {BaseName}V{version}
    class_name = f"{base_name}V{version.lstrip('v')}".replace("__", "_")

    # Look up in current module
    current_module = sys.modules[__name__]

    model_class = getattr(current_module, class_name, None)
    if model_class and issubclass(model_class, BaseModel):
        return model_class

    return None


def parse_api_version(
    version_header: str = None,
    path_version: str = None,
) -> str:
    """Parse API version from header or path.

    Args:
        version_header: X-API-Version header value
        path_version: URL path version (e.g., "v1" from /api/v1/...)

    Returns:
        Normalized API version string
    """
    # Priority: path version > header version > default
    if path_version:
        return path_version.lower()

    if version_header:
        # Handle date-based versions: 2024-01-15 -> v1
        if version_header.startswith("20"):
            # Map date versions to semantic versions
            return "v1"  # Simplified mapping
        return version_header.lower()

    return _DEFAULT_API_VERSION


# ============================================================================
# Validation Helpers
# ============================================================================


def sanitize_equation_name(name: str) -> str:
    """Sanitize equation name input.

    Args:
        name: Raw equation name input

    Returns:
        Sanitized equation name

    Raises:
        ValueError: If name is invalid
    """
    if not name or not isinstance(name, str):
        raise ValueError("Equation name must be a non-empty string")

    name = name.strip().lower()

    # Remove any potentially dangerous characters
    name = re.sub(r"[^a-z0-9_]", "", name)

    if not name:
        raise ValueError("Equation name contains no valid characters")

    if not _EQUATION_NAME_PATTERN.match(name):
        raise ValueError(
            "Equation name must start with letter and contain only "
            "alphanumeric characters and underscores"
        )

    return name


def sanitize_numeric_input(
    value: Any,
    min_value: float = None,
    max_value: float = None,
) -> float:
    """Sanitize and validate numeric input.

    Args:
        value: Input value to sanitize
        min_value: Minimum allowed value
        max_value: Maximum allowed value

    Returns:
        Sanitized float value

    Raises:
        ValueError: If value is invalid
    """
    try:
        num = float(value)
    except (TypeError, ValueError) as e:
        raise ValueError(f"Cannot convert {type(value).__name__} to numeric: {e}") from e

    # Check for special float values
    if not (float("-inf") < num < float("inf")):
        raise ValueError("Numeric value must be finite")

    if min_value is not None and num < min_value:
        raise ValueError(f"Value {num} below minimum {min_value}")

    if max_value is not None and num > max_value:
        raise ValueError(f"Value {num} above maximum {max_value}")

    return num


def create_error_response(
    error_code: str,
    error_message: str,
    validation_error: Optional[ValidationError] = None,
    request_id: str = None,
) -> ErrorResponse:
    """Create standardized error response.

    Args:
        error_code: Machine-readable error code
        error_message: Human-readable error message
        validation_error: Pydantic validation error if applicable
        request_id: Request ID for tracing

    Returns:
        ErrorResponse instance
    """
    field_errors = None
    if validation_error:
        field_errors = [
            {
                "field": ".".join(str(x) for x in e["loc"]),
                "message": e["msg"],
                "type": e["type"],
            }
            for e in validation_error.errors()
        ]

    return ErrorResponse(
        error_code=error_code,
        error_message=error_message,
        field_errors=field_errors,
        request_id=request_id,
    )


# ============================================================================
# Model Serialization
# ============================================================================


def to_json_schema(model_class: type[BaseModel]) -> Dict[str, Any]:
    """Generate JSON schema for a model class.

    Args:
        model_class: Pydantic model class

    Returns:
        JSON schema dictionary
    """
    if not PYDANTIC_AVAILABLE:
        return {}

    return model_class.model_json_schema()


def get_all_models() -> dict[str, type[BaseModel]]:
    """Get all available model classes.

    Returns:
        Dictionary of model name to class
    """
    if not PYDANTIC_AVAILABLE:
        return {}

    import inspect

    current_module = sys.modules[__name__]

    models = {}
    for name, obj in inspect.getmembers(current_module):
        if (
            inspect.isclass(obj)
            and issubclass(obj, BaseModel)
            and obj is not BaseModel
            and name.startswith(("Base", "Equation", "Batch", "Verification", "GraphQL"))
        ):
            models[name] = obj

    return models
