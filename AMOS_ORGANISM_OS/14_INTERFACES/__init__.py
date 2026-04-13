"""
14_INTERFACES — CLI, API, web dashboard and chat integration.

The user-facing interface layer for AMOS.
"""

from .cli import AmosCLI, CommandHandler
from .api_server import APIServer

__all__ = ["AmosCLI", "CommandHandler", "APIServer"]
