"""
Repo Doctor Ω∞ - Hard Invariants Module

Core invariants implemented:
I_parse, I_import, I_api

RepoValid = ∧n I_n (3 invariants currently)
"""

# Import only implemented invariants
from .api import APIInvariant
from .base import Invariant, InvariantResult, InvariantSeverity
from .imports import ImportInvariant
from .parse import ParseInvariant

__all__ = [
    "Invariant",
    "InvariantResult",
    "InvariantSeverity",
    "InvariantEngine",
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
]
