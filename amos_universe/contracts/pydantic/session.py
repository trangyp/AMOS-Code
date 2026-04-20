"""Session and user management API contracts."""

from datetime import datetime, timezone

UTC = timezone.utc
from typing import Any

from amos_universe.contracts.pydantic.base import BaseAMOSModel

from pydantic import Field


class User(BaseAMOSModel):
    """User account information."""

    user_id: str = Field(..., description="Unique user identifier")
    email: str = Field(..., description="User email address")
    name: str = Field(None, description="User display name")
    avatar_url: str = Field(None, description="User avatar URL")
    is_admin: bool = Field(default=False, description="Whether user has admin rights")
    preferences: dict[str, Any] = Field(default_factory=dict, description="User preferences")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), description="When the user was created"
    )
    last_active_at: datetime = Field(None, description="Last activity timestamp")


class Workspace(BaseAMOSModel):
    """Workspace/tenant information."""

    workspace_id: str = Field(..., description="Unique workspace identifier")
    slug: str = Field(..., description="URL-friendly workspace identifier")
    name: str = Field(..., description="Workspace display name")
    description: str = Field(None, description="Workspace description")
    owner_id: str = Field(..., description="Workspace owner user ID")
    plan: str = Field(default="free", description="Subscription plan")
    settings: dict[str, Any] = Field(default_factory=dict, description="Workspace settings")
    quota: dict[str, int] = Field(
        default_factory=dict, description="Usage quotas (users, api_keys, etc)"
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When the workspace was created",
    )


class SessionContext(BaseAMOSModel):
    """Context for an API session."""

    session_id: str = Field(..., description="Unique session identifier")
    user_id: str = Field(None, description="Authenticated user ID")
    workspace_id: str = Field(None, description="Active workspace ID")
    api_key_id: str = Field(None, description="API key used for authentication")
    client_info: dict[str, Any] = Field(
        default_factory=dict, description="Client information (user_agent, ip, etc)"
    )
    permissions: list[str] = Field(default_factory=list, description="Granted permissions")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When the session was created",
    )
    expires_at: datetime = Field(None, description="Session expiration time")


class UserSession(BaseAMOSModel):
    """Full user session information."""

    session: SessionContext = Field(..., description="Session context")
    user: User = Field(None, description="User information")
    workspace: Workspace = Field(None, description="Active workspace")
    is_authenticated: bool = Field(
        default=False, description="Whether the session is authenticated"
    )
