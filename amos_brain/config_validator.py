"""Configuration validation for AMOS local runtime.

Validates environment variables and settings before runtime initialization
to provide early, actionable error messages.
"""

import os
import re
from dataclasses import dataclass
from typing import Any


@dataclass
class ValidationResult:
    """Result of configuration validation."""

    valid: bool
    errors: list[str]
    warnings: list[str]
    config: dict[str, Any]


class ConfigValidator:
    """Validator for AMOS local runtime configuration."""

    VALID_BACKENDS = {"ollama", "openai-local", "lmstudio", "vllm", "llamacpp"}
    DEFAULT_URLS = {
        "ollama": "http://127.0.0.1:11434",
        "openai-local": "http://127.0.0.1:1234/v1",
        "lmstudio": "http://127.0.0.1:1234/v1",
        "vllm": "http://127.0.0.1:8000/v1",
        "llamacpp": "http://127.0.0.1:8080/v1",
    }

    def __init__(self):
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.config: dict[str, Any] = {}

    def validate(self) -> ValidationResult:
        """Validate all configuration settings.

        Returns:
            ValidationResult with validity status, errors, warnings,
            and parsed config
        """
        self.errors = []
        self.warnings = []
        self.config = {}

        # Validate backend provider
        self._validate_backend()

        # Validate model name
        self._validate_model()

        # Validate base URL if provided
        self._validate_base_url()

        # Validate API key if needed
        self._validate_api_key()

        # Validate numeric parameters
        self._validate_temperature()

        return ValidationResult(
            valid=len(self.errors) == 0,
            errors=self.errors,
            warnings=self.warnings,
            config=self.config,
        )

    def _validate_backend(self) -> None:
        """Validate the backend provider setting."""
        backend = os.getenv("AMOS_LLM_BACKEND", "ollama").lower()

        if not backend:
            self.errors.append(
                "AMOS_LLM_BACKEND is not set. "
                f"Valid options: {', '.join(sorted(self.VALID_BACKENDS))}"
            )
            return

        if backend not in self.VALID_BACKENDS:
            self.errors.append(
                f"Invalid AMOS_LLM_BACKEND: '{backend}'. "
                f"Valid options: {', '.join(sorted(self.VALID_BACKENDS))}"
            )
            return

        self.config["backend"] = backend

        # Check for common typos
        if backend == "ollama" and os.getenv("AMOS_LLM_BACKEND") == "Ollama":
            self.warnings.append("AMOS_LLM_BACKEND should be lowercase 'ollama', not 'Ollama'")

    def _validate_model(self) -> None:
        """Validate the model name setting."""
        model = os.getenv("AMOS_MODEL", "")
        backend = self.config.get("backend", "ollama")

        if not model:
            # Set sensible defaults based on backend
            defaults = {
                "ollama": "qwen2.5:14b-instruct",
                "lmstudio": "local-model",
                "vllm": "default",
                "llamacpp": "default",
                "openai-local": "local-model",
            }
            default_model = defaults.get(backend, "default")
            self.warnings.append(f"AMOS_MODEL not set. Using default: '{default_model}'")
            self.config["model"] = default_model
            return

        # Check for common issues
        if ":" not in model and backend == "ollama":
            msg = (
                f"Ollama model '{model}' missing tag "
                f"(e.g., '{model}:latest'). "
                "May fail if tag required."
            )
            self.warnings.append(msg)

        # Check for dangerous characters
        if re.search(r"[<>&|;$]", model):
            self.errors.append(
                f"AMOS_MODEL contains invalid characters: '{model}'. "
                "Model name should be alphanumeric with -, _, /, :, ."
            )
            return

        self.config["model"] = model

    def _validate_base_url(self) -> None:
        """Validate the base URL setting."""
        base_url = os.getenv("AMOS_BASE_URL", "").strip()
        backend = self.config.get("backend", "ollama")

        if not base_url:
            # Use default URL
            default_url = self.DEFAULT_URLS.get(backend)
            self.config["base_url"] = default_url
            return

        # Validate URL format
        if not base_url.startswith(("http://", "https://")):
            err = f"AMOS_BASE_URL must start with http:// or https://: '{base_url}'"
            self.errors.append(err)
            return

        # Check for common mistakes
        if "localhost" in base_url and backend == "ollama":
            self.warnings.append(
                "Using 'localhost' instead of '127.0.0.1' for Ollama. "
                "This may fail if IPv6 is not configured."
            )

        # Check port consistency
        port_match = re.search(r":(\d+)", base_url)
        if port_match:
            port = int(port_match.group(1))
            expected_ports = {
                "ollama": 11434,
                "lmstudio": 1234,
                "vllm": 8000,
                "llamacpp": 8080,
            }
            expected = expected_ports.get(backend)
            if expected and port != expected:
                msg = (
                    f"{backend} typically uses port {expected}, "
                    f"but URL has {port}. OK if custom port set."
                )
                self.warnings.append(msg)

        self.config["base_url"] = base_url

    def _validate_api_key(self) -> None:
        """Validate API key setting for OpenAI-compatible backends."""
        backend = self.config.get("backend", "ollama")
        api_key = os.getenv("AMOS_API_KEY", "")

        # Only OpenAI-compatible backends need API keys
        if backend in {"ollama"}:
            if api_key:
                self.warnings.append(f"AMOS_API_KEY is set but not needed for {backend} backend")
            self.config["api_key"] = None
            return

        # For OpenAI-compatible backends
        if not api_key:
            self.warnings.append(f"AMOS_API_KEY not set for {backend}. Using 'local' as default.")
            self.config["api_key"] = "local"
        else:
            self.config["api_key"] = api_key

    def _validate_temperature(self) -> None:
        """Validate temperature setting."""
        temp_str = os.getenv("AMOS_TEMPERATURE", "")

        if not temp_str:
            self.config["temperature"] = 0.2
            return

        try:
            temp = float(temp_str)
            if temp < 0.0 or temp > 2.0:
                msg = (
                    f"AMOS_TEMPERATURE={temp} outside typical "
                    f"range (0.0-2.0). May produce odd results."
                )
                self.warnings.append(msg)
            self.config["temperature"] = temp
        except ValueError:
            self.errors.append(f"AMOS_TEMPERATURE must be a number, got: '{temp_str}'")

    def get_help_message(self, validation_result: ValidationResult) -> str:
        """Generate help message based on validation errors.

        Args:
            validation_result: Result from validate()

        Returns:
            Formatted help message with fixes for errors
        """
        lines = ["\nConfiguration Help:\n"]
        lines.append("  export AMOS_MODEL=llama3.2:latest")
        lines.append("  python amos_local.py")
        lines.append("")
        lines.append("  # With LM Studio")
        lines.append("  export AMOS_LLM_BACKEND=lmstudio")
        lines.append("  export AMOS_MODEL=your-model-name")
        lines.append("  python amos_local.py")

        return "\n".join(lines)


def validate_config() -> ValidationResult:
    """Convenience function to validate configuration.

    Returns:
        ValidationResult with validation status and parsed config
    """
    validator = ConfigValidator()
    return validator.validate()
