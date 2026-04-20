"""INTERFACES module — Alias for 14_INTERFACES"""

import importlib.util
from pathlib import Path

# Load modules from 14_INTERFACES using importlib
_14_INTERFACES_PATH = Path(__file__).parent.parent / "14_INTERFACES"

# Import and re-export
try:
    # api_server
    _spec_api = importlib.util.spec_from_file_location(
        "_api_srv", _14_INTERFACES_PATH / "api_server.py"
    )
    _mod_api = importlib.util.module_from_spec(_spec_api)
    _spec_api.loader.exec_module(_mod_api)
    APIServer = _mod_api.APIServer

    # cli
    _spec_cli = importlib.util.spec_from_file_location("_cli_mod", _14_INTERFACES_PATH / "cli.py")
    _mod_cli = importlib.util.module_from_spec(_spec_cli)
    _spec_cli.loader.exec_module(_mod_cli)
    AmosCLI = _mod_cli.AmosCLI
    CommandHandler = _mod_cli.CommandHandler

    __all__ = ["AmosCLI", "CommandHandler", "APIServer"]
except Exception:
    __all__ = []
