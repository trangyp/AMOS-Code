#!/usr/bin/env python3
"""AMOS Math CLI-Dashboard Integration Layer.

Provides async integration between CLI commands and the math dashboard server.
Allows CLI to query running dashboard instances and manage server lifecycle.

Architecture: Async Client-Server Bridge Pattern
"""

import asyncio
import json
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Import httpx for async HTTP requests
try:
    import httpx

    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False

# Math framework imports

from clawspring.amos_brain.mathematical_framework_engine import get_framework_engine


@dataclass
class DashboardStatus:
    """Status of the math dashboard server."""

    running: bool
    url: str
    health: dict[str, Any]
    timestamp: str


class MathDashboardClient:
    """Async client for interacting with the math dashboard server."""

    def __init__(self, base_url: str = "http://localhost:8081"):
        self.base_url = base_url
        self._client: httpx.AsyncClient = None

    async def __aenter__(self) -> MathDashboardClient:
        if HTTPX_AVAILABLE:
            self._client = httpx.AsyncClient(timeout=5.0)
        return self

    async def __aexit__(self, *args) -> None:
        if self._client:
            await self._client.aclose()

    async def health_check(self) -> dict[str, Any]:
        """Check dashboard health."""
        if not HTTPX_AVAILABLE or not self._client:
            # Fallback: check if port is open
            return await self._manual_health_check()

        try:
            response = await self._client.get(f"{self.base_url}/api/health")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"status": "error", "error": str(e)}

    async def get_dashboard_summary(self) -> dict[str, Any]:
        """Get comprehensive dashboard summary."""
        if not HTTPX_AVAILABLE or not self._client:
            # Use local engine directly
            return self._local_summary()

        try:
            response = await self._client.get(f"{self.base_url}/api/dashboard/summary")
            response.raise_for_status()
            return response.json()
        except Exception:
            return self._local_summary()

    async def analyze_task(self, task: str) -> dict[str, Any]:
        """Analyze a task using the dashboard API."""
        if not HTTPX_AVAILABLE or not self._client:
            # Use local engine directly
            return self._local_analyze(task)

        try:
            response = await self._client.post(
                f"{self.base_url}/api/math/analyze", json={"task": task}
            )
            response.raise_for_status()
            return response.json()
        except Exception:
            return self._local_analyze(task)

    def _local_summary(self) -> dict[str, Any]:
        """Generate summary using local engine."""
        engine = get_framework_engine()
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": "local",
            "math_engine": engine.get_stats(),
        }

    def _local_analyze(self, task: str) -> dict[str, Any]:
        """Analyze using local engine."""
        engine = get_framework_engine()
        return {
            "analysis": engine.analyze_architecture(task),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": "local",
        }

    async def _manual_health_check(self) -> dict[str, Any]:
        """Manual health check without httpx."""
        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection("localhost", 8081), timeout=2.0
            )
            writer.close()
            await writer.wait_closed()
            return {"status": "healthy", "manual_check": True}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}


class MathCLIServerManager:
    """Manages the math dashboard server lifecycle from CLI."""

    def __init__(self):
        self._process: subprocess.Popen = None
        self._server_path = Path(__file__).parent / "math_dashboard_server.py"

    async def start_server(
        self, host: str = "0.0.0.0", port: int = 8081, daemon: bool = False
    ) -> DashboardStatus:
        """Start the dashboard server."""
        if not self._server_path.exists():
            return DashboardStatus(
                running=False,
                url=f"http://{host}:{port}",
                health={"error": f"Server not found: {self._server_path}"},
                timestamp=datetime.now(timezone.utc).isoformat(),
            )

        # Check if already running
        client = MathDashboardClient(f"http://{host}:{port}")
        health = await client.health_check()

        if health.get("status") == "healthy":
            return DashboardStatus(
                running=True,
                url=f"http://{host}:{port}",
                health=health,
                timestamp=datetime.now(timezone.utc).isoformat(),
            )

        # Start the server
        if daemon:
            # Start in background
            subprocess.Popen(
                [sys.executable, str(self._server_path)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )
        else:
            # Start in foreground (will block)
            self._process = subprocess.Popen(
                [sys.executable, str(self._server_path)], stdout=sys.stdout, stderr=sys.stderr
            )

        # Wait for server to start
        for _ in range(10):  # Try 10 times
            await asyncio.sleep(0.5)
            health = await client.health_check()
            if health.get("status") == "healthy":
                return DashboardStatus(
                    running=True,
                    url=f"http://{host}:{port}",
                    health=health,
                    timestamp=datetime.now(timezone.utc).isoformat(),
                )

        return DashboardStatus(
            running=False,
            url=f"http://{host}:{port}",
            health={"error": "Server failed to start"},
            timestamp=datetime.now(timezone.utc).isoformat(),
        )

    async def stop_server(self) -> bool:
        """Stop the running dashboard server."""
        if self._process:
            self._process.terminate()
            try:
                self._process.wait(timeout=5)
                return True
            except subprocess.TimeoutExpired:
                self._process.kill()
                return True
        return False


# Async CLI command wrappers
async def async_math_analyze(task: str) -> dict[str, Any]:
    """Async version of math analyze command."""
    async with MathDashboardClient() as client:
        return await client.analyze_task(task)


async def async_math_stats() -> dict[str, Any]:
    """Async version of math stats command."""
    async with MathDashboardClient() as client:
        return await client.get_dashboard_summary()


async def async_math_dashboard_start(
    host: str = "0.0.0.0", port: int = 8081, daemon: bool = False
) -> DashboardStatus:
    """Async version of dashboard start command."""
    manager = MathCLIServerManager()
    return await manager.start_server(host, port, daemon)


# Sync wrappers for CLI integration
def analyze_task_sync(task: str) -> dict[str, Any]:
    """Synchronous wrapper for async analyze."""
    return asyncio.run(async_math_analyze(task))


def get_stats_sync() -> dict[str, Any]:
    """Synchronous wrapper for async stats."""
    return asyncio.run(async_math_stats())


def start_dashboard_sync(
    host: str = "0.0.0.0", port: int = 8081, daemon: bool = False
) -> DashboardStatus:
    """Synchronous wrapper for async dashboard start."""
    return asyncio.run(async_math_dashboard_start(host, port, daemon))


if __name__ == "__main__":
    # Demo async usage
    print("Math CLI Integration Demo")
    print("=" * 50)

    # Test local analysis
    result = analyze_task_sync("Design responsive grid layout")
    print(f"\nAnalysis result: {json.dumps(result, indent=2)}")

    # Test stats
    stats = get_stats_sync()
    print(f"\nStats: {json.dumps(stats, indent=2)}")

    print("\n✓ Integration layer ready")
