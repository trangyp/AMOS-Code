"""INTERFACES module — Alias for 14_INTERFACES"""

import sys
from pathlib import Path

# Add 14_INTERFACES to path
interfaces_path = Path(__file__).parent.parent / "14_INTERFACES"
if str(interfaces_path) not in sys.path:
    sys.path.insert(0, str(interfaces_path))

# Import and re-export
try:
    from api_server import APIServer
    from cli import AmosCLI, CommandHandler

    __all__ = ["AmosCLI", "CommandHandler", "APIServer"]
except ImportError:
    __all__ = []
