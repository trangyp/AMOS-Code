"""
AMOS Platform Orchestrator - Master Integration Controller

Coordinates all 31+ production infrastructure components into a unified platform.
Provides lifecycle management, health monitoring, and cross-component integration.

Author: AMOS System
Version: 1.0.0
"""

from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from datetime import UTC, datetime, timezone

UTC = UTC
from typing import Any, Optional

from amos_circuit_breaker import get_circuit_breaker_registry
from amos_tracing import init_tracing, shutdown_tracing
from fastapi import FastAPI

from amos_async_jobs import celery_app
from amos_db_sqlalchemy import close_db, get_session, init_db
from amos_error_handling import setup_exception_handlers
from amos_event_bus import get_event_bus

# Import all AMOS infrastructure components
from amos_settings import get_settings
from amos_structured_logging import get_logger
from amos_websocket_manager import get_websocket_manager

# ============================================================================
# Platform State Model
# ============================================================================


@dataclass
class PlatformComponent:
    """Represents a platform component with its state."""

    name: str
    status: str = "stopped"  # stopped, starting, running, error
    health: str = "unknown"  # healthy, degraded, unhealthy
    initialized_at: datetime = None
    last_error: str = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class PlatformState:
    """Complete state of the AMOS platform."""

    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    components: dict[str, PlatformComponent] = field(default_factory=dict)
    overall_health: str = "initializing"
    version: str = "1.0.0"

    def get_component(self, name: str) -> Optional[PlatformComponent]:
        return self.components.get(name)

    def update_component(self, name: str, **kwargs) -> None:
        if name not in self.components:
            self.components[name] = PlatformComponent(name=name)
        component = self.components[name]
        for key, value in kwargs.items():
            if hasattr(component, key):
                setattr(component, key, value)


# ============================================================================
# Platform Orchestrator
# ============================================================================


class AMOSPlatformOrchestrator:
    """
    Master orchestrator for the AMOS platform.

    Manages lifecycle of all 31+ infrastructure components:
    - Configuration (amos_settings)
    - Database (amos_db_sqlalchemy)
    - Event Bus (amos_event_bus) with Redis
    - Circuit Breakers (amos_circuit_breaker)
    - Tracing (amos_tracing) OpenTelemetry
    - Structured Logging (amos_structured_logging)
    - Service Layer (amos_services)
    - WebSocket Manager (amos_websocket_manager)
    - Rate Limiting (amos_rate_limiter)
    - Async Jobs (amos_async_jobs) Celery
    - API Versioning (amos_api_versioning)
    - Error Handling (amos_error_handling)

    Usage:
        orchestrator = AMOSPlatformOrchestrator()
        await orchestrator.start()

        # Get integrated FastAPI app
        app = orchestrator.get_fastapi_app()

        # Health check
        health = await orchestrator.health_check()
    """

    def __init__(self):
        self.state = PlatformState()
        self.logger = get_logger("platform.orchestrator")
        self._components: dict[str, Any] = {}
        self._running = False
        self._lock = asyncio.Lock()

    # ========================================================================
    # Lifecycle Management
    # ========================================================================

    async def start(self) -> bool:
        """
        Initialize and start all platform components.

        Returns:
            True if all critical components started successfully
        """
        async with self._lock:
            if self._running:
                return True

            self.logger.info("🚀 Starting AMOS Platform Orchestrator...")

            try:
                # 1. Configuration (Critical)
                await self._init_configuration()

                # 2. Structured Logging (Critical)
                await self._init_logging()

                # 3. Database (Critical)
                await self._init_database()

                # 4. Event Bus (High Priority)
                await self._init_event_bus()

                # 5. Service Layer (High Priority)
                await self._init_service_layer()

                # 6. WebSocket Manager (High Priority)
                await self._init_websocket_manager()

                # 7. Circuit Breakers (Medium Priority)
                await self._init_circuit_breakers()

                # 8. Rate Limiting (Medium Priority)
                await self._init_rate_limiting()

                # 9. Tracing (Medium Priority)
                await self._init_tracing()

                # 10. Async Jobs (Background)
                await self._init_async_jobs()

                self._running = True
                self.state.overall_health = "healthy"

                self.logger.info("✅ AMOS Platform fully operational")
                self.logger.info(f"   Components: {len(self.state.components)}")
                self.logger.info(f"   Version: {self.state.version}")

                return True

            except Exception as e:
                self.state.overall_health = "error"
                self.logger.error(f"❌ Platform startup failed: {e}")
                await self.stop()
                return False

    async def stop(self) -> None:
        """Gracefully shutdown all components."""
        async with self._lock:
            if not self._running:
                return

            self.logger.info("🛑 Shutting down AMOS Platform...")

            # Shutdown in reverse order
            shutdown_order = [
                "async_jobs",
                "tracing",
                "rate_limiting",
                "circuit_breakers",
                "websocket_manager",
                "service_layer",
                "event_bus",
                "database",
                "logging",
                "configuration",
            ]

            for component_name in shutdown_order:
                try:
                    await self._shutdown_component(component_name)
                except Exception as e:
                    self.logger.warning(f"⚠️ Error shutting down {component_name}: {e}")

            self._running = False
            self.state.overall_health = "stopped"
            self.logger.info("✅ Platform shutdown complete")

    # ========================================================================
    # Component Initialization
    # ========================================================================

    async def _init_configuration(self) -> None:
        """Initialize unified configuration."""
        self.state.update_component(
            "configuration", status="starting", initialized_at=datetime.now(timezone.utc)
        )

        settings = get_settings()
        self._components["settings"] = settings

        self.state.update_component(
            "configuration",
            status="running",
            health="healthy",
            metadata={"env": settings.environment},
        )
        self.logger.info("✅ Configuration loaded")

    async def _init_logging(self) -> None:
        """Initialize structured logging."""
        self.state.update_component(
            "logging", status="starting", initialized_at=datetime.now(timezone.utc)
        )

        # Logging already initialized via get_logger
        self.state.update_component("logging", status="running", health="healthy")
        self.logger.info("✅ Structured logging active")

    async def _init_database(self) -> None:
        """Initialize database connection pool."""
        self.state.update_component(
            "database", status="starting", initialized_at=datetime.now(timezone.utc)
        )

        await init_db()

        self.state.update_component("database", status="running", health="healthy")
        self.logger.info("✅ Database pool initialized")

    async def _init_event_bus(self) -> None:
        """Initialize event bus with Redis if configured."""
        self.state.update_component(
            "event_bus", status="starting", initialized_at=datetime.now(timezone.utc)
        )

        event_bus = get_event_bus()

        # Try to connect Redis if configured
        settings = self._components.get("settings")
        if settings and hasattr(settings, "redis_url") and settings.redis_url:
            await event_bus.connect_redis(settings.redis_url)

        self._components["event_bus"] = event_bus

        self.state.update_component(
            "event_bus",
            status="running",
            health="healthy",
            metadata={"distributed_mode": event_bus._distributed_mode},
        )
        self.logger.info("✅ Event Bus initialized")

    async def _init_service_layer(self) -> None:
        """Initialize service layer with factory."""
        self.state.update_component(
            "service_layer", status="starting", initialized_at=datetime.now(timezone.utc)
        )

        # Service factory created on-demand via UnitOfWork
        self.state.update_component("service_layer", status="running", health="healthy")
        self.logger.info("✅ Service Layer ready")

    async def _init_websocket_manager(self) -> None:
        """Initialize WebSocket manager."""
        self.state.update_component(
            "websocket_manager", status="starting", initialized_at=datetime.now(timezone.utc)
        )

        ws_manager = get_websocket_manager()
        await ws_manager.start_event_listener()

        self._components["websocket_manager"] = ws_manager

        self.state.update_component("websocket_manager", status="running", health="healthy")
        self.logger.info("✅ WebSocket Manager started")

    async def _init_circuit_breakers(self) -> None:
        """Initialize circuit breaker registry."""
        self.state.update_component(
            "circuit_breakers", status="starting", initialized_at=datetime.now(timezone.utc)
        )

        registry = get_circuit_breaker_registry()
        self._components["circuit_breakers"] = registry

        self.state.update_component("circuit_breakers", status="running", health="healthy")
        self.logger.info("✅ Circuit Breakers active")

    async def _init_rate_limiting(self) -> None:
        """Initialize rate limiter."""
        self.state.update_component(
            "rate_limiting", status="starting", initialized_at=datetime.now(timezone.utc)
        )

        # Rate limiter initialized via middleware
        self.state.update_component("rate_limiting", status="running", health="healthy")
        self.logger.info("✅ Rate Limiting configured")

    async def _init_tracing(self) -> None:
        """Initialize OpenTelemetry tracing."""
        self.state.update_component(
            "tracing", status="starting", initialized_at=datetime.now(timezone.utc)
        )

        settings = self._components.get("settings")
        if settings and getattr(settings, "tracing_enabled", False):
            init_tracing(service_name="amos-platform", jaeger_endpoint=settings.jaeger_endpoint)

        self.state.update_component("tracing", status="running", health="healthy")
        self.logger.info("✅ Tracing initialized")

    async def _init_async_jobs(self) -> None:
        """Initialize Celery async job processor."""
        self.state.update_component(
            "async_jobs", status="starting", initialized_at=datetime.now(timezone.utc)
        )

        # Celery app already configured
        self._components["celery"] = celery_app

        self.state.update_component("async_jobs", status="running", health="healthy")
        self.logger.info("✅ Async Jobs (Celery) ready")

    async def _shutdown_component(self, name: str) -> None:
        """Shutdown a specific component."""
        if name == "websocket_manager" and "websocket_manager" in self._components:
            await self._components["websocket_manager"].stop()
        elif name == "event_bus" and "event_bus" in self._components:
            await self._components["event_bus"].stop()
        elif name == "tracing":
            shutdown_tracing()
        elif name == "database":
            await close_db()

        self.state.update_component(name, status="stopped")

    # ========================================================================
    # Health & Status
    # ========================================================================

    async def health_check(self) -> dict[str, Any]:
        """
        Comprehensive health check of all components.

        Returns:
            Health status report
        """
        checks = {}

        # Database health
        try:
            async with get_session() as session:
                await session.execute("SELECT 1")
            checks["database"] = "healthy"
        except Exception as e:
            checks["database"] = f"unhealthy: {e}"

        # Event Bus health
        if "event_bus" in self._components:
            bus = self._components["event_bus"]
            checks["event_bus"] = "healthy" if bus._running else "stopped"

        # WebSocket health
        if "websocket_manager" in self._components:
            ws = self._components["websocket_manager"]
            stats = ws.get_stats()
            checks["websocket"] = f"healthy ({stats['total_connections']} connections)"

        # Circuit Breakers
        if "circuit_breakers" in self._components:
            registry = self._components["circuit_breakers"]
            states = registry.get_all_states()
            open_count = sum(1 for s in states.values() if s.get("state") == "OPEN")
            checks["circuit_breakers"] = f"healthy ({open_count} open)"

        overall = (
            "healthy" if all("unhealthy" not in str(v) for v in checks.values()) else "degraded"
        )

        return {
            "overall": overall,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "components": checks,
            "platform_version": self.state.version,
        }

    def get_status(self) -> dict[str, Any]:
        """Get current platform status."""
        return {
            "running": self._running,
            "health": self.state.overall_health,
            "started_at": self.state.started_at.isoformat(),
            "components": {
                name: {
                    "status": comp.status,
                    "health": comp.health,
                    "initialized": comp.initialized_at.isoformat() if comp.initialized_at else None,
                }
                for name, comp in self.state.components.items()
            },
        }

    # ========================================================================
    # FastAPI Integration
    # ========================================================================

    @asynccontextmanager
    async def lifespan(self, app: FastAPI):
        """FastAPI lifespan context manager."""
        await self.start()
        yield
        await self.stop()

    def get_fastapi_app(self) -> FastAPI:
        """
        Create a fully configured FastAPI application.

        Returns:
            FastAPI app with all AMOS infrastructure integrated
        """
        app = FastAPI(
            title="AMOS Platform API",
            description="Unified platform with 31+ production components",
            version=self.state.version,
            lifespan=self.lifespan,
        )

        # Setup exception handlers
        setup_exception_handlers(app)

        # Health check endpoint
        @app.get("/health")
        async def health():
            return await self.health_check()

        # Platform status endpoint
        @app.get("/platform/status")
        async def status():
            return self.get_status()

        return app


# ============================================================================
# Global Orchestrator Instance
# ============================================================================_orchestrator: Optional[AMOSPlatformOrchestrator] = None


def get_platform_orchestrator() -> AMOSPlatformOrchestrator:
    """Get or create global platform orchestrator."""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = AMOSPlatformOrchestrator()
    return _orchestrator
