"""Ingest modules for external substrate integration."""
from __future__ import annotations

from .api_substrate import APIDiscrepancy, APISubstrate, APISymbol
from .entrypoint_substrate import (
    EntrypointDeclaration,
    EntrypointSubstrate,
    EntrypointValidation,
)
from .import_substrate import ImportResolution, ImportStatement, ImportSubstrate
from .packaging_substrate import PackagingIssue, PackagingSubstrate, PackagingValidation
from .security_substrate import SecurityAnalysis, SecurityFinding, SecuritySubstrate
from .status_substrate import StatusClaim, StatusSubstrate, StatusValidation
from .test_substrate import TestCase, TestResult, TestSubstrate
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
    "PackagingSubstrate",
    "PackagingIssue",
    "PackagingValidation",
    "SecuritySubstrate",
    "SecurityFinding",
    "SecurityAnalysis",
    "StatusSubstrate",
    "StatusClaim",
    "StatusValidation",
    "TestSubstrate",
    "TestCase",
    "TestResult",
    "TreeSitterSubstrate",
    "FileParseResult",
    "ParseError",
]
