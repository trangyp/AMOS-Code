# Stub to re-export from 14_INTERFACES
import sys
from pathlib import Path

interfaces_path = Path(__file__).parent.parent / "14_INTERFACES"
if str(interfaces_path) not in sys.path:
    sys.path.insert(0, str(interfaces_path))

from cli import AmosCLI, CommandHandler

__all__ = ["AmosCLI", "CommandHandler"]
