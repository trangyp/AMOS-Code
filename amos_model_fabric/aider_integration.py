"""Aider Integration - Terminal-Native AI Coding Assistant

Real integration with Aider for repo-wide editing via terminal.
https://aider.chat/docs/llms/ollama.html
"""

import json
import logging
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class AiderIntegration:
    """Integrate Aider terminal AI assistant with AMOS platform."""

    def __init__(self, litellm_proxy_url: str = "http://localhost:4000"):
        self.proxy_url = litellm_proxy_url
        self.config_file = Path.home() / ".aider.conf.yml"

    def is_installed(self) -> bool:
        """Check if Aider is installed."""
        return subprocess.run(
            ["aider", "--version"],
            capture_output=True,
        ).returncode == 0

    def install(self) -> bool:
        """Install Aider via pip."""
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "aider-chat", "-q"],
                check=True,
            )
            logger.info("Aider installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to install Aider: {e}")
            return False

    def generate_config(self) -> Dict[str, Any]:
        """Generate Aider configuration for LiteLLM proxy."""
        config = {
            # Use LiteLLM proxy as OpenAI-compatible endpoint
            "openai-api-base": self.proxy_url,
            "openai-api-key": "sk-amos-local",
            "model": "openai/ollama/qwen2.5-coder:14b",

            # Editor settings
            "edit-format": "diff",
            "stream": True,
            "pretty": True,

            # Git settings
            "auto-commits": True,
            "dirty-commits": False,
            "commit-prompt": "Commit changes with a concise, descriptive message",

            # Security
            "confirm-ask": True,  # Ask before making changes
            "code-theme": "monokai",

            # Files
            "file-context": True,
            "voice": False,  # Disabled by default
        }
        return config

    def write_config(self, config: Optional[Dict[str, Any] ] = None) -> Path:
        """Write Aider configuration."""
        import yaml

        config = config or self.generate_config()
        self.config_file.write_text(yaml.dump(config, default_flow_style=False))
        logger.info(f"Aider config written to {self.config_file}")
        return self.config_file

    def start_aider(
        self,
        files: Optional[List[str] ] = None,
        message: Optional[str] = None,
        model: str = "ollama/qwen2.5-coder:14b",
    ) -> subprocess.Popen:
        """Start Aider in the current directory."""
        if not self.is_installed():
            logger.error("Aider not installed. Run install() first.")
            raise RuntimeError("Aider not installed")

        cmd = [
            "aider",
            "--openai-api-base", self.proxy_url,
            "--openai-api-key", "sk-amos-local",
            "--model", f"openai/{model}",
        ]

        if files:
            cmd.extend(files)

        if message:
            cmd.extend(["--message", message])

        return subprocess.Popen(cmd)

    def run_once(
        self,
        message: str,
        files: Optional[List[str] ] = None,
        model: str = "ollama/qwen2.5-coder:14b",
    ) -> str:
        """Run Aider once with a message and return output."""
        cmd = [
            "aider",
            "--openai-api-base", self.proxy_url,
            "--openai-api-key", "sk-amos-local",
            "--model", f"openai/{model}",
            "--yes",  # Non-interactive mode
            "--no-auto-commits",
            "--message", message,
        ]

        if files:
            cmd.extend(files)

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
        )

        return result.stdout + result.stderr

    def get_status(self) -> Dict[str, Any]:
        """Get Aider integration status."""
        status = {
            "installed": self.is_installed(),
            "config_path": str(self.config_file),
            "config_exists": self.config_file.exists(),
            "proxy_url": self.proxy_url,
        }

        if status["installed"]:
            try:
                result = subprocess.run(
                    ["aider", "--version"],
                    capture_output=True,
                    text=True,
                )
                status["version"] = result.stdout.strip()
            except Exception:
                pass

        return status


def main():
    """CLI for Aider integration."""
    import argparse

    parser = argparse.ArgumentParser(description="Aider Integration")
    parser.add_argument("command", choices=["setup", "status", "run"])
    parser.add_argument("--message", "-m", help="Message to send to Aider")
    parser.add_argument("--files", nargs="+", help="Files to edit")
    parser.add_argument("--model", default="ollama/qwen2.5-coder:14b")
    parser.add_argument("--proxy-url", default="http://localhost:4000")

    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    aider = AiderIntegration(litellm_proxy_url=args.proxy_url)

    if args.command == "setup":
        if not aider.is_installed():
            print("Installing Aider...")
            aider.install()
        aider.write_config()
        print(f"\nAider configured:")
        print(f"  Config: {aider.config_file}")
        print(f"  Proxy: {aider.proxy_url}")
        print(f"\nUsage:")
        print(f"  aider --openai-api-base {aider.proxy_url} --model openai/ollama/qwen2.5-coder:14b")

    elif args.command == "status":
        status = aider.get_status()
        print(json.dumps(status, indent=2))

    elif args.command == "run":
        if not args.message:
            print("ERROR: --message required")
            sys.exit(1)

        output = aider.run_once(
            message=args.message,
            files=args.files,
            model=args.model,
        )
        print(output)


if __name__ == "__main__":
    main()
