"""AMOS SDK Data Models.

Type definitions for API responses.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Dict, Any, Optional


@dataclass
class ThinkResult:
    """Result from a think operation."""
    content: str
    reasoning: List[str]
    confidence: float
    law_compliant: bool
    domain: str


@dataclass
class DecideResult:
    """Result from a decide operation."""
    approved: bool
    risk_level: str
    reasoning: str
    decision_id: str


@dataclass
class AmoslResult:
    """Result from AMOSL compilation."""
    success: bool
    invariants_valid: bool
    violations: List[str]
    ir_stats: Dict[str, Any]


@dataclass
class QueryRecord:
    """Single query history record."""
    id: int
    endpoint: str
    query: str
    domain: str
    confidence: str
    law_compliant: bool
    processing_time_ms: int
    created_at: str


@dataclass
class Stats:
    """Usage statistics."""
    total_requests: int
    avg_response_time_ms: float
    success_rate_percent: float
    period_days: int
