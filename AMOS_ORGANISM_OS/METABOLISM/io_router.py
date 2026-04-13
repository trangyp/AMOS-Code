# Stub to re-export from 07_METABOLISM
import sys
from pathlib import Path

metabolism_path = Path(__file__).parent.parent / "07_METABOLISM"
if str(metabolism_path) not in sys.path:
    sys.path.insert(0, str(metabolism_path))

from io_router import (
    IORouter,
    Route,
    RouteConfig,
    get_io_router,
)

__all__ = [
    "IORouter",
    "Route",
    "RouteConfig",
    "get_io_router",
]
