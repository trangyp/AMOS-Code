"""Settings - Configuration management for kernel"""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class KernelSettings:
    """Kernel configuration settings."""

    # Paths
    data_dir: str = field(default_factory=lambda: str(Path.home() / ".amos_kernel"))
    db_path: Optional[str] = None

    # Law validation
    enable_law_validation: bool = True
    max_contradictions: int = 0
    default_capacity: float = 100.0

    # Workflow
    max_workflow_history: int = 1000
    auto_save_workflows: bool = True

    # API Server
    api_host: str = "127.0.0.1"
    api_port: int = 8000
    api_workers: int = 1

    # Events
    max_event_history: int = 10000

    # Observability
    log_level: str = "INFO"
    metrics_enabled: bool = True

    def __post_init__(self):
        if self.db_path is None:
            self.db_path = str(Path(self.data_dir) / "kernel.db")


class SettingsManager:
    """Manages kernel settings from env vars and config files."""

    def __init__(self):
        self._settings: Optional[KernelSettings] = None

    def get_settings(self) -> KernelSettings:
        """Get or create settings."""
        if self._settings is None:
            self._settings = self._load_settings()
        return self._settings

    def _load_settings(self) -> KernelSettings:
        """Load settings from environment."""
        return KernelSettings(
            data_dir=os.getenv("AMOS_KERNEL_DATA_DIR", str(Path.home() / ".amos_kernel")),
            enable_law_validation=os.getenv("AMOS_KERNEL_DISABLE_LAWS", "false").lower() != "true",
            max_workflow_history=int(os.getenv("AMOS_KERNEL_MAX_HISTORY", "1000")),
            api_host=os.getenv("AMOS_KERNEL_API_HOST", "127.0.0.1"),
            api_port=int(os.getenv("AMOS_KERNEL_API_PORT", "8000")),
            log_level=os.getenv("AMOS_KERNEL_LOG_LEVEL", "INFO"),
        )

    def reload(self) -> None:
        """Reload settings from environment."""
        self._settings = self._load_settings()


# Global settings manager
_settings_manager = SettingsManager()


def get_settings() -> KernelSettings:
    """Get current kernel settings."""
    return _settings_manager.get_settings()


def reload_settings() -> None:
    """Reload settings from environment."""
    _settings_manager.reload()
