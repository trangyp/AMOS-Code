"""
Repo Doctor Ω∞∞∞∞∞∞ - Complete Hard Invariants Module.

Core invariants implemented (18 surfaces):
I_parse, I_import, I_api, I_entry, I_pack, I_runtime,
I_persist, I_status, I_tests, I_security, I_history,
I_migration, I_perf, I_obs, I_auth, I_env, I_artifact

RepoValid = ∧n I_n (18 invariants - complete)
"""

# Import base classes
# Import all 12 hard invariants
from .api import APIInvariant
from .artifact import ArtifactInvariant
from .authorization import AuthorizationInvariant
from .base import Invariant, InvariantGroup, InvariantResult, InvariantSeverity

# Import engine
from .engine import InvariantEngine
from .entrypoints import EntrypointInvariant
from .environment import EnvironmentInvariant
from .history import HistoryInvariant
from .imports import ImportInvariant

# Import 6 Phase 1-2 invariants
from .migration import MigrationInvariant
from .observability import ObservabilityInvariant
from .packaging import PackagingInvariant
from .parse import ParseInvariant
from .performance import PerformanceInvariant
from .persistence import PersistenceInvariant
from .runtime import RuntimeInvariant
from .security import SecurityInvariant
from .status import StatusInvariant
from .tests import TestsInvariant
from .types import TypeInvariant

__all__ = [
    # Base
    "Invariant",
    "InvariantGroup",
    "InvariantResult",
    "InvariantSeverity",
    # Engine
    "InvariantEngine",
    # 12 Hard Invariants
    "ParseInvariant",
    "ImportInvariant",
    "TypeInvariant",
    "APIInvariant",
    "EntrypointInvariant",
    "PackagingInvariant",
    "RuntimeInvariant",
    "PersistenceInvariant",
    "StatusInvariant",
    "TestsInvariant",
    "SecurityInvariant",
    "HistoryInvariant",
    # Phase 1-2 additions
    "MigrationInvariant",
    "PerformanceInvariant",
    "ObservabilityInvariant",
    "AuthorizationInvariant",
    "EnvironmentInvariant",
    "ArtifactInvariant",
]
