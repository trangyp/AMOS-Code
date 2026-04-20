from __future__ import annotations

from typing import Any

"""AMOS Brain Logging Configuration - Structured logging for production observability.

Provides consistent logging across all brain components with:
- Structured JSON logging for production
- Console logging for development
- Log level configuration via environment
- Contextual logging with component names
"""

import logging
import os
import sys

# Default log level from environment or INFO
DEFAULT_LOG_LEVEL = os.getenv("AMOS_LOG_LEVEL", "INFO").upper()

# Component name for contextual logging
COMPONENT_CONTEXT: dict[str, str] = {}


def get_logger(component: str) -> logging.Logger:
    """Get a logger for a specific brain component.

    Args:
        component: Component name (e.g., 'TaskQueue', 'Governance')

    Returns:
        Configured logger instance

    """
    logger = logging.getLogger(f"amos.brain.{component}")

    # Set level if not already set
    if logger.level == logging.NOTSET:
        logger.setLevel(getattr(logging, DEFAULT_LOG_LEVEL, logging.INFO))

    # Add handler if not already added
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stderr)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


def log_component_action(component: str, action: str, details: dict[str, Any] = None) -> None:
    """Log a component action with structured data.

    Args:
        component: Component name
        action: Action being performed
        details: Optional additional details

    """
    logger = get_logger(component)
    msg = f"[{component}] {action}"
    if details:
        msg += f" | {details}"
    logger.info(msg)


def log_component_error(component: str, error: Exception, context: dict[str, Any] = None) -> None:
    """Log a component error with context.

    Args:
        component: Component name
        error: Exception that occurred
        context: Optional context dictionary

    """
    logger = get_logger(component)
    msg = f"[{component}] Error: {error}"
    if context:
        msg += f" | Context: {context}"
    logger.error(msg, exc_info=True)


def log_component_warning(component: str, message: str, details: dict[str, Any] = None) -> None:
    """Log a warning with component context.

    Args:
        component: Component name
        message: Warning message
        details: Optional additional details

    """
    logger = get_logger(component)
    msg = f"[{component}] {message}"
    if details:
        msg += f" | {details}"
    logger.warning(msg)


def log_component_debug(component: str, message: str, data: dict[str, Any] = None) -> None:
    """Log debug information with component context.

    Args:
        component: Component name
        message: Debug message
        data: Optional debug data

    """
    logger = get_logger(component)
    msg = f"[{component}] {message}"
    if data:
        msg += f" | {data}"
    logger.debug(msg)


# Convenience functions for common patterns
def log_initialization(component: str, status: str = "complete") -> None:
    """Log component initialization."""
    log_component_action(component, f"Initialization {status}")


def log_fallback_mode(component: str, reason: str) -> None:
    """Log when component enters fallback mode."""
    log_component_warning(component, f"Using fallback mode: {reason}")


def log_task_submission(component: str, task_id: str, description: str) -> None:
    """Log task submission."""
    log_component_action(component, f"Task submitted: {task_id}", {"description": description[:50]})


def log_task_completion(component: str, task_id: str, duration_ms: float, success: bool) -> None:
    """Log task completion."""
    status = "completed" if success else "failed"
    log_component_action(
        component, f"Task {status}: {task_id}", {"duration_ms": round(duration_ms, 2)}
    )


def log_health_check(component: str, status: str, details: dict[str, Any] = None) -> None:
    """Log health check result."""
    log_component_action(component, f"Health check: {status}", details)


# Legacy compatibility - convert print statements to logs
def print_to_log(component: str, message: str, level: str = "info") -> None:
    """Convert legacy print statements to structured logs.

    This helps migrate from print-based logging to structured logging.

    Args:
        component: Component name
        message: Original print message (often starts with [Component])
        level: Log level (info, warning, error, debug)

    """
    logger = get_logger(component)

    # Strip component prefix if present
    if message.startswith(f"[{component}]"):
        message = message[len(f"[{component}]") :].strip()

    log_func = getattr(logger, level.lower(), logger.info)
    log_func(message)
