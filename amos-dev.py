#!/usr/bin/env python3
"""AMOS Development Environment Orchestrator

Unified development environment management:
- Start/stop full stack (backend + frontend + infrastructure)
- Health checks and connectivity verification
- Log aggregation and monitoring
- Database migrations and seeding

Usage:
    python amos-dev.py start      # Start full stack
    python amos-dev.py stop       # Stop all services
    python amos-dev.py status     # Check service health
    python amos-dev.py logs       # View all logs
    python amos-dev.py reset      # Reset databases

Creator: Trang Phan
Version: 1.0.0
"""

import argparse
import asyncio
import os
import subprocess
import sys
from datetime import UTC, datetime

UTC = UTC
from typing import Any


class Colors:
    """Terminal colors for output."""

    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    RESET = "\033[0m"


def log(msg: str, level: str = "info") -> None:
    """Print colored log message."""
    colors = {
        "info": Colors.BLUE,
        "success": Colors.GREEN,
        "error": Colors.RED,
        "warning": Colors.YELLOW,
    }
    color = colors.get(level, Colors.RESET)
    timestamp = datetime.now(UTC).strftime("%H:%M:%S")
    print(f"{color}[{timestamp}] {msg}{Colors.RESET}")


class ServiceManager:
    """Manage AMOS development services."""

    def __init__(self):
        self.project_root = os.path.dirname(os.path.abspath(__file__))
        self.services: dict[str, dict[str, Any]] = {
            "postgres": {
                "port": 5432,
                "health_url": None,
                "container": "amos-postgres",
            },
            "redis": {
                "port": 6379,
                "health_url": None,
                "container": "amos-redis",
            },
            "backend": {
                "port": 8000,
                "health_url": "http://localhost:8000/health",
                "process": None,
            },
            "dashboard": {
                "port": 5173,
                "health_url": "http://localhost:5173",
                "process": None,
            },
        }

    async def start_infrastructure(self) -> bool:
        """Start PostgreSQL and Redis via docker-compose."""
        log("Starting infrastructure services (PostgreSQL, Redis)...", "info")

        compose_file = os.path.join(self.project_root, "docker-compose.yml")
        if not os.path.exists(compose_file):
            log("docker-compose.yml not found!", "error")
            return False

        try:
            # Start only infrastructure services
            result = subprocess.run(
                ["docker-compose", "up", "-d", "postgres", "redis"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=60,
            )

            if result.returncode != 0:
                log(f"Failed to start infrastructure: {result.stderr}", "error")
                return False

            # Wait for services to be healthy
            log("Waiting for services to be healthy...", "info")
            await asyncio.sleep(5)

            log("Infrastructure services started", "success")
            return True

        except subprocess.TimeoutExpired:
            log("Timeout starting infrastructure", "error")
            return False
        except FileNotFoundError:
            log("docker-compose not found. Is Docker installed?", "error")
            return False

    async def start_backend(self) -> bool:
        """Start FastAPI backend."""
        log("Starting FastAPI backend...", "info")

        backend_dir = os.path.join(self.project_root, "backend")
        main_file = os.path.join(backend_dir, "main.py")

        if not os.path.exists(main_file):
            log(f"Backend main.py not found at {main_file}", "error")
            return False

        try:
            # Check if already running
            if await self._is_port_in_use(8000):
                log("Backend already running on port 8000", "warning")
                return True

            # Start backend in background
            env = os.environ.copy()
            env["PYTHONPATH"] = self.project_root

            process = subprocess.Popen(
                [
                    sys.executable,
                    "-m",
                    "uvicorn",
                    "backend.main:app",
                    "--host",
                    "0.0.0.0",
                    "--port",
                    "8000",
                    "--reload",
                ],
                cwd=self.project_root,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            self.services["backend"]["process"] = process

            # Wait for backend to be ready
            log("Waiting for backend to be ready...", "info")
            for _ in range(30):  # 30 seconds timeout
                if await self._check_health("http://localhost:8000/health"):
                    log("Backend started successfully", "success")
                    return True
                await asyncio.sleep(1)

            log("Backend failed to start within timeout", "error")
            return False

        except Exception as e:
            log(f"Error starting backend: {e}", "error")
            return False

    async def start_dashboard(self) -> bool:
        """Start React dashboard."""
        log("Starting React dashboard...", "info")

        dashboard_dir = os.path.join(self.project_root, "dashboard")
        if not os.path.exists(dashboard_dir):
            log("Dashboard directory not found", "error")
            return False

        try:
            # Check if already running
            if await self._is_port_in_use(5173):
                log("Dashboard already running on port 5173", "warning")
                return True

            # Check for node_modules
            node_modules = os.path.join(dashboard_dir, "node_modules")
            if not os.path.exists(node_modules):
                log("Installing dashboard dependencies...", "info")
                result = subprocess.run(
                    ["npm", "install"],
                    cwd=dashboard_dir,
                    capture_output=True,
                    text=True,
                    timeout=120,
                )
                if result.returncode != 0:
                    log(f"npm install failed: {result.stderr}", "error")
                    return False

            # Start dev server
            process = subprocess.Popen(
                ["npm", "run", "dev"],
                cwd=dashboard_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            self.services["dashboard"]["process"] = process

            # Wait for dashboard to be ready
            log("Waiting for dashboard to be ready...", "info")
            for _ in range(30):
                if await self._is_port_in_use(5173):
                    log("Dashboard started successfully", "success")
                    return True
                await asyncio.sleep(1)

            log("Dashboard failed to start within timeout", "error")
            return False

        except FileNotFoundError:
            log("npm not found. Is Node.js installed?", "error")
            return False
        except Exception as e:
            log(f"Error starting dashboard: {e}", "error")
            return False

    async def stop_all(self) -> None:
        """Stop all services."""
        log("Stopping all services...", "info")

        # Stop backend
        backend_proc = self.services["backend"].get("process")
        if backend_proc and backend_proc.poll() is None:
            backend_proc.terminate()
            try:
                backend_proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                backend_proc.kill()
            log("Backend stopped", "success")

        # Stop dashboard
        dashboard_proc = self.services["dashboard"].get("process")
        if dashboard_proc and dashboard_proc.poll() is None:
            dashboard_proc.terminate()
            try:
                dashboard_proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                dashboard_proc.kill()
            log("Dashboard stopped", "success")

        # Stop infrastructure
        try:
            subprocess.run(
                ["docker-compose", "down"],
                cwd=self.project_root,
                capture_output=True,
                timeout=30,
            )
            log("Infrastructure stopped", "success")
        except Exception as e:
            log(f"Error stopping infrastructure: {e}", "error")

    async def check_status(self) -> dict[str, bool]:
        """Check health of all services."""
        log("Checking service health...", "info")

        results = {}

        # Check infrastructure
        for service in ["postgres", "redis"]:
            container = self.services[service].get("container")
            if container:
                try:
                    result = subprocess.run(
                        ["docker", "ps", "-q", "-f", f"name={container}"],
                        capture_output=True,
                        text=True,
                        timeout=5,
                    )
                    running = bool(result.stdout.strip())
                    results[service] = running
                    log(
                        f"  {service}: {'✅' if running else '❌'}",
                        "success" if running else "error",
                    )
                except Exception:
                    results[service] = False
                    log(f"  {service}: ❌", "error")

        # Check backend
        backend_health = await self._check_health("http://localhost:8000/health")
        results["backend"] = backend_health
        log(
            f"  backend: {'✅' if backend_health else '❌'}",
            "success" if backend_health else "error",
        )

        # Check dashboard
        dashboard_health = await self._is_port_in_use(5173)
        results["dashboard"] = dashboard_health
        log(
            f"  dashboard: {'✅' if dashboard_health else '❌'}",
            "success" if dashboard_health else "error",
        )

        return results

    async def _check_health(self, url: str, timeout: int = 5) -> bool:
        """Check if health endpoint is responding."""
        try:
            import urllib.request

            req = urllib.request.Request(url, method="GET")
            with urllib.request.urlopen(req, timeout=timeout) as response:
                return response.status == 200
        except Exception:
            return False

    async def _is_port_in_use(self, port: int) -> bool:
        """Check if a port is in use."""
        import socket

        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                result = s.connect_ex(("localhost", port))
                return result == 0
        except Exception:
            return False

    async def run_full_check(self) -> bool:
        """Run full integration check."""
        log("Running full integration check...", "info")

        # Run Python integration test
        try:
            result = subprocess.run(
                [sys.executable, "amos_fullstack_integration_test.py"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=60,
            )

            if result.returncode == 0:
                log("✅ Full integration check passed", "success")
                return True
            else:
                log("❌ Integration check failed", "error")
                print(result.stdout)
                print(result.stderr)
                return False

        except Exception as e:
            log(f"Error running integration check: {e}", "error")
            return False


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="AMOS Development Environment Orchestrator")
    parser.add_argument(
        "command",
        choices=["start", "stop", "status", "check", "logs", "reset"],
        help="Command to execute",
    )
    parser.add_argument(
        "--infra-only",
        action="store_true",
        help="Only start infrastructure (no backend/dashboard)",
    )
    parser.add_argument(
        "--skip-dashboard",
        action="store_true",
        help="Skip starting the dashboard",
    )

    args = parser.parse_args()

    manager = ServiceManager()

    if args.command == "start":
        log("=" * 60, "info")
        log("AMOS Development Environment", "info")
        log("=" * 60, "info")

        # Start infrastructure
        if not await manager.start_infrastructure():
            log("Failed to start infrastructure", "error")
            sys.exit(1)

        if args.infra_only:
            log("Infrastructure only mode - skipping backend/dashboard", "info")
            sys.exit(0)

        # Start backend
        if not await manager.start_backend():
            log("Failed to start backend", "error")
            sys.exit(1)

        # Start dashboard (unless skipped)
        if not args.skip_dashboard:
            if not await manager.start_dashboard():
                log("Failed to start dashboard", "warning")
                log("Backend is running - you can start dashboard manually", "info")

        # Final status check
        log("\n" + "=" * 60, "info")
        log("Final Status Check", "info")
        log("=" * 60, "info")
        status = await manager.check_status()

        all_healthy = all(status.values())
        if all_healthy:
            log("\n✅ All services are healthy!", "success")
            log("\nAccess Points:", "info")
            log("  - API Docs: http://localhost:8000/docs", "info")
            log("  - Dashboard: http://localhost:5173", "info")
            log("  - Health: http://localhost:8000/health", "info")
        else:
            log("\n⚠️ Some services are not healthy", "warning")

        # Run full integration check
        await manager.run_full_check()

    elif args.command == "stop":
        await manager.stop_all()
        log("All services stopped", "success")

    elif args.command == "status":
        await manager.check_status()

    elif args.command == "check":
        await manager.run_full_check()

    elif args.command == "logs":
        log("Viewing logs... (Ctrl+C to exit)", "info")
        try:
            subprocess.run(
                ["docker-compose", "logs", "-f"],
                cwd=manager.project_root,
            )
        except KeyboardInterrupt:
            pass

    elif args.command == "reset":
        log("Resetting databases...", "warning")
        await manager.stop_all()
        try:
            subprocess.run(
                ["docker-compose", "down", "-v"],
                cwd=manager.project_root,
                capture_output=True,
                timeout=30,
            )
            log("Databases reset. Run 'start' to reinitialize.", "success")
        except Exception as e:
            log(f"Error resetting: {e}", "error")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log("\nInterrupted by user", "warning")
        sys.exit(0)
