#!/usr/bin/env python3
"""AMOS Web Interface

Web-facing API and dashboard interfaces.
"""

from dataclasses import dataclass
from typing import Any


@dataclass
class WebEndpoint:
    """Web API endpoint definition."""
    path: str
    method: str
    description: str
    requires_auth: bool = True


class WebInterface:
    """Web interface manager."""
    
    def __init__(self):
        self.endpoints: list[WebEndpoint] = [
            WebEndpoint("/health", "GET", "System health check", False),
            WebEndpoint("/status", "GET", "Full system status", True),
            WebEndpoint("/brain/think", "POST", "Execute brain cognition", True),
            WebEndpoint("/repos", "GET", "List 6-repo status", True),
            WebEndpoint("/canon/verify", "GET", "Verify canonical structure", True),
        ]
    
    def list_endpoints(self) -> list[WebEndpoint]:
        """List all web endpoints."""
        return self.endpoints


def get_web_interface() -> WebInterface:
    """Get web interface instance."""
    return WebInterface()
