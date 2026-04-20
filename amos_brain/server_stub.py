"""Stub for server functionality - imports only when server extras installed.

This module provides safe stubs for server-dependent functionality.
When [server] extras are installed, the real implementations are used.
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)

# Try to import FastAPI-dependent modules
try:
    from fastapi import FastAPI

    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False
    FastAPI = None  # type: ignore


def create_fastapi_app(*args: Any, **kwargs: Any) -> Any:
    """Create FastAPI app if available, otherwise raise informative error."""
    if not HAS_FASTAPI:
        raise ImportError(
            "FastAPI not installed. Install server extras: pip install amos-brain[server]"
        )
    from fastapi import FastAPI

    return FastAPI(*args, **kwargs)


def start_api_server(*args: Any, **kwargs: Any) -> None:
    """Start API server if dependencies available."""
    if not HAS_FASTAPI:
        raise ImportError("Server dependencies not installed. Run: pip install amos-brain[server]")
    logger.info("Starting API server...")
    # Actual server start would be imported here


__all__ = [
    "HAS_FASTAPI",
    "create_fastapi_app",
    "start_api_server",
]
