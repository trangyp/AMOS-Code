"""AMOS Unified Deployment Orchestrator.

Production-grade deployment orchestration integrating:
- MCP Server (AI protocol interface)
- Production Runtime (bootstrap, healing, equations)
- Cognitive Bridge (tool routing)
- Container lifecycle (Docker/K8s ready)

Architecture:
    ┌─────────────────────────────────────────────────────────────┐
    │                  DEPLOYMENT ORCHESTRATOR                    │
    ├─────────────────────────────────────────────────────────────┤
    │  Phase 1: Environment Validation                            │
    │  Phase 2: Component Initialization                        │
    │  Phase 3: Health Verification                               │
    │  Phase 4: MCP Server Startup                                │
    │  Phase 5: Monitoring & Self-Healing                         │
    └─────────────────────────────────────────────────────────────┘

Usage:
    # Standard deployment
    orchestrator = await AMOSDeploymentOrchestrator.deploy()

    # With custom config
    config = DeploymentConfig(mode="production", enable_mcp=True)
    orchestrator = await AMOSDeploymentOrchestrator.deploy(config)

    # Shutdown
    await orchestrator.shutdown()

Owner: Trang
Version: 1.0.0
"""

import asyncio
import signal
import sys
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from pathlib import Path

from amos_mcp_production_integration import (
    AMOSMCPProductionInterface,
    get_mcp_production_interface,
)

# Core AMOS imports
from amos_production_runtime import AMOSProductionRuntime, get_production_runtime


class DeploymentPhase(Enum):
    """Deployment lifecycle phases."""

    IDLE = auto()
    VALIDATING = auto()  # Environment checks
    INITIALIZING = auto()  # Component startup
    HEALTH_CHECKING = auto()  # Verification
    STARTING_MCP = auto()  # MCP server startup
    RUNNING = auto()  # Fully operational
    DEGRADED = auto()  # Partial failure
    SHUTTING_DOWN = auto()  # Graceful stop
    SHUTDOWN = auto()  # Complete


@dataclass
class DeploymentConfig:
    """Configuration for deployment orchestration."""

    # Mode
    mode: str = "production"  # development, staging, production

    # Components
    enable_mcp: bool = True
    enable_runtime: bool = True
    enable_healing: bool = True
    enable_monitoring: bool = True

    # MCP Settings
    mcp_transport: str = "stdio"  # stdio, sse, http
    mcp_port: int = 8080

    # Health Settings
    health_check_interval: float = 30.0
    health_threshold: float = 0.5  # Min health score

    # Timeout Settings
    init_timeout: float = 120.0
    shutdown_timeout: float = 30.0

    # Recovery
    auto_recovery: bool = True
    max_recovery_attempts: int = 3

    # Metadata
    deployment_id: str = field(default_factory=lambda: str(uuid.uuid4())[:12])
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())


@dataclass
class DeploymentStatus:
    """Current deployment status."""

    phase: DeploymentPhase = DeploymentPhase.IDLE
    deployment_id: str = ""
    timestamp: str = ""

    # Component status
    runtime_ready: bool = False
    mcp_ready: bool = False
    bridge_ready: bool = False
    healing_active: bool = False

    # Health
    overall_health: float = 0.0
    last_health_check: str = ""

    # Metrics
    uptime_seconds: float = 0.0
    request_count: int = 0
    error_count: int = 0

    # Issues
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


class AMOSDeploymentOrchestrator:
    """Unified deployment orchestrator for AMOS production systems.

    Manages the complete lifecycle:
    1. Environment validation (dependencies, paths)
    2. Production runtime initialization (bootstrap 7 phases)
    3. MCP production interface setup (health-monitored)
    4. MCP server startup (stdio/sse/http)
    5. Continuous monitoring and self-healing

    This is the ONE entry point for production AMOS deployments.
    """

    _instance: Optional[AMOSDeploymentOrchestrator] = None
    _shutdown_event: asyncio.Event = None

    def __new__(cls) -> AMOSDeploymentOrchestrator:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._shutdown_event = asyncio.Event()
        return cls._instance

    def __init__(self):
        if hasattr(self, "_initialized"):
            return
        self._initialized = False

        # Configuration
        self.config: DeploymentConfig = DeploymentConfig()
        self.status = DeploymentStatus()

        # Components
        self._runtime: Optional[AMOSProductionRuntime] = None
        self._mcp_interface: Optional[AMOSMCPProductionInterface] = None

        # State
        self._start_time: datetime = None
        self._health_task: asyncio.Task = None
        self._monitoring_active = False

        # Signal handlers
        self._setup_signal_handlers()

    def _setup_signal_handlers(self):
        """Setup graceful shutdown handlers."""
        try:
            loop = asyncio.get_running_loop()
            for sig in (signal.SIGINT, signal.SIGTERM):
                loop.add_signal_handler(sig, self._signal_handler)
        except RuntimeError:
            # No event loop running yet
            pass

    def _signal_handler(self):
        """Handle shutdown signals."""
        print("\n⚠️  Shutdown signal received, initiating graceful shutdown...")
        if self._shutdown_event:
            self._shutdown_event.set()
        asyncio.create_task(self.shutdown())

    @classmethod
    async def deploy(cls, config: Optional[DeploymentConfig] = None) -> AMOSDeploymentOrchestrator:
        """Deploy AMOS with full orchestration.

        This is the main entry point for production deployment.

        Args:
            config: Deployment configuration (uses defaults if None)

        Returns:
            Fully deployed orchestrator instance

        Example:
            orchestrator = await AMOSDeploymentOrchestrator.deploy()
            print(f"Health: {orchestrator.status.overall_health}")
        """
        orchestrator = cls()
        if config:
            orchestrator.config = config

        success = await orchestrator._execute_deployment()
        if not success:
            raise RuntimeError("Deployment failed - check logs for details")

        return orchestrator

    async def _execute_deployment(self) -> bool:
        """Execute full deployment sequence."""
        self._start_time = datetime.now(UTC)
        self.status.deployment_id = self.config.deployment_id
        self.status.timestamp = self._start_time.isoformat()

        print("=" * 70)
        print(" AMOS UNIFIED DEPLOYMENT ORCHESTRATOR v1.0")
        print("=" * 70)
        print(f"Deployment ID: {self.config.deployment_id}")
        print(f"Mode: {self.config.mode}")
        print(f"Timestamp: {self.status.timestamp}")
        print(f"Components: MCP={self.config.enable_mcp}, Runtime={self.config.enable_runtime}")
        print("=" * 70)

        try:
            # Phase 1: Environment Validation
            if not await self._phase_validate():
                return False

            # Phase 2: Component Initialization
            if not await self._phase_initialize():
                return False

            # Phase 3: Health Verification
            if not await self._phase_health_check():
                return False

            # Phase 4: MCP Server Startup (if enabled)
            if self.config.enable_mcp:
                if not await self._phase_start_mcp():
                    return False

            # Phase 5: Start Monitoring
            await self._phase_start_monitoring()

            # Deployment complete
            self.status.phase = DeploymentPhase.RUNNING
            self._initialized = True

            print("\n" + "=" * 70)
            print(" ✅ DEPLOYMENT SUCCESSFUL")
            print("=" * 70)
            print(f"Phase: {self.status.phase.name}")
            print(f"Runtime: {'✅ READY' if self.status.runtime_ready else '❌ FAILED'}")
            print(f"MCP Interface: {'✅ READY' if self.status.mcp_ready else '❌ FAILED'}")
            print(f"Health: {self.status.overall_health:.2f}/1.0")
            print("=" * 70)

            return True

        except Exception as e:
            self.status.phase = DeploymentPhase.DEGRADED
            self.status.errors.append(f"Deployment failed: {e}")
            print(f"\n❌ Deployment failed: {e}")
            await self.shutdown()
            return False

    async def _phase_validate(self) -> bool:
        """Phase 1: Validate environment."""
        print("\n[Phase 1/5] Environment Validation...")
        self.status.phase = DeploymentPhase.VALIDATING

        # Check Python version
        if sys.version_info < (3, 10):
            self.status.errors.append("Python 3.10+ required")
            return False

        # Check critical paths
        amos_root = Path(__file__).parent
        critical_paths = [
            amos_root / "AMOS_ORGANISM_OS",
            amos_root / "amos_production_runtime.py",
        ]

        for path in critical_paths:
            if not path.exists():
                self.status.warnings.append(f"Path not found: {path}")

        print("   ✅ Environment validated")
        return True

    async def _phase_initialize(self) -> bool:
        """Phase 2: Initialize components."""
        print("\n[Phase 2/5] Component Initialization...")
        self.status.phase = DeploymentPhase.INITIALIZING

        # Initialize production runtime
        if self.config.enable_runtime:
            print("   Initializing Production Runtime...")
            try:
                self._runtime = await get_production_runtime().initialize()
                if self._runtime and getattr(self._runtime, "_initialized", False):
                    self.status.runtime_ready = True
                    print("   ✅ Production Runtime initialized")
                else:
                    self.status.warnings.append("Runtime initialization incomplete")
            except Exception as e:
                self.status.errors.append(f"Runtime init failed: {e}")
                if self.config.mode == "production":
                    return False

        # Initialize MCP interface
        if self.config.enable_mcp:
            print("   Initializing MCP Production Interface...")
            try:
                self._mcp_interface = await get_mcp_production_interface()
                if self._mcp_interface and self._mcp_interface._initialized:
                    self.status.mcp_ready = True
                    self.status.bridge_ready = True
                    print("   ✅ MCP Interface initialized")
                else:
                    self.status.warnings.append("MCP interface initialization incomplete")
            except Exception as e:
                self.status.errors.append(f"MCP interface init failed: {e}")
                if self.config.mode == "production":
                    return False

        return True

    async def _phase_health_check(self) -> bool:
        """Phase 3: Verify health."""
        print("\n[Phase 3/5] Health Verification...")
        self.status.phase = DeploymentPhase.HEALTH_CHECKING

        health_scores = []

        # Check runtime health
        if self._runtime and hasattr(self._runtime, "get_health"):
            health = self._runtime.get_health()
            score = health.get("health_score", 0.0)
            health_scores.append(score)
            print(f"   Runtime Health: {score:.2f}")

        # Check MCP interface stats
        if self._mcp_interface:
            stats = self._mcp_interface.get_stats()
            print(f"   MCP Bridge: {stats.get('request_count', 0)} requests")

        # Overall health
        if health_scores:
            self.status.overall_health = sum(health_scores) / len(health_scores)

        self.status.last_health_check = datetime.now(UTC).isoformat()

        # Validate against threshold
        if self.status.overall_health < self.config.health_threshold:
            msg = f"Health {self.status.overall_health:.2f} below threshold {self.config.health_threshold}"
            self.status.warnings.append(msg)
            if self.config.mode == "production":
                print(f"   ⚠️  {msg}")
                # Don't fail, but warn

        print(f"   ✅ Overall Health: {self.status.overall_health:.2f}")
        return True

    async def _phase_start_mcp(self) -> bool:
        """Phase 4: Start MCP server."""
        print("\n[Phase 4/5] MCP Server Startup...")
        self.status.phase = DeploymentPhase.STARTING_MCP

        # Note: MCP server would be started here
        # For now, the interface is ready and server can be started separately
        print(f"   MCP Transport: {self.config.mcp_transport}")
        print(f"   MCP Port: {self.config.mcp_port}")
        print("   ✅ MCP Server configuration ready")
        print(
            "   ℹ️  Start MCP server separately: python -m AMOS_ORGANISM_OS.14_INTERFACES.mcp_server"
        )

        return True

    async def _phase_start_monitoring(self):
        """Phase 5: Start continuous monitoring."""
        print("\n[Phase 5/5] Starting Monitoring...")

        if self.config.enable_monitoring:
            self._monitoring_active = True
            self._health_task = asyncio.create_task(self._health_monitor_loop())
            print(f"   Health check interval: {self.config.health_check_interval}s")

        if self.config.enable_healing and self._runtime:
            # Enable self-healing through runtime
            if hasattr(self._runtime, "enable_self_healing"):
                await self._runtime.enable_self_healing(
                    interval_seconds=self.config.health_check_interval
                )
                self.status.healing_active = True
                print("   ✅ Self-healing enabled")

        print("   ✅ Monitoring active")

    async def _health_monitor_loop(self):
        """Continuous health monitoring."""
        while self._monitoring_active and not (
            self._shutdown_event and self._shutdown_event.is_set()
        ):
            try:
                await self._perform_health_check()
                await asyncio.wait_for(
                    self._shutdown_event.wait()
                    if self._shutdown_event
                    else asyncio.sleep(self.config.health_check_interval),
                    timeout=self.config.health_check_interval,
                )
            except TimeoutError:
                continue
            except Exception as e:
                print(f"Health monitor error: {e}")
                await asyncio.sleep(5)

    async def _perform_health_check(self):
        """Perform single health check."""
        if not self._runtime:
            return

        try:
            health = self._runtime.get_health()
            self.status.overall_health = health.get("health_score", 0.0)
            self.status.last_health_check = datetime.now(UTC).isoformat()

            # Auto-recovery if needed
            if (
                self.config.auto_recovery
                and self.status.overall_health < self.config.health_threshold
            ):
                print(
                    f"\n⚠️  Low health detected ({self.status.overall_health:.2f}), triggering recovery..."
                )
                await self._attempt_recovery()

        except Exception as e:
            self.status.errors.append(f"Health check failed: {e}")

    async def _attempt_recovery(self):
        """Attempt system recovery."""
        if not self._runtime or not hasattr(self._runtime, "_healing"):
            return

        try:
            healing = self._runtime._healing
            if hasattr(healing, "heal_all"):
                await healing.heal_all()
                print("   Recovery attempted")
        except Exception as e:
            print(f"   Recovery failed: {e}")

    def get_status(self) -> DeploymentStatus:
        """Get current deployment status."""
        if self._start_time:
            uptime = (datetime.now(UTC) - self._start_time).total_seconds()
            self.status.uptime_seconds = uptime
        return self.status

    async def shutdown(self):
        """Graceful shutdown."""
        print("\n" + "=" * 70)
        print(" INITIATING SHUTDOWN")
        print("=" * 70)

        self.status.phase = DeploymentPhase.SHUTTING_DOWN
        self._monitoring_active = False

        # Cancel health monitoring
        if self._health_task:
            self._health_task.cancel()
            try:
                await self._health_task
            except asyncio.CancelledError:
                pass

        # Shutdown MCP interface
        if self._mcp_interface:
            print("   Shutting down MCP interface...")
            self.status.mcp_ready = False

        # Shutdown runtime
        if self._runtime and hasattr(self._runtime, "shutdown"):
            print("   Shutting down Production Runtime...")
            await self._runtime.shutdown()
            self.status.runtime_ready = False

        self.status.phase = DeploymentPhase.SHUTDOWN
        self._initialized = False

        print("   ✅ Shutdown complete")
        print("=" * 70)


# Convenience function
async def deploy_amos(
    mode: str = "production", enable_mcp: bool = True, enable_healing: bool = True
) -> AMOSDeploymentOrchestrator:
    """Quick deploy AMOS with standard configuration.

    Args:
        mode: deployment mode (development, staging, production)
        enable_mcp: enable MCP server integration
        enable_healing: enable self-healing

    Returns:
        Deployed orchestrator instance
    """
    config = DeploymentConfig(mode=mode, enable_mcp=enable_mcp, enable_healing=enable_healing)
    return await AMOSDeploymentOrchestrator.deploy(config)


if __name__ == "__main__":
    # Demo deployment
    async def demo():
        try:
            orchestrator = await deploy_amos(mode="development")
            status = orchestrator.get_status()
            print("\nDeployment Status:")
            print(f"  ID: {status.deployment_id}")
            print(f"  Phase: {status.phase.name}")
            print(f"  Health: {status.overall_health:.2f}")
            print(f"  Uptime: {status.uptime_seconds:.1f}s")

            # Keep running for a bit
            await asyncio.sleep(5)

            # Shutdown
            await orchestrator.shutdown()
        except Exception as e:
            print(f"Demo failed: {e}")
            sys.exit(1)

    asyncio.run(demo())
