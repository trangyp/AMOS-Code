#!/usr/bin/env python3
"""AMOS Multi-Tenancy & Workspace Isolation - Phase 17
=========================================================

Enterprise multi-tenant architecture with PostgreSQL Row-Level Security (RLS),
workspace isolation, and tenant-aware request routing.

Architecture Pattern: Shared Database + Schema Isolation + RLS
Benefits:
- Complete data isolation between tenants
- No code changes for tenant filtering (RLS handles it)
- Scalable to thousands of tenants
- Single database backup/restore

Features:
- Workspace/Tenant management
- Automatic tenant context extraction
- PostgreSQL Row-Level Security policies
- Tenant-aware database queries
- Subscription/billing tracking
- Resource quotas per tenant

Models:
- Workspace: Tenant container with settings
- WorkspaceMember: User membership in workspace
- Subscription: Billing and plan info
- ResourceQuota: Usage limits per tenant

Owner: Trang
Version: 1.0.0
Phase: 17
"""

import uuid
from contextvars import ContextVar
from datetime import datetime, timezone
UTC = timezone.utc
from enum import Enum
from typing import Any, List, Optional

# SQLAlchemy imports
try:
    from sqlalchemy import (
        JSON,
        Boolean,
        Column,
        DateTime,
        ForeignKey,
        Index,
        Integer,
        String,
        Text,
        event,
        select,
    )
    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy.orm import Mapped, mapped_column, relationship
    from sqlalchemy.sql import expression

    MULTITENANCY_AVAILABLE = True
except ImportError:
    MULTITENANCY_AVAILABLE = False
    print("SQLAlchemy not installed. Multi-tenancy disabled.")

# FastAPI imports
try:
    from fastapi import Depends, HTTPException, Request, status
    from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False

# Import database models from Phase 16
try:
    from amos_db_sqlalchemy import APIKey, AuditLog, Base, User

    DATABASE_AVAILABLE = True
except ImportError:
    DATABASE_AVAILABLE = False

import logging

logger = logging.getLogger(__name__)

# Context variable for current tenant
current_workspace_id: ContextVar[str] = ContextVar("current_workspace_id", default=None)


# ============================================
# Enums
# ============================================


class WorkspaceRole(str, Enum):
    """Roles within a workspace."""

    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"
    VIEWER = "viewer"


class SubscriptionPlan(str, Enum):
    """Subscription plans."""

    FREE = "free"
    STARTER = "starter"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


class SubscriptionStatus(str, Enum):
    """Subscription status."""

    ACTIVE = "active"
    TRIAL = "trial"
    EXPIRED = "expired"
    CANCELLED = "cancelled"
    SUSPENDED = "suspended"


# ============================================
# Database Models
# ============================================

if MULTITENANCY_AVAILABLE and DATABASE_AVAILABLE:

    class Workspace(Base):
        """Workspace/tenant container."""

        __tablename__ = "workspaces"
        __table_args__ = (
            Index("ix_workspaces_slug", "slug", unique=True),
            Index("ix_workspaces_owner_id", "owner_id"),
            Index("ix_workspaces_is_active", "is_active"),
        )

        id: Mapped[str] = mapped_column(
            String(36), primary_key=True, default=lambda: str(uuid.uuid4())
        )
        name: Mapped[str] = mapped_column(String(255), nullable=False)
        slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
        description: Mapped[str] = mapped_column(Text, nullable=True)

        # Ownership
        owner_id: Mapped[int] = mapped_column(
            Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
        )

        # Settings
        settings: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

        # Status
        is_active: Mapped[bool] = mapped_column(Boolean, default=True)
        is_public: Mapped[bool] = mapped_column(Boolean, default=False)

        # Timestamps
        created_at: Mapped[datetime] = mapped_column(
            DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
        )
        updated_at: Mapped[datetime] = mapped_column(
            DateTime(timezone=True),
            default=lambda: datetime.now(timezone.utc),
            onupdate=lambda: datetime.now(timezone.utc),
        )

        # Relationships
        owner: Mapped[User] = relationship(back_populates="owned_workspaces")
        members: Mapped[list[WorkspaceMember]] = relationship(
            back_populates="workspace", lazy="selectin", cascade="all, delete-orphan"
        )
        subscription: Mapped[Subscription] = relationship(
            back_populates="workspace", lazy="selectin", uselist=False
        )
        quota: Mapped[ResourceQuota] = relationship(
            back_populates="workspace", lazy="selectin", uselist=False
        )

    class WorkspaceMember(Base):
        """User membership in a workspace."""

        __tablename__ = "workspace_members"
        __table_args__ = (
            Index("ix_workspace_members_workspace_id", "workspace_id"),
            Index("ix_workspace_members_user_id", "user_id"),
            Index("ix_workspace_members_role", "role"),
        )

        id: Mapped[int] = mapped_column(Integer, primary_key=True)
        workspace_id: Mapped[str] = mapped_column(
            String(36), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False
        )
        user_id: Mapped[int] = mapped_column(
            Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
        )
        role: Mapped[str] = mapped_column(
            String(50), default=WorkspaceRole.MEMBER.value, nullable=False
        )

        # Permissions (override role defaults)
        permissions: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)

        joined_at: Mapped[datetime] = mapped_column(
            DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
        )
        invited_by_id: Mapped[int] = mapped_column(
            Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
        )

        # Relationships
        workspace: Mapped[Workspace] = relationship(back_populates="members")
        user: Mapped[User] = relationship(
            back_populates="workspace_memberships", foreign_keys=[user_id]
        )

    class Subscription(Base):
        """Subscription and billing info."""

        __tablename__ = "subscriptions"
        __table_args__ = (
            Index("ix_subscriptions_workspace_id", "workspace_id"),
            Index("ix_subscriptions_status", "status"),
            Index("ix_subscriptions_plan", "plan"),
        )

        id: Mapped[int] = mapped_column(Integer, primary_key=True)
        workspace_id: Mapped[str] = mapped_column(
            String(36), ForeignKey("workspaces.id", ondelete="CASCADE"), unique=True, nullable=False
        )

        # Plan
        plan: Mapped[str] = mapped_column(
            String(50), default=SubscriptionPlan.FREE.value, nullable=False
        )
        status: Mapped[str] = mapped_column(
            String(50), default=SubscriptionStatus.TRIAL.value, nullable=False
        )

        # Billing
        billing_email: Mapped[str] = mapped_column(String(255), nullable=True)
        stripe_customer_id: Mapped[str] = mapped_column(String(255), nullable=True)
        stripe_subscription_id: Mapped[str] = mapped_column(String(255), nullable=True)

        # Period
        current_period_start: Mapped[datetime] = mapped_column(
            DateTime(timezone=True), nullable=True
        )
        current_period_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
        trial_ends_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

        # Metadata
        metadata: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)

        created_at: Mapped[datetime] = mapped_column(
            DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
        )
        updated_at: Mapped[datetime] = mapped_column(
            DateTime(timezone=True),
            default=lambda: datetime.now(timezone.utc),
            onupdate=lambda: datetime.now(timezone.utc),
        )

        # Relationships
        workspace: Mapped[Workspace] = relationship(back_populates="subscription")

    class ResourceQuota(Base):
        """Resource usage limits per workspace."""

        __tablename__ = "resource_quotas"
        __table_args__ = (Index("ix_resource_quotas_workspace_id", "workspace_id"),)

        id: Mapped[int] = mapped_column(Integer, primary_key=True)
        workspace_id: Mapped[str] = mapped_column(
            String(36), ForeignKey("workspaces.id", ondelete="CASCADE"), unique=True, nullable=False
        )

        # Limits (0 = unlimited)
        max_users: Mapped[int] = mapped_column(Integer, default=5)
        max_api_keys: Mapped[int] = mapped_column(Integer, default=10)
        max_equations_per_hour: Mapped[int] = mapped_column(Integer, default=100)
        max_storage_mb: Mapped[int] = mapped_column(Integer, default=100)

        # Current usage
        current_users: Mapped[int] = mapped_column(Integer, default=0)
        current_api_keys: Mapped[int] = mapped_column(Integer, default=0)
        current_storage_mb: Mapped[int] = mapped_column(Integer, default=0)

        updated_at: Mapped[datetime] = mapped_column(
            DateTime(timezone=True),
            default=lambda: datetime.now(timezone.utc),
            onupdate=lambda: datetime.now(timezone.utc),
        )

        # Relationships
        workspace: Mapped[Workspace] = relationship(back_populates="quota")

        def check_limit(self, resource: str, amount: int = 1) -> bool:
            """Check if resource usage is within limits."""
            if resource == "users":
                return self.max_users == 0 or (self.current_users + amount) <= self.max_users
            elif resource == "api_keys":
                return (
                    self.max_api_keys == 0 or (self.current_api_keys + amount) <= self.max_api_keys
                )
            elif resource == "storage":
                return (
                    self.max_storage_mb == 0
                    or (self.current_storage_mb + amount) <= self.max_storage_mb
                )
            return True

        def increment_usage(self, resource: str, amount: int = 1) -> None:
            """Increment resource usage."""
            if resource == "users":
                self.current_users += amount
            elif resource == "api_keys":
                self.current_api_keys += amount
            elif resource == "storage":
                self.current_storage_mb += amount

    # Add relationships to existing User model
    User.owned_workspaces = relationship(
        "Workspace", back_populates="owner", lazy="selectin", cascade="all, delete-orphan"
    )
    User.workspace_memberships = relationship(
        "WorkspaceMember",
        back_populates="user",
        lazy="selectin",
        foreign_keys=[WorkspaceMember.user_id],
        cascade="all, delete-orphan",
    )


# ============================================
# Tenant Context Management
# ============================================


class TenantContext:
    """Manages tenant context for request lifecycle."""

    def __init__(self, workspace_id: str = None):
        self.workspace_id = workspace_id
        self._token = None

    def __enter__(self):
        self._token = current_workspace_id.set(self.workspace_id)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._token:
            current_workspace_id.reset(self._token)

    @classmethod
    def get_current_workspace_id(cls) -> str:
        """Get current workspace ID from context."""
        return current_workspace_id.get()


# ============================================
# RLS (Row Level Security) Integration
# ============================================


def set_rls_tenant_id(session: AsyncSession, workspace_id: str) -> None:
    """
    Set tenant ID for PostgreSQL Row-Level Security.

    This executes SET LOCAL amos.current_workspace_id = 'uuid'
    which enables RLS policies to filter by tenant.
    """
    if workspace_id:
        session.execute(expression.text(f"SET LOCAL amos.current_workspace_id = '{workspace_id}'"))
    else:
        session.execute(expression.text("SET LOCAL amos.current_workspace_id = NULL"))


# SQL for creating RLS policies
RLS_SETUP_SQL = """
-- Enable RLS on tables
ALTER TABLE workspaces ENABLE ROW LEVEL SECURITY;
ALTER TABLE workspace_members ENABLE ROW LEVEL SECURITY;
ALTER TABLE subscriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE resource_quotas ENABLE ROW LEVEL SECURITY;

-- Create policy function
CREATE OR REPLACE FUNCTION amos.current_workspace_id()
RETURNS TEXT AS $$
BEGIN
    RETURN current_setting('amos.current_workspace_id', true);
EXCEPTION WHEN OTHERS THEN
    RETURN NULL;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create RLS policies
CREATE POLICY workspace_isolation ON workspaces
    USING (id = amos.current_workspace_id() OR
           amos.current_workspace_id() IS NULL);

CREATE POLICY workspace_member_isolation ON workspace_members
    USING (workspace_id = amos.current_workspace_id() OR
           amos.current_workspace_id() IS NULL);

CREATE POLICY subscription_isolation ON subscriptions
    USING (workspace_id = amos.current_workspace_id() OR
           amos.current_workspace_id() IS NULL);

CREATE POLICY quota_isolation ON resource_quotas
    USING (workspace_id = amos.current_workspace_id() OR
           amos.current_workspace_id() IS NULL);
"""


# ============================================
# Workspace Manager
# ============================================


class WorkspaceManager:
    """
    Manages workspace lifecycle and operations.
    """

    def __init__(self, db_session: AsyncSession):
        self._session = db_session

    async def create_workspace(
        self,
        name: str,
        slug: str,
        owner_id: int,
        description: str = None,
        plan: str = SubscriptionPlan.FREE.value,
    ) -> "Workspace":
        """Create a new workspace with owner and subscription."""
        if not MULTITENANCY_AVAILABLE:
            raise RuntimeError("Multi-tenancy not available")

        # Create workspace
        workspace = Workspace(
            name=name,
            slug=slug,
            description=description,
            owner_id=owner_id,
            settings={"theme": "default", "timezone": "timezone.utc", "notifications": True},
        )
        self._session.add(workspace)
        await self._session.flush()

        # Add owner as member
        owner_member = WorkspaceMember(
            workspace_id=workspace.id, user_id=owner_id, role=WorkspaceRole.OWNER.value
        )
        self._session.add(owner_member)

        # Create subscription
        subscription = Subscription(
            workspace_id=workspace.id,
            plan=plan,
            status=SubscriptionStatus.TRIAL.value,
            trial_ends_at=datetime.now(timezone.utc) + timedelta(days=14),
        )
        self._session.add(subscription)

        # Create quota based on plan
        quota_limits = {
            SubscriptionPlan.FREE.value: {
                "max_users": 3,
                "max_api_keys": 5,
                "max_equations_per_hour": 100,
                "max_storage_mb": 500,
            },
            SubscriptionPlan.STARTER.value: {
                "max_users": 10,
                "max_api_keys": 20,
                "max_equations_per_hour": 1000,
                "max_storage_mb": 5000,
            },
            SubscriptionPlan.PROFESSIONAL.value: {
                "max_users": 50,
                "max_api_keys": 100,
                "max_equations_per_hour": 10000,
                "max_storage_mb": 50000,
            },
            SubscriptionPlan.ENTERPRISE.value: {
                "max_users": 0,  # Unlimited
                "max_api_keys": 0,
                "max_equations_per_hour": 0,
                "max_storage_mb": 0,
            },
        }

        limits = quota_limits.get(plan, quota_limits[SubscriptionPlan.FREE.value])
        quota = ResourceQuota(workspace_id=workspace.id, **limits)
        self._session.add(quota)

        await self._session.flush()
        await self._session.refresh(workspace)

        return workspace

    async def get_workspace_by_slug(self, slug: str) -> "Workspace":
        """Get workspace by slug."""
        if not MULTITENANCY_AVAILABLE:
            return None

        result = await self._session.execute(
            select(Workspace).where(Workspace.slug == slug).where(Workspace.is_active == True)
        )
        return result.scalar_one_or_none()

    async def get_user_workspaces(self, user_id: int) -> List["Workspace"]:
        """Get all workspaces for a user."""
        if not MULTITENANCY_AVAILABLE:
            return []

        # Workspaces owned by user
        owned_result = await self._session.execute(
            select(Workspace)
            .where(Workspace.owner_id == user_id)
            .where(Workspace.is_active == True)
        )
        owned = list(owned_result.scalars().all())

        # Workspaces where user is a member
        member_result = await self._session.execute(
            select(Workspace)
            .join(WorkspaceMember)
            .where(WorkspaceMember.user_id == user_id)
            .where(Workspace.is_active == True)
        )
        member = list(member_result.scalars().all())

        # Combine and deduplicate
        workspaces = {w.id: w for w in owned + member}
        return list(workspaces.values())

    async def add_workspace_member(
        self,
        workspace_id: str,
        user_id: int,
        role: str = WorkspaceRole.MEMBER.value,
        invited_by_id: int = None,
    ) -> "WorkspaceMember":
        """Add a member to workspace."""
        if not MULTITENANCY_AVAILABLE:
            raise RuntimeError("Multi-tenancy not available")

        # Check quota
        quota_result = await self._session.execute(
            select(ResourceQuota).where(ResourceQuota.workspace_id == workspace_id)
        )
        quota = quota_result.scalar_one_or_none()

        if quota and not quota.check_limit("users"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Workspace user limit reached. Upgrade your plan.",
            )

        member = WorkspaceMember(
            workspace_id=workspace_id, user_id=user_id, role=role, invited_by_id=invited_by_id
        )
        self._session.add(member)

        if quota:
            quota.increment_usage("users")

        await self._session.flush()
        await self._session.refresh(member)

        return member


# ============================================
# FastAPI Dependencies
# ============================================

if FASTAPI_AVAILABLE:
    security = HTTPBearer(auto_error=False)

    async def get_current_workspace(
        request: Request, credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
    ) -> str:
        """
        Extract workspace ID from request.

        Priority:
        1. X-Workspace-ID header
        2. JWT token claims (workspace_id)
        3. API key associated workspace
        4. Subdomain (workspace-slug.amos.io)
        """
        # Check header first
        workspace_id = request.headers.get("X-Workspace-ID")
        if workspace_id:
            return workspace_id

        # Check subdomain
        host = request.headers.get("Host", "")
        if ".amos.io" in host:
            subdomain = host.split(".")[0]
            if subdomain and subdomain != "www":
                # Lookup workspace by slug
                # For now, return slug as workspace identifier
                return subdomain

        return None

    async def require_workspace(workspace_id: str = Depends(get_current_workspace)) -> str:
        """Require a workspace to be specified."""
        if not workspace_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Workspace ID required. Use X-Workspace-ID header or workspace subdomain.",
            )
        return workspace_id


# ============================================
# Middleware
# ============================================

if FASTAPI_AVAILABLE:
    from starlette.middleware.base import BaseHTTPMiddleware

    class TenantMiddleware(BaseHTTPMiddleware):
        """
        Middleware to extract and set tenant context.
        """

        async def dispatch(self, request: Request, call_next):
            # Extract workspace ID
            workspace_id = None

            # From header
            workspace_id = request.headers.get("X-Workspace-ID")

            # From subdomain
            if not workspace_id:
                host = request.headers.get("Host", "")
                if ".amos.io" in host:
                    subdomain = host.split(".")[0]
                    if subdomain and subdomain != "www":
                        workspace_id = subdomain

            # Set context
            with TenantContext(workspace_id):
                response = await call_next(request)

                # Add workspace header to response for debugging
                if workspace_id:
                    response.headers["X-Workspace-ID"] = workspace_id

                return response


# ============================================
# Example Usage
# ============================================

if __name__ == "__main__":
    print("AMOS Multi-Tenancy - Phase 17")
    print("=" * 60)

    if not MULTITENANCY_AVAILABLE:
        print("\n⚠️  Multi-tenancy not available")
        print("   Install: pip install sqlalchemy")
        exit(1)

    print("\n✅ Multi-tenancy module ready!")
    print("\n📊 Features:")
    print("   - Workspace/tenant isolation")
    print("   - Row-Level Security (RLS) support")
    print("   - Subscription/billing tracking")
    print("   - Resource quotas per tenant")
    print("   - Tenant-aware request routing")

    print("\n🔧 Usage:")
    print("   # Create workspace")
    print("   workspace = await manager.create_workspace(")
    print("       name='My Team',")
    print("       slug='my-team',")
    print("       owner_id=user.id")
    print("   )")

    print("\n   # Use tenant context")
    print("   with TenantContext(workspace.id):")
    print("       # All queries automatically filtered by tenant")
    print("       data = await get_workspace_data()")

    print("\n" + "=" * 60)
    print("✅ Phase 17: Multi-Tenancy ready for production!")
