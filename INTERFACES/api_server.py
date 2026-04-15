"""API Server stub for INTERFACES package."""

from typing import Any, Callable


class APIServer:
    """API server for AMOS system."""

    def __init__(self, host: str = "localhost", port: int = 8000):
        self.host = host
        self.port = port
        self.routes: dict[str, Callable] = {}

    def route(self, path: str, handler: Callable) -> None:
        """Register API route."""
        self.routes[path] = handler

    def start(self) -> None:
        """Start API server."""
        print(f"API server would start on {self.host}:{self.port}")

    def stop(self) -> None:
        """Stop API server."""
        print("API server would stop")


def create_server(host: str = "localhost", port: int = 8000) -> APIServer:
    """Create API server instance."""
    return APIServer(host, port)


__all__ = ["APIServer", "create_server"]
