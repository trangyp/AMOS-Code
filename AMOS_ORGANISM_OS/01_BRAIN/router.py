"""
System Router — Routes decisions to appropriate subsystems.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from pathlib import Path
import json


@dataclass
class RoutingDecision:
    """A decision to route to a specific subsystem."""
    target: str              # Subsystem code (e.g., "06_MUSCLE")
    action: str              # Action to perform
    params: Dict[str, Any]   # Parameters for the action
    priority: int = 5        # 1-10, lower is more urgent
    reason: str = ""         # Why this routing decision was made


class SystemRouter:
    """
    Routes tasks to the appropriate AMOS subsystem.

    Primary loop routing:
    01_BRAIN -> 02_SENSES -> 05_SKELETON -> 08_WORLD_MODEL ->
    12_QUANTUM_LAYER -> 06_MUSCLE -> 07_METABOLISM -> 01_BRAIN
    """

    PRIMARY_LOOP = [
        "01_BRAIN",
        "02_SENSES",
        "05_SKELETON",
        "08_WORLD_MODEL",
        "12_QUANTUM_LAYER",
        "06_MUSCLE",
        "07_METABOLISM",
    ]

    SUPPORTING_ROUTES = {
        "risk": ["03_IMMUNE", "11_LEGAL_BRAIN", "04_BLOOD"],
        "life": ["10_LIFE_ENGINE", "04_BLOOD", "02_SENSES"],
        "social": ["09_SOCIAL_ENGINE", "08_WORLD_MODEL", "10_LIFE_ENGINE"],
        "factory": ["13_FACTORY", "01_BRAIN", "05_SKELETON", "07_METABOLISM"],
        "interfaces": ["14_INTERFACES", "01_BRAIN", "06_MUSCLE", "07_METABOLISM"],
    }

    ACTION_SUBSYSTEM_MAP = {
        # Brain actions
        "reason": "01_BRAIN",
        "plan": "01_BRAIN",
        "decide": "01_BRAIN",
        "route": "01_BRAIN",

        # Sense actions
        "scan": "02_SENSES",
        "monitor": "02_SENSES",
        "detect": "02_SENSES",

        # Skeleton actions
        "validate": "05_SKELETON",
        "check_constraints": "05_SKELETON",
        "enforce_rules": "05_SKELETON",

        # Immune actions
        "audit": "03_IMMUNE",
        "check_safety": "03_IMMUNE",
        "scan_threats": "03_IMMUNE",

        # Blood actions
        "budget": "04_BLOOD",
        "forecast": "04_BLOOD",
        "allocate": "04_BLOOD",

        # Muscle actions
        "execute": "06_MUSCLE",
        "code": "06_MUSCLE",
        "deploy": "06_MUSCLE",
        "run": "06_MUSCLE",

        # Metabolism actions
        "transform": "07_METABOLISM",
        "route_io": "07_METABOLISM",
        "cleanup": "07_METABOLISM",

        # World Model actions
        "model": "08_WORLD_MODEL",
        "forecast_world": "08_WORLD_MODEL",
        "analyze_sectors": "08_WORLD_MODEL",

        # Social Engine actions
        "negotiate": "09_SOCIAL_ENGINE",
        "influence": "09_SOCIAL_ENGINE",
        "analyze_social": "09_SOCIAL_ENGINE",

        # Life Engine actions
        "cycle": "10_LIFE_ENGINE",
        "restore": "10_LIFE_ENGINE",
        "balance": "10_LIFE_ENGINE",

        # Legal Brain actions
        "check_compliance": "11_LEGAL_BRAIN",
        "review_contract": "11_LEGAL_BRAIN",
        "scan_regulatory": "11_LEGAL_BRAIN",

        # Quantum Layer actions
        "time": "12_QUANTUM_LAYER",
        "probability": "12_QUANTUM_LAYER",
        "sync": "12_QUANTUM_LAYER",

        # Factory actions
        "create_agent": "13_FACTORY",
        "upgrade": "13_FACTORY",
        "quality_check": "13_FACTORY",

        # Interface actions
        "cli": "14_INTERFACES",
        "api": "14_INTERFACES",
        "dashboard": "14_INTERFACES",
        "chat": "14_INTERFACES",
    }

    def __init__(self, organism_root: Optional[Path] = None):
        self.organism_root = organism_root
        self._history: List[RoutingDecision] = []

    def route(self, action: str, params: Dict[str, Any] = None,
              priority: int = 5, reason: str = "") -> RoutingDecision:
        """Route an action to the appropriate subsystem."""
        subsystem = self.ACTION_SUBSYSTEM_MAP.get(action, "01_BRAIN")
        decision = RoutingDecision(
            target=subsystem,
            action=action,
            params=params or {},
            priority=priority,
            reason=reason or f"Action '{action}' mapped to {subsystem}",
        )
        self._history.append(decision)
        return decision

    def route_to_primary(self, current: str) -> Optional[str]:
        """Get next subsystem in primary loop."""
        try:
            idx = self.PRIMARY_LOOP.index(current)
            next_idx = (idx + 1) % len(self.PRIMARY_LOOP)
            return self.PRIMARY_LOOP[next_idx]
        except ValueError:
            return None

    def get_supporting(self, category: str) -> List[str]:
        """Get supporting subsystems for a category."""
        return self.SUPPORTING_ROUTES.get(category, [])

    def suggest_parallel(self, action: str) -> List[str]:
        """Suggest subsystems that could work in parallel."""
        # Risk-related actions should include Immune
        if any(x in action for x in ["deploy", "execute", "code", "run"]):
            return ["03_IMMUNE", "11_LEGAL_BRAIN"]
        # Financial actions should include Blood
        if any(x in action for x in ["budget", "cost", "resource"]):
            return ["04_BLOOD"]
        # Interface actions
        if any(x in action for x in ["cli", "api", "chat"]):
            return ["14_INTERFACES"]
        return []

    def get_history(self, n: int = 10) -> List[RoutingDecision]:
        """Get recent routing decisions."""
        return self._history[-n:]

    def export_wiring(self, filepath: Path):
        """Export wiring configuration."""
        data = {
            "primary_loop": self.PRIMARY_LOOP,
            "supporting_routes": self.SUPPORTING_ROUTES,
            "action_map": self.ACTION_SUBSYSTEM_MAP,
        }
        filepath.write_text(json.dumps(data, indent=2))
