"""AMOS Local-First AI Platform - Unified CLI

One command to rule them all:
- LiteLLM proxy for model routing
- Continue.dev for IDE integration
- Aider for terminal coding
- OpenHands for autonomous work
- OpenClaw for persistent assistant
- Repo Doctor for security verification

Usage:
    python amos_local_platform.py setup    # Install and configure all tools
    python amos_local_platform.py start   # Start LiteLLM proxy
    python amos_local_platform.py status  # Check all services
    python amos_local_platform.py stop    # Stop all services
"""

import argparse
import json
import logging
import subprocess
import sys
import time
from pathlib import Path

# Add amos_model_fabric to path
sys.path.insert(0, str(Path(__file__).parent))

from amos_model_fabric.aider_integration import AiderIntegration
from amos_model_fabric.continue_integration import ContinueConfigGenerator
from amos_model_fabric.litellm_setup import LiteLLMSetup
from amos_model_fabric.openhands_integration import OpenHandsIntegration

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


class AMOSLocalPlatform:
    """Unified local-first AI platform."""

    def __init__(self):
        self.litellm = LiteLLMSetup()
        self.continue_gen = ContinueConfigGenerator()
        self.aider = AiderIntegration()
        self.openhands = OpenHandsIntegration()

    def setup_all(self) -> bool:
        """Setup all platform components."""
        print("=" * 60)
        print("AMOS Local-First AI Platform Setup")
        print("=" * 60)

        # 1. Install LiteLLM
        print("\n1. Setting up LiteLLM proxy...")
        if not self.litellm.install_litellm():
            print("❌ Failed to install LiteLLM")
            return False
        config = self.litellm.generate_config()
        self.litellm.write_config(config)
        print(f"   ✓ LiteLLM config: {self.litellm.config_file}")

        # 2. Configure Continue
        print("\n2. Configuring Continue.dev...")
        self.continue_gen.write_config()
        print(f"   ✓ Continue config: {self.continue_gen.config_file}")

        # 3. Check Aider
        print("\n3. Checking Aider...")
        if not self.aider.is_installed():
            print("   Installing Aider...")
            self.aider.install()
        self.aider.write_config()
        print(f"   ✓ Aider config: {self.aider.config_file}")

        # 4. Check security scanners
        print("\n4. Checking security scanners...")
        scanners = ["semgrep", "trivy", "gitleaks", "ruff"]
        missing = [s for s in scanners if not self._is_installed(s)]
        if missing:
            print(f"   ⚠ Missing scanners: {', '.join(missing)}")
            print("   Run: ./scripts/install_security_scanners.sh")
        else:
            print("   ✓ All security scanners available")

        # Summary
        print("\n" + "=" * 60)
        print("Setup complete!")
        print("=" * 60)
        print("\nNext steps:")
        print("  1. Start Ollama: ollama serve")
        print("  2. Start platform: python amos_local_platform.py start")
        print("  3. Open VS Code and install Continue extension")
        print("\nUsage:")
        print("  IDE coding: Use Continue.dev in VS Code")
        print("  Terminal:   aider --openai-api-base http://localhost:4000")
        print("  Autonomous: python -m amos_model_fabric.openhands_integration interactive")

        return True

    def start(self) -> bool:
        """Start the platform."""
        print("Starting AMOS Local Platform...")

        # Start LiteLLM proxy
        process = self.litellm.start_proxy(port=4000, daemon=True)
        if process:
            print("✓ LiteLLM proxy started on http://localhost:4000")
            time.sleep(2)

            # Test connection
            models = self.litellm.get_models(port=4000)
            if models:
                print(f"✓ {len(models)} models available")
                for m in models[:3]:
                    print(f"  - {m.get('id', 'unknown')}")
            else:
                print("⚠ No models detected. Make sure Ollama is running.")

        return True

    def stop(self) -> bool:
        """Stop all services."""
        print("Stopping AMOS Local Platform...")
        self.litellm.stop_proxy()
        print("✓ LiteLLM proxy stopped")
        return True

    def status(self) -> dict:
        """Get platform status."""
        import urllib.request

        status = {
            "litellm_proxy": False,
            "models_available": 0,
            "continue_config": False,
            "aider_installed": False,
            "openhands_ready": False,
        }

        # Check LiteLLM
        try:
            req = urllib.request.Request(
                "http://localhost:4000/health",
                headers={"Authorization": "Bearer sk-amos-local"},
            )
            with urllib.request.urlopen(req, timeout=2) as resp:
                status["litellm_proxy"] = resp.status == 200
        except Exception:
            pass

        if status["litellm_proxy"]:
            models = self.litellm.get_models(port=4000)
            status["models_available"] = len(models)

        # Check configs
        status["continue_config"] = self.continue_gen.config_file.exists()
        status["aider_installed"] = self.aider.is_installed()
        status["openhands_ready"] = self.openhands.is_docker_available()

        return status

    def _is_installed(self, cmd: str) -> bool:
        """Check if a command is installed."""
        return (
            subprocess.run(
                ["which", cmd],
                capture_output=True,
            ).returncode
            == 0
        )


def main():
    parser = argparse.ArgumentParser(
        description="AMOS Local-First AI Platform",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s setup          # Install and configure all tools
  %(prog)s start          # Start LiteLLM proxy
  %(prog)s status         # Check all services
  %(prog)s stop           # Stop all services
  %(prog)s test           # Test chat completion
        """,
    )
    parser.add_argument(
        "command", choices=["setup", "start", "stop", "status", "test"], help="Command to run"
    )

    args = parser.parse_args()

    platform = AMOSLocalPlatform()

    if args.command == "setup":
        success = platform.setup_all()
        sys.exit(0 if success else 1)

    elif args.command == "start":
        success = platform.start()
        sys.exit(0 if success else 1)

    elif args.command == "stop":
        success = platform.stop()
        sys.exit(0 if success else 1)

    elif args.command == "status":
        status = platform.status()
        print(json.dumps(status, indent=2))

        print("\nStatus Summary:")
        for key, value in status.items():
            icon = "✅" if value else "❌"
            if isinstance(value, bool):
                print(f"  {icon} {key}: {'Yes' if value else 'No'}")
            else:
                print(f"  {icon} {key}: {value}")

    elif args.command == "test":
        setup = LiteLLMSetup()
        models = setup.get_models(port=4000)
        if models:
            model_id = models[0].get("id", "ollama/qwen2.5-coder:14b")
            print(f"Testing model: {model_id}")
            success = setup.test_chat_completion(model_id, port=4000)
            sys.exit(0 if success else 1)
        else:
            print("No models available. Start Ollama first.")
            sys.exit(1)


if __name__ == "__main__":
    main()
