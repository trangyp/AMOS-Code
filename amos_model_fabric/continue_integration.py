"""Continue.dev Integration - VS Code Extension Configuration

Generates Continue.dev config for local LLM backends via LiteLLM proxy.
https://docs.continue.dev/guides/ollama-guide
"""

import json
import logging
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)


class ContinueConfigGenerator:
    """Generate Continue.dev configuration for AMOS platform."""

    def __init__(self, litellm_proxy_url: str = "http://localhost:4000"):
        self.proxy_url = litellm_proxy_url
        self.config_dir = Path.home() / ".continue"
        self.config_file = self.config_dir / "config.yaml"

    def generate_config(self, models: Optional[list[dict[str, Any]]] = None) -> dict[str, Any]:
        """Generate Continue.dev configuration."""
        if not models:
            models = self._get_default_models()

        # Build Continue models configuration
        continue_models = []
        for model in models:
            continue_models.append(
                {
                    "title": model["name"],
                    "provider": "openai",  # LiteLLM exposes OpenAI-compatible API
                    "model": model["id"],
                    "apiBase": self.proxy_url,
                    "apiKey": "sk-amos-local",
                }
            )

        # Primary model (first available)
        primary = continue_models[0] if continue_models else None

        config = {
            "models": continue_models,
            "context": {
                "provider": "ollama",  # Use Ollama for embeddings if available
                "model": "nomic-embed-text",
            },
            "completionOptions": {
                "temperature": 0.7,
                "maxTokens": 4096,
            },
        }

        # Add tab autocomplete model if we have a fast one
        fast_models = [
            m
            for m in models
            if any(x in m["id"] for x in ["qwen2.5-coder", "codellama", "deepseek-coder"])
        ]
        if fast_models:
            config["tabAutocompleteModel"] = {
                "title": f"Autocomplete ({fast_models[0]['name']})",
                "provider": "openai",
                "model": fast_models[0]["id"],
                "apiBase": self.proxy_url,
                "apiKey": "sk-amos-local",
            }

        # Add custom commands
        config["customCommands"] = [
            {
                "name": "test",
                "prompt": "Write a comprehensive set of unit tests for the selected code. It should setup, run tests that check for correctness including important edge cases, and teardown. Ensure that the tests are complete and sophisticated. Give the tests just as chat output, do not edit any file.",
                "description": "Write unit tests for highlighted code",
            },
            {
                "name": "security-review",
                "prompt": "Review the selected code for security vulnerabilities including: injection risks, hardcoded secrets, insecure crypto, path traversal. Provide specific line-by-line findings with severity levels.",
                "description": "Security-focused code review",
            },
        ]

        return config

    def _get_default_models(self) -> list[dict[str, Any]]:
        """Get default model list for Continue."""
        return [
            {
                "name": "Qwen 2.5 Coder (Local)",
                "id": "ollama/qwen2.5-coder:14b",
                "description": "Primary coding model - 14B parameters",
            },
            {
                "name": "DeepSeek Coder V2 (Local)",
                "id": "ollama/deepseek-coder-v2:16b",
                "description": "Alternative coding model - 16B parameters",
            },
            {
                "name": "Llama 3.2 (Local)",
                "id": "ollama/llama3.2",
                "description": "Fast general-purpose model - 3B parameters",
            },
        ]

    def write_config(self, config: Optional[dict[str, Any]] = None) -> Path:
        """Write Continue configuration to ~/.continue/config.yaml."""
        import yaml

        config = config or self.generate_config()
        self.config_dir.mkdir(parents=True, exist_ok=True)

        self.config_file.write_text(yaml.dump(config, default_flow_style=False))
        logger.info(f"Continue config written to {self.config_file}")
        return self.config_file

    def install_extension(self) -> bool:
        """Open VS Code to install Continue extension."""
        import shutil
        import subprocess

        code_cmd = shutil.which("code")
        if not code_cmd:
            logger.error("VS Code CLI not found. Please install VS Code.")
            return False

        try:
            subprocess.run(
                [code_cmd, "--install-extension", "continue.continue"],
                check=True,
                capture_output=True,
            )
            logger.info("Continue extension installed")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to install Continue: {e}")
            return False

    def open_vscode(self) -> bool:
        """Open VS Code."""
        import shutil
        import subprocess

        code_cmd = shutil.which("code")
        if not code_cmd:
            logger.error("VS Code CLI not found")
            return False

        try:
            subprocess.run([code_cmd, "."], cwd=Path.cwd())
            return True
        except Exception as e:
            logger.error(f"Failed to open VS Code: {e}")
            return False

    def get_status(self) -> dict[str, Any]:
        """Get Continue configuration status."""
        status = {
            "config_exists": self.config_file.exists(),
            "config_path": str(self.config_file),
            "proxy_url": self.proxy_url,
        }

        if self.config_file.exists():
            try:
                import yaml

                config = yaml.safe_load(self.config_file.read_text())
                status["models_configured"] = len(config.get("models", []))
                status["autocomplete_configured"] = "tabAutocompleteModel" in config
            except Exception as e:
                status["error"] = str(e)

        return status


def main():
    """CLI for Continue integration."""
    import argparse

    parser = argparse.ArgumentParser(description="Continue.dev Integration")
    parser.add_argument("command", choices=["setup", "status", "install"])
    parser.add_argument("--proxy-url", default="http://localhost:4000")

    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    gen = ContinueConfigGenerator(litellm_proxy_url=args.proxy_url)

    if args.command == "setup":
        gen.write_config()
        print("\nContinue configuration:")
        print(f"  Config: {gen.config_file}")
        print("\nNext steps:")
        print("  1. Start LiteLLM proxy: python -m amos_model_fabric.litellm_setup start")
        print("  2. Install Continue extension: code --install-extension continue.continue")
        print("  3. Restart VS Code")

    elif args.command == "status":
        status = gen.get_status()
        print(json.dumps(status, indent=2))

    elif args.command == "install":
        gen.install_extension()


if __name__ == "__main__":
    main()
