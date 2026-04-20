"""AMOS Platform SDK - Python client for AMOS API Gateway.

This SDK provides synchronous and asynchronous clients for connecting
to the AMOS Platform API Gateway (amos-platform).

Usage:
    from amos_platform_sdk import AMOSClient

    # Synchronous
    client = AMOSClient(api_key="your_key", base_url="http://localhost:8000")
    response = client.chat("Hello, AMOS!")

    # Asynchronous
    async with AMOSClient(api_key="your_key") as client:
        response = await client.chat("Hello, AMOS!")
"""

__version__ = "1.0.0"

from amos_platform_sdk.client import AMOSClient, AsyncAMOSClient
from amos_platform_sdk.exceptions import (
    AMOSAPIError,
    AMOSAuthenticationError,
    AMOSNotFoundError,
    AMOSRateLimitError,
    AMOSValidationError,
)

__all__ = [
    "AMOSClient",
    "AsyncAMOSClient",
    "AMOSAPIError",
    "AMOSAuthenticationError",
    "AMOSValidationError",
    "AMOSNotFoundError",
    "AMOSRateLimitError",
]
