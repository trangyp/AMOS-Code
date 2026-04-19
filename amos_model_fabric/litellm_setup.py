"""LiteLLM Proxy Server Setup and Configuration

Real implementation for managing LiteLLM proxy with all local LLM backends.
"""

import json
import logging
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

logger = logging.getLogger(__name__)


class LiteLLMSetup:
    """Setup and manage LiteLLM proxy server for AMOS."""

    def __init__(self, config_dir: Optional[Path] = None):
        self.config_dir = config_dir or Path.home() / ".amos" / "litellm"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.config_file = self.config_dir / "config.yaml"
        self.env_file = self.config_dir / ".env"
        self.proxy_process: subprocess.Popen | None = None

    def detect_ollama_models(self) -> List[dict[str, Any]]:
        """Detect available Ollama models."""
        models = []
        try:
            result = subprocess.run(
                ["ollama", "list"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                lines = result.stdout.strip().split("\n")[1:]  # Skip header
                for line in lines:
                    parts = line.split()
                    if parts:
                        model_name = parts[0]
                        models.append({
                            "model_name": f"ollama/{model_name}",
                            "litellm_params": {
                                "model": f"ollama/{model_name}",
                                "api_base": "http://localhost:11434",
                            },
                            "model_info": {
                                "id": model_name,
                                "mode": "chat",
                            },
                        })
        except (subprocess.TimeoutExpired, FileNotFoundError, Exception) as e:
            logger.warning(f"Could not detect Ollama models: {e}")
        return models

    def detect_lmstudio(self) -> Optional[Dict[str, Any] ]:
        """Detect if LM Studio is running."""
        import urllib.request
        try:
            req = urllib.request.Request(
                "http://localhost:1234/v1/models",
                headers={"Authorization": "Bearer lm-studio"},
                method="GET",
            )
            with urllib.request.urlopen(req, timeout=2) as resp:
                if resp.status == 200:
                    return {
                        "model_name": "lmstudio/local",
                        "litellm_params": {
                            "model": "openai/local-model",
                            "api_base": "http://localhost:1234/v1",
                            "api_key": "lm-studio",
                        },
                        "model_info": {
                            "id": "lmstudio-local",
                            "mode": "chat",
                        },
                    }
        except Exception:
            pass
        return None

    def detect_vllm(self) -> Optional[Dict[str, Any] ]:
        """Detect if vLLM is running."""
        import urllib.request
        try:
            req = urllib.request.Request(
                "http://localhost:8000/v1/models",
                method="GET",
            )
            with urllib.request.urlopen(req, timeout=2) as resp:
                if resp.status == 200:
                    return {
                        "model_name": "vllm/local",
                        "litellm_params": {
                            "model": "openai/local-model",
                            "api_base": "http://localhost:8000/v1",
                        },
                        "model_info": {
                            "id": "vllm-local",
                            "mode": "chat",
                        },
                    }
        except Exception:
            pass
        return None

    def generate_config(self) -> Dict[str, Any]:
        """Generate LiteLLM configuration with detected models."""
        model_list = []

        # Detect Ollama models
        ollama_models = self.detect_ollama_models()
        model_list.extend(ollama_models)

        # Detect LM Studio
        lmstudio = self.detect_lmstudio()
        if lmstudio:
            model_list.append(lmstudio)

        # Detect vLLM
        vllm = self.detect_vllm()
        if vllm:
            model_list.append(vllm)

        # Default config
        config = {
            "model_list": model_list,
            "litellm_settings": {
                "drop_params": True,
                "num_retries": 3,
                "request_timeout": 120,
                "fallbacks": [{"ollama/qwen2.5-coder:14b": ["ollama/llama3.2"]}],
            },
            "router_settings": {
                "routing_strategy": "least-busy",
                "enable_cooldowns": True,
                "cooldown_time": 30,
            },
            "general_settings": {
                "master_key": os.environ.get("LITELLM_MASTER_KEY", "sk-amos-local"),
                "proxy_batch_write_at": 60,
            },
        }

        return config

    def write_config(self, config: Optional[Dict[str, Any] ] = None) -> Path:
        """Write LiteLLM configuration to file."""
        config = config or self.generate_config()
        self.config_file.write_text(yaml.dump(config, default_flow_style=False))
        logger.info(f"LiteLLM config written to {self.config_file}")
        return self.config_file

    def setup_environment(self) -> None:
        """Setup environment variables."""
        env_vars = {
            "LITELLM_MASTER_KEY": "sk-amos-local",
            "LITELLM_LOG": "DEBUG",
            "OLLAMA_API_BASE": "http://localhost:11434",
        }

        env_content = "\n".join(f'{k}="{v}"' for k, v in env_vars.items())
        self.env_file.write_text(env_content)
        logger.info(f"Environment file written to {self.env_file}")

    def install_litellm(self) -> bool:
        """Install LiteLLM proxy if not already installed."""
        try:
            import litellm
            logger.info(f"LiteLLM already installed: {litellm.__version__}")
            return True
        except ImportError:
            logger.info("Installing LiteLLM...")
            try:
                subprocess.run(
                    [sys.executable, "-m", "pip", "install", "litellm[proxy]", "-q"],
                    check=True,
                )
                logger.info("LiteLLM installed successfully")
                return True
            except subprocess.CalledProcessError as e:
                logger.error(f"Failed to install LiteLLM: {e}")
                return False

    def start_proxy(self, port: int = 4000, daemon: bool = False) -> subprocess.Popen | None:
        """Start LiteLLM proxy server."""
        if not self.config_file.exists():
            self.write_config()

        # Check if already running
        import urllib.request
        try:
            with urllib.request.urlopen(f"http://localhost:{port}/health", timeout=2) as resp:
                if resp.status == 200:
                    logger.info(f"LiteLLM proxy already running on port {port}")
                    return None
        except Exception:
            pass

        # Start proxy
        cmd = [
            sys.executable, "-m", "litellm",
            "--config", str(self.config_file),
            "--port", str(port),
        ]

        env = {**os.environ, "LITELLM_MASTER_KEY": "sk-amos-local"}

        if daemon:
            # Background process
            self.proxy_process = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                env=env,
            )
        else:
            # Foreground for debugging
            self.proxy_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env,
            )

        # Wait for startup
        time.sleep(5)

        # Verify
        for _ in range(5):
            try:
                headers = {"Authorization": "Bearer sk-amos-local"}
                req = urllib.request.Request(
                    f"http://localhost:{port}/models",
                    headers=headers,
                )
                with urllib.request.urlopen(req, timeout=2) as resp:
                    if resp.status == 200:
                        logger.info(f"LiteLLM proxy started on http://localhost:{port}")
                        return self.proxy_process
            except Exception:
                time.sleep(1)

        logger.error("Failed to start LiteLLM proxy")
        return None

    def stop_proxy(self) -> None:
        """Stop LiteLLM proxy server."""
        if self.proxy_process:
            self.proxy_process.terminate()
            self.proxy_process.wait(timeout=5)
            self.proxy_process = None
            logger.info("LiteLLM proxy stopped")

    def get_models(self, port: int = 4000) -> List[dict[str, Any]]:
        """Get list of available models from proxy."""
        import urllib.request
        try:
            headers = {"Authorization": "Bearer sk-amos-local"}
            req = urllib.request.Request(
                f"http://localhost:{port}/models",
                headers=headers,
            )
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read())
                return data.get("data", [])
        except Exception as e:
            logger.error(f"Failed to get models: {e}")
            return []

    def test_chat_completion(self, model: str, port: int = 4000) -> bool:
        """Test chat completion through proxy."""
        import urllib.request
        try:
            payload = {
                "model": model,
                "messages": [{"role": "user", "content": "Say 'LiteLLM is working'"}],
                "max_tokens": 50,
            }
            headers = {
                "Authorization": "Bearer sk-amos-local",
                "Content-Type": "application/json",
            }
            req = urllib.request.Request(
                f"http://localhost:{port}/v1/chat/completions",
                data=json.dumps(payload).encode(),
                headers=headers,
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read())
                content = data["choices"][0]["message"]["content"]
                logger.info(f"Test response: {content}")
                return True
        except Exception as e:
            logger.error(f"Test failed: {e}")
            return False


def main():
    """CLI for LiteLLM setup."""
    import argparse

    parser = argparse.ArgumentParser(description="AMOS LiteLLM Proxy Setup")
    parser.add_argument("command", choices=["setup", "start", "stop", "status", "test"])
    parser.add_argument("--port", type=int, default=4000)
    parser.add_argument("--daemon", action="store_true", help="Run in background")

    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    setup = LiteLLMSetup()

    if args.command == "setup":
        setup.install_litellm()
        config = setup.generate_config()
        setup.write_config(config)
        setup.setup_environment()
        print(f"\nLiteLLM configuration:")
        print(f"  Config: {setup.config_file}")
        print(f"  Models: {len(config['model_list'])}")
        for m in config["model_list"]:
            print(f"    - {m['model_name']}")

    elif args.command == "start":
        setup.write_config()
        process = setup.start_proxy(port=args.port, daemon=args.daemon)
        if process and not args.daemon:
            try:
                process.wait()
            except KeyboardInterrupt:
                setup.stop_proxy()

    elif args.command == "stop":
        setup.stop_proxy()

    elif args.command == "status":
        models = setup.get_models(port=args.port)
        print(f"Available models ({len(models)}):")
        for m in models:
            print(f"  - {m.get('id', 'unknown')}")

    elif args.command == "test":
        models = setup.get_models(port=args.port)
        if models:
            model_id = models[0].get("id", "ollama/qwen2.5-coder:14b")
            print(f"Testing with model: {model_id}")
            success = setup.test_chat_completion(model_id, port=args.port)
            print(f"Test {'PASSED' if success else 'FAILED'}")


if __name__ == "__main__":
    main()
