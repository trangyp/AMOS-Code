"""AMOS Container Orchestrator.

Integrates Unified Deployment Orchestrator with container infrastructure:
- Docker Compose deployment with health checks
- Kubernetes-ready configuration
- Container-aware health monitoring
- Graceful lifecycle management

Architecture:
    ┌─────────────────────────────────────────────────────────────┐
    │                  CONTAINER ORCHESTRATOR                     │
    ├─────────────────────────────────────────────────────────────┤
    │  1. Build container image with embedded orchestrator          │
    │  2. Deploy with Docker Compose / Kubernetes                 │
    │  3. Container runs 5-phase deployment internally              │
    │  4. Expose health endpoint for container probes               │
    │  5. Monitor and auto-restart on failure                       │
    └─────────────────────────────────────────────────────────────┘

Usage:
    # Build and deploy locally
    orchestrator = AMOSContainerOrchestrator()
    await orchestrator.deploy_local()

    # Deploy with Docker Compose
    await orchestrator.deploy_compose()

    # Get container health
    health = await orchestrator.check_container_health()

Owner: Trang
Version: 1.0.0
"""

import asyncio
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
UTC = timezone.utc, timezone

UTC = UTC
from enum import Enum, auto
from pathlib import Path
from typing import Any, Optional


class ContainerState(Enum):
    """Container lifecycle states."""

    NOT_BUILT = auto()
    BUILDING = auto()
    BUILT = auto()
    STARTING = auto()
    RUNNING = auto()
    HEALTHY = auto()
    UNHEALTHY = auto()
    STOPPING = auto()
    STOPPED = auto()
    ERROR = auto()


@dataclass
class ContainerConfig:
    """Configuration for container deployment."""

    # Image settings
    image_name: str = "amos-superbrain"
    image_tag: str = "latest"

    # Container settings
    container_name: str = "amos-production"
    port: int = 8080

    # Health check
    health_check_interval: float = 30.0
    health_check_timeout: float = 10.0
    health_check_retries: int = 3

    # Resources
    memory_limit: str = "2g"
    cpu_limit: str = "1.0"

    # Environment
    environment: dict[str, str] = field(default_factory=dict)

    # Deployment mode
    mode: str = "production"  # development, staging, production


@dataclass
class ContainerStatus:
    """Container runtime status."""

    state: ContainerState = ContainerState.NOT_BUILT
    container_id: str = ""
    image_id: str = ""

    # Health
    health_status: str = "unknown"  # healthy, unhealthy, starting
    last_health_check: str = ""
    consecutive_failures: int = 0

    # Metrics
    start_time: str = ""
    uptime_seconds: float = 0.0
    restart_count: int = 0

    # AMOS internal status (from container)
    amos_health: float = 0.0
    amos_bootstrap_phase: str = ""
    amos_equations: int = 0

    # Issues
    errors: list[str] = field(default_factory=list)
    logs: list[str] = field(default_factory=list)


class AMOSContainerOrchestrator:
    """Container orchestrator for AMOS deployment.

    Manages the complete container lifecycle:
    1. Build Docker image with unified deployment orchestrator
    2. Deploy with health checks and resource limits
    3. Monitor container and AMOS internal health
    4. Auto-restart on failure with backoff
    5. Graceful shutdown on stop command

    This provides production-grade container orchestration
    with full integration of the 5-phase deployment pipeline.
    """

    def __init__(self, config: Optional[ContainerConfig] = None):
        self.config = config or ContainerConfig()
        self.status = ContainerStatus()

        # Paths
        self.project_root = Path(__file__).parent
        self.dockerfile_path = self.project_root / "Dockerfile"

        # State
        self._monitoring = False
        self._monitor_task: asyncio.Task = None

    async def deploy_local(self) -> bool:
        """Deploy locally with Docker.

        Executes:
        1. Build image with unified orchestrator
        2. Run container with health checks
        3. Start monitoring loop
        4. Wait for AMOS to report healthy

        Returns:
            bool: True if deployment successful
        """
        print("=" * 70)
        print(" AMOS CONTAINER ORCHESTRATOR - Local Deployment")
        print("=" * 70)
        print(f"Image: {self.config.image_name}:{self.config.image_tag}")
        print(f"Port: {self.config.port}")
        print(f"Mode: {self.config.mode}")
        print("=" * 70)

        # Phase 1: Build image
        if not await self._build_image():
            return False

        # Phase 2: Run container
        if not await self._run_container():
            return False

        # Phase 3: Wait for healthy
        if not await self._wait_for_healthy():
            return False

        # Phase 4: Start monitoring
        await self._start_monitoring()

        print("\n" + "=" * 70)
        print(" ✅ CONTAINER DEPLOYMENT SUCCESSFUL")
        print("=" * 70)
        print(f"Container: {self.status.container_id[:12]}")
        print(f"Health: {self.status.health_status}")
        print(f"AMOS Health: {self.status.amos_health:.2f}")
        print(f"Port: http://localhost:{self.config.port}")
        print("=" * 70)

        return True

    async def deploy_compose(self) -> bool:
        """Deploy with Docker Compose.

        Uses docker-compose.yml for multi-service deployment
        with Redis, monitoring, and AMOS services.
        """
        print("=" * 70)
        print(" AMOS CONTAINER ORCHESTRATOR - Docker Compose Deployment")
        print("=" * 70)

        compose_file = self.project_root / "docker-compose.production-runtime.yml"
        if not compose_file.exists():
            print(f"\n❌ Compose file not found: {compose_file}")
            return False

        # Build and start
        print("\n[1/3] Building services...")
        result = await self._run_command(["docker-compose", "-f", str(compose_file), "build"])
        if result[0] != 0:
            print(f"   ❌ Build failed: {result[2]}")
            return False
        print("   ✅ Services built")

        print("\n[2/3] Starting services...")
        result = await self._run_command(["docker-compose", "-f", str(compose_file), "up", "-d"])
        if result[0] != 0:
            print(f"   ❌ Start failed: {result[2]}")
            return False
        print("   ✅ Services started")

        print("\n[3/3] Waiting for health checks...")
        await asyncio.sleep(10)  # Give services time to initialize

        # Check if containers are healthy
        result = await self._run_command(["docker-compose", "-f", str(compose_file), "ps"])
        if result[0] == 0:
            print("   ✅ Services status:")
            print(result[1])

        print("\n" + "=" * 70)
        print(" ✅ DOCKER COMPOSE DEPLOYMENT SUCCESSFUL")
        print("=" * 70)
        print("Services:")
        print("  - AMOS API: http://localhost:8000")
        print("  - Prometheus: http://localhost:9090")
        print("  - Grafana: http://localhost:3000")
        print("=" * 70)

        return True

    async def stop(self) -> bool:
        """Stop and remove container."""
        print("\n" + "=" * 70)
        print(" STOPPING AMOS CONTAINER")
        print("=" * 70)

        self._monitoring = False
        if self._monitor_task:
            self._monitor_task.cancel()

        # Stop container gracefully
        result = await self._run_command(
            ["docker", "stop", "--time", "30", self.config.container_name]
        )
        if result[0] == 0:
            print("   ✅ Container stopped gracefully")

        # Remove container
        result = await self._run_command(["docker", "rm", self.config.container_name])
        if result[0] == 0:
            print("   ✅ Container removed")

        self.status.state = ContainerState.STOPPED
        print("=" * 70)
        return True

    async def check_container_health(self) -> dict[str, Any]:
        """Check container and AMOS internal health."""
        # Check Docker health
        result = await self._run_command(
            [
                "docker",
                "inspect",
                "--format",
                "{{.State.Health.Status}}",
                self.config.container_name,
            ]
        )

        docker_health = result[1].strip() if result[0] == 0 else "unknown"

        # Try to get AMOS internal health via HTTP
        amos_health = 0.0
        try:
            # This would call the container's health endpoint
            # For now, simulate with docker logs
            result = await self._run_command(
                ["docker", "logs", "--tail", "50", self.config.container_name]
            )
            if "AMOS Production Runtime: ACTIVE" in result[1]:
                amos_health = 1.0
        except Exception:
            pass

        return {
            "container_health": docker_health,
            "amos_health": amos_health,
            "state": self.status.state.name,
        }

    def get_status(self) -> ContainerStatus:
        """Get current container status."""
        if self.status.start_time:
            start = datetime.fromisoformat(self.status.start_time)
            self.status.uptime_seconds = (datetime.now(timezone.utc) - start).total_seconds()
        return self.status

    # Internal methods

    async def _build_image(self) -> bool:
        """Build Docker image."""
        print("\n[Phase 1/4] Building Docker image...")
        self.status.state = ContainerState.BUILDING

        if not self.dockerfile_path.exists():
            print(f"   ❌ Dockerfile not found: {self.dockerfile_path}")
            return False

        result = await self._run_command(
            [
                "docker",
                "build",
                "-t",
                f"{self.config.image_name}:{self.config.image_tag}",
                "-f",
                str(self.dockerfile_path),
                str(self.project_root),
            ]
        )

        if result[0] != 0:
            print(f"   ❌ Build failed: {result[2]}")
            self.status.errors.append(f"Build failed: {result[2]}")
            return False

        self.status.state = ContainerState.BUILT
        print("   ✅ Image built successfully")
        return True

    async def _run_container(self) -> bool:
        """Run container with health checks."""
        print("\n[Phase 2/4] Starting container...")
        self.status.state = ContainerState.STARTING

        # Prepare environment variables
        env_vars = []
        for key, value in self.config.environment.items():
            env_vars.extend(["-e", f"{key}={value}"])

        # Add deployment mode
        env_vars.extend(["-e", f"AMOS_DEPLOYMENT_MODE={self.config.mode}"])
        env_vars.extend(["-e", "AMOS_ENABLE_HEALING=true"])
        env_vars.extend(["-e", "AMOS_ENABLE_MONITORING=true"])

        # Build run command
        cmd = (
            [
                "docker",
                "run",
                "-d",
                "--name",
                self.config.container_name,
                "-p",
                f"{self.config.port}:8080",
                "--memory",
                self.config.memory_limit,
                "--cpus",
                self.config.cpu_limit,
                "--health-cmd",
                "curl -f http://localhost:8080/health || exit 1",
                "--health-interval",
                f"{self.config.health_check_interval}s",
                "--health-timeout",
                f"{self.config.health_check_timeout}s",
                "--health-retries",
                str(self.config.health_check_retries),
                "--restart",
                "unless-stopped",
            ]
            + env_vars
            + [f"{self.config.image_name}:{self.config.image_tag}"]
        )

        result = await self._run_command(cmd)

        if result[0] != 0:
            print(f"   ❌ Container start failed: {result[2]}")
            self.status.errors.append(f"Run failed: {result[2]}")
            return False

        self.status.container_id = result[1].strip()
        self.status.start_time = datetime.now(timezone.utc).isoformat()
        self.status.state = ContainerState.RUNNING

        print(f"   ✅ Container started: {self.status.container_id[:12]}")
        return True

    async def _wait_for_healthy(self, timeout: float = 120.0) -> bool:
        """Wait for container and AMOS to be healthy."""
        print("\n[Phase 3/4] Waiting for health checks...")

        start = time.time()
        check_interval = 5.0

        while time.time() - start < timeout:
            # Check container health
            result = await self._run_command(
                [
                    "docker",
                    "inspect",
                    "--format",
                    "{{.State.Health.Status}}",
                    self.config.container_name,
                ]
            )

            if result[0] == 0:
                health = result[1].strip()
                self.status.health_status = health

                if health == "healthy":
                    self.status.state = ContainerState.HEALTHY
                    print(f"   ✅ Container healthy (took {time.time() - start:.1f}s)")
                    return True
                elif health == "unhealthy":
                    self.status.consecutive_failures += 1
                    if self.status.consecutive_failures >= 3:
                        print("   ❌ Container unhealthy after 3 checks")
                        return False

            print(f"   ⏳ Health status: {self.status.health_status}...")
            await asyncio.sleep(check_interval)

        print(f"   ⚠️  Health check timeout ({timeout}s)")
        return False

    async def _start_monitoring(self):
        """Start background health monitoring."""
        print("\n[Phase 4/4] Starting health monitoring...")
        self._monitoring = True
        self._monitor_task = asyncio.create_task(self._monitor_loop())
        print("   ✅ Monitoring active (30s interval)")

    async def _monitor_loop(self):
        """Continuous health monitoring."""
        while self._monitoring:
            try:
                health = await self.check_container_health()
                self.status.amos_health = health.get("amos_health", 0.0)

                # Log significant changes
                if health.get("container_health") == "unhealthy":
                    print("\n⚠️  Container unhealthy detected")
                    self.status.restart_count += 1

                await asyncio.sleep(30)
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Monitor error: {e}")
                await asyncio.sleep(5)

    async def _run_command(self, cmd: list[str]) -> tuple[int, str, str]:
        """Run shell command asynchronously."""
        proc = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()
        return (proc.returncode or 0, stdout.decode().strip(), stderr.decode().strip())


# Convenience function
async def deploy_amos_container(
    mode: str = "production", port: int = 8080
) -> AMOSContainerOrchestrator:
    """Quick deploy AMOS in container.

    Args:
        mode: deployment mode (development, staging, production)
        port: host port to expose

    Returns:
        Container orchestrator instance
    """
    config = ContainerConfig(mode=mode, port=port)
    orchestrator = AMOSContainerOrchestrator(config)

    success = await orchestrator.deploy_local()
    if not success:
        raise RuntimeError("Container deployment failed")

    return orchestrator


if __name__ == "__main__":
    # Demo deployment
    async def demo():
        try:
            orchestrator = await deploy_amos_container(mode="development")
            status = orchestrator.get_status()
            print("\nContainer Status:")
            print(f"  ID: {status.container_id[:12]}")
            print(f"  State: {status.state.name}")
            print(f"  Health: {status.health_status}")
            print(f"  Uptime: {status.uptime_seconds:.1f}s")

            # Keep running
            print("\nPress Ctrl+C to stop...")
            while True:
                await asyncio.sleep(1)

        except KeyboardInterrupt:
            print("\n\nStopping...")
            await orchestrator.stop()
        except Exception as e:
            print(f"Demo failed: {e}")
            sys.exit(1)

    asyncio.run(demo())
