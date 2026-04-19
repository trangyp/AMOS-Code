"""OpenHands Integration - Autonomous AI Software Engineer

Real integration with OpenHands for autonomous repo work.
https://docs.openhands.dev/
"""

from __future__ import annotations

import json
import logging
import subprocess
import sys
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class OpenHandsIntegration:
    """Integrate OpenHands autonomous agent with AMOS platform."""

    def __init__(self, litellm_proxy_url: str = "http://localhost:4000"):
        self.proxy_url = litellm_proxy_url
        self.workspace_dir = Path.cwd()

    def is_docker_available(self) -> bool:
        """Check if Docker is available (required for OpenHands)."""
        try:
            result = subprocess.run(
                ["docker", "--version"],
                capture_output=True,
                timeout=5,
            )
            return result.returncode == 0
        except Exception:
            return False

    def is_installed(self) -> bool:
        """Check if OpenHands runtime is available."""
        try:
            result = subprocess.run(
                ["docker", "images", "ghcr.io/all-hands-ai/runtime", "-q"],
                capture_output=True,
                text=True,
            )
            return bool(result.stdout.strip())
        except Exception:
            return False

    def pull_runtime(self) -> bool:
        """Pull OpenHands Docker runtime."""
        try:
            subprocess.run(
                ["docker", "pull", "ghcr.io/all-hands-ai/runtime:0.9-docker"],
                check=True,
            )
            logger.info("OpenHands runtime pulled")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to pull OpenHands: {e}")
            return False

    def run_task(
        self,
        task: str,
        model: str = "ollama/qwen2.5-coder:14b",
        timeout_minutes: int = 30,
    ) -> subprocess.Popen:
        """Run OpenHands with a specific task."""
        if not self.is_docker_available():
            raise RuntimeError("Docker not available")

        # OpenHands Docker command with LiteLLM proxy
        cmd = [
            "docker", "run", "-it", "--rm",
            "-e", f"LLM_API_KEY=sk-amos-local",
            "-e", f"LLM_BASE_URL={self.proxy_url}",
            "-e", f"LLM_MODEL={model}",
            "-e", "AGENT_MEMORY_ENABLED=true",
            "-v", f"{self.workspace_dir}:/workspace",
            "-v", "/var/run/docker.sock:/var/run/docker.sock",
            "ghcr.io/all-hands-ai/runtime:0.9-docker",
            "poetry", "run", "python", "-m", "openhands.core.main",
            "-t", task,
        ]

        return subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

    def run_interactive(self, model: str = "ollama/qwen2.5-coder:14b") -> subprocess.Popen:
        """Run OpenHands in interactive mode."""
        if not self.is_docker_available():
            raise RuntimeError("Docker not available")

        cmd = [
            "docker", "run", "-it", "--rm",
            "-e", f"LLM_API_KEY=sk-amos-local",
            "-e", f"LLM_BASE_URL={self.proxy_url}",
            "-e", f"LLM_MODEL={model}",
            "-e", "AGENT_MEMORY_ENABLED=true",
            "-v", f"{self.workspace_dir}:/workspace",
            "-v", "/var/run/docker.sock:/var/run/docker.sock",
            "ghcr.io/all-hands-ai/runtime:0.9-docker",
            "/bin/bash",
        ]

        return subprocess.Popen(cmd)

    def get_status(self) -> dict[str, Any]:
        """Get OpenHands integration status."""
        return {
            "docker_available": self.is_docker_available(),
            "runtime_available": self.is_installed(),
            "workspace_dir": str(self.workspace_dir),
            "proxy_url": self.proxy_url,
        }


def main():
    """CLI for OpenHands integration."""
    import argparse

    parser = argparse.ArgumentParser(description="OpenHands Integration")
    parser.add_argument("command", choices=["setup", "status", "run", "interactive"])
    parser.add_argument("--task", "-t", help="Task description for OpenHands")
    parser.add_argument("--model", default="ollama/qwen2.5-coder:14b")
    parser.add_argument("--proxy-url", default="http://localhost:4000")
    parser.add_argument("--timeout", type=int, default=30)

    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    oh = OpenHandsIntegration(litellm_proxy_url=args.proxy_url)

    if args.command == "setup":
        if not oh.is_docker_available():
            print("ERROR: Docker is required for OpenHands")
            sys.exit(1)
        print("Pulling OpenHands runtime...")
        oh.pull_runtime()
        print("\nOpenHands configured")

    elif args.command == "status":
        status = oh.get_status()
        print(json.dumps(status, indent=2))

    elif args.command == "run":
        if not args.task:
            print("ERROR: --task required")
            sys.exit(1)

        process = oh.run_task(
            task=args.task,
            model=args.model,
            timeout_minutes=args.timeout,
        )
        stdout, stderr = process.communicate()
        print(stdout)
        if stderr:
            print(stderr, file=sys.stderr)

    elif args.command == "interactive":
        process = oh.run_interactive(model=args.model)
        process.wait()


if __name__ == "__main__":
    main()
