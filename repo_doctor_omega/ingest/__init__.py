"""Ingest modules for external substrate integration."""
from __future__ import annotations

from .api_substrate import APIDiscrepancy, APISubstrate, APISymbol
from .entrypoint_substrate import (
    EntrypointDeclaration,
    EntrypointSubstrate,
    EntrypointValidation,
)
from .import_substrate import ImportResolution, ImportStatement, ImportSubstrate
from .treesitter_substrate import FileParseResult, ParseError, TreeSitterSubstrate

__all__ = [
    "APISubstrate",
    "APISymbol",
    "APIDiscrepancy",
    "EntrypointSubstrate",
    "EntrypointDeclaration",
    "EntrypointValidation",
    "ImportSubstrate",
    "ImportStatement",
    "ImportResolution",
    "TreeSitterSubstrate",
    "FileParseResult",
    "ParseError",
]
