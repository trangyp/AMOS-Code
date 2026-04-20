"""Base models for AMOS API contracts."""

from datetime import UTC, datetime, timezone

UTC = UTC
from pydantic import BaseModel, ConfigDict, Field


class BaseAMOSModel(BaseModel):
    """Base model for all AMOS API contracts.

    Provides common configuration:
    - forbid extra fields
    - validate assignments
    - json encoders for datetime
    """

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        json_encoders={
            datetime: lambda dt: dt.isoformat() if dt else None,
        },
    )


class TimestampsMixin(BaseModel):
    """Mixin for models that track creation/update timestamps."""

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="UTC timestamp when the record was created",
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="UTC timestamp when the record was last updated",
    )
