"""AMOS Logging Configuration
==========================

Production-grade logging setup for AMOS brain system.
Based on 2024 Python CLI best practices.

Usage:
    from amos_brain.logging_config import setup_logging
    logger = setup_logging(verbose=True)
    logger.info("Processing task")
    logger.error("Failed to connect", exc_info=True)
"""

import logging
import sys
from pathlib import Path
from typing import Optional


def setup_logging(
    verbose: bool = False, log_file: Optional[str] = None, component: str = "amos"
) -> logging.Logger:
    """Configure logging with console + optional file output.

    Args:
        verbose: Enable DEBUG level logging
        log_file: Optional file path for logs
        component: Component name for logger identification

    Returns:
        Configured logger instance
    """
    # Create logger
    logger = logging.getLogger(component)
    logger.setLevel(logging.DEBUG if verbose else logging.INFO)

    # Remove existing handlers (prevents duplicate logs)
    logger.handlers.clear()

    # Console handler with colored output
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG if verbose else logging.INFO)

    # Different formats for verbose vs normal
    if verbose:
        console_format = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s.%(funcName)s:%(lineno)d - %(message)s",
            datefmt="%H:%M:%S",
        )
    else:
        console_format = logging.Formatter("%(levelname)s: %(message)s")
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)

    # Optional file handler for persistent logs
    if log_file:
        # Ensure log directory exists
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_format = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s.%(funcName)s:%(lineno)d - %(message)s"
        )
        file_handler.setFormatter(file_format)
        logger.addHandler(file_handler)

    return logger


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for a specific component.

    Args:
        name: Component name (e.g., 'amos.brain', 'amos.cli')

    Returns:
        Logger instance
    """
    return logging.getLogger(name)


class LogContext:
    """Context manager for temporary logging level changes."""

    def __init__(self, logger: logging.Logger, level: int):
        self.logger = logger
        self.level = level
        self.original_level = logger.level

    def __enter__(self):
        self.logger.setLevel(self.level)
        return self.logger

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.logger.setLevel(self.original_level)
        return False


# Pre-configured loggers for common components
def get_brain_logger() -> logging.Logger:
    """Get logger for brain operations."""
    return get_logger("amos.brain")


def get_cli_logger() -> logging.Logger:
    """Get logger for CLI operations."""
    return get_logger("amos.cli")


def get_mcp_logger() -> logging.Logger:
    """Get logger for MCP server operations."""
    return get_logger("amos.mcp")


def get_coherence_logger() -> logging.Logger:
    """Get logger for coherence engine operations."""
    return get_logger("amos.coherence")


__all__ = [
    "setup_logging",
    "get_logger",
    "LogContext",
    "get_brain_logger",
    "get_cli_logger",
    "get_mcp_logger",
    "get_coherence_logger",
]
