"""AMOS SDK - Python client for AMOS Brain API.

Official Python SDK for interacting with the AMOS Brain API at neurosyncai.tech

Usage:
    import amos_sdk
    
    client = amos_sdk.Client(api_key="your_key")
    result = client.think("What is the next logical step?")
    print(result.content)
"""
from __future__ import annotations

__version__ = "1.0.0"
__author__ = "Trang Phan"

from .client import Client, AsyncClient
from .exceptions import (
    AmosError,
    AuthenticationError,
    RateLimitError,
    ServerError,
    ValidationError,
)
from .models import (
    ThinkResult,
    DecideResult,
    AmoslResult,
    QueryRecord,
    Stats,
)

__all__ = [
    "Client",
    "AsyncClient",
    "AmosError",
    "AuthenticationError",
    "RateLimitError",
    "ServerError",
    "ValidationError",
    "ThinkResult",
    "DecideResult",
    "AmoslResult",
    "QueryRecord",
    "Stats",
]
