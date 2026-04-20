#!/usr/bin/env python3
"""AMOS Docker Entrypoint Script.

Production entrypoint for Docker containers using Unified Deployment Orchestrator.
Replaces legacy CMD with 5-phase deployment pipeline.

Usage (in Dockerfile):
    ENTRYPOINT ["python3", "docker_entrypoint.py"]
    CMD ["production"]

Phases:
    1. Environment validation
    2. Component initialization (Runtime, MCP, Healing)
    3. Health verification
    4. MCP server startup
    5. Monitoring & self-healing

Exit Codes:
    0 - Graceful shutdown
    1 - Deployment failure
    2 - Health check failure
    3 - Timeout

Owner: Trang
Version: 1.0.0
"""

import asyncio
import signal
import sys
from pathlib import Path

# Add paths for imports
_AMOS_ROOT = Path(__file__).parent
sys.path.insert(0, str(_AMOS_ROOT))


from amos_unified_deployment_orchestrator import (
    AMOSDeploymentOrchestrator,
    deploy_amos,
)


class DockerEntrypoint:
    """Docker entrypoint handler with graceful shutdown."""

    def __init__(self):
        self.orchestrator: Optional[AMOSDeploymentOrchestrator] = None
        self._shutdown_event = asyncio.Event()
        self._setup_signal_handlers()

    def _setup_signal_handlers(self):
        """Setup graceful shutdown on SIGTERM/SIGINT."""
        for sig in (signal.SIGTERM, signal.SIGINT):
            signal.signal(sig, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        print(f"\n⚠️  Received signal {signum}, initiating graceful shutdown...")
        self._shutdown_event.set()
        if self.orchestrator:
            asyncio.create_task(self._shutdown())

    async def _shutdown(self):
        """Perform graceful shutdown."""
        if self.orchestrator:
            await self.orchestrator.shutdown()
        sys.exit(0)

    async def run(self, mode: str = "production") -> int:
        """Run deployment orchestration.

        Args:
            mode: Deployment mode (development, staging, production)

        Returns:
            Exit code (0 for success, 1-3 for various failures)
        """
        print("=" * 70)
        print(" AMOS DOCKER ENTRYPOINT")
        print(" Unified Deployment Orchestrator Integration")
        print("=" * 70)
        print(f"Mode: {mode}")
        print(f"Working Directory: {Path.cwd()}")
        print("=" * 70)

        try:
            # Deploy with unified orchestrator
            print("\n🚀 Starting 5-phase deployment...\n")
            self.orchestrator = await deploy_amos(mode=mode, enable_mcp=True, enable_healing=True)

            # Get deployment status
            status = self.orchestrator.get_status()

            print("\n" + "=" * 70)
            print(" ✅ DEPLOYMENT SUCCESSFUL - CONTAINER READY")
            print("=" * 70)
            print(f"Deployment ID: {status.deployment_id}")
            print(f"Phase: {status.phase.name}")
            print(f"Health: {status.overall_health:.2f}/1.0")
            print(f"Runtime: {'✅ READY' if status.runtime_ready else '❌ FAILED'}")
            print(f"MCP: {'✅ READY' if status.mcp_ready else '❌ FAILED'}")
            print("=" * 70)

            # Keep container running
            print("\n💤 Container running - Press Ctrl+C or send SIGTERM to stop")
            await self._wait_for_shutdown()

            return 0

        except Exception as e:
            print(f"\n❌ Deployment failed: {e}")
            return 1

    async def _wait_for_shutdown(self):
        """Wait for shutdown signal."""
        while not self._shutdown_event.is_set():
            try:
                await asyncio.wait_for(self._shutdown_event.wait(), timeout=1.0)
            except TimeoutError:
                continue


async def main():
    """Main entrypoint."""
    # Get mode from command line or environment
    mode = sys.argv[1] if len(sys.argv) > 1 else "production"

    # Validate mode
    valid_modes = ["development", "staging", "production"]
    if mode not in valid_modes:
        print(f"❌ Invalid mode: {mode}")
        print(f"Valid modes: {', '.join(valid_modes)}")
        sys.exit(1)

    entrypoint = DockerEntrypoint()
    exit_code = await entrypoint.run(mode)
    sys.exit(exit_code)


if __name__ == "__main__":
    asyncio.run(main())
