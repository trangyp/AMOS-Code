"""Cognitive Stack - Domain engine management and orchestration."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class DomainEngine:
    """A domain-specific cognitive engine."""

    name: str
    domain: str
    version: str
    description: str = ""
    core_principles: dict[str, str] = field(default_factory=dict)
    processing_pipeline: list[str] = field(default_factory=list)
    safety_constraints: dict[str, bool] = field(default_factory=dict)
    active: bool = True

    def process(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Process input through this domain engine."""
        # Check safety constraints
        for constraint, enabled in self.safety_constraints.items():
            if enabled and not self._check_constraint(constraint, input_data):
                return {
                    "error": f"Safety constraint violated: {constraint}",
                    "engine": self.name,
                    "status": "blocked",
                }

        # Apply processing pipeline
        result = input_data.copy()
        for step in self.processing_pipeline:
            result = self._apply_step(step, result)

        return {
            "engine": self.name,
            "domain": self.domain,
            "status": "success",
            "output": result,
            "principles_applied": list(self.core_principles.keys()),
        }

    def _check_constraint(self, constraint: str, data: dict[str, Any]) -> bool:
        """Check if input satisfies safety constraint."""
        # Placeholder: actual constraints would be domain-specific
        return True

    def _apply_step(self, step: str, data: dict[str, Any]) -> dict[str, Any]:
        """Apply a processing step."""
        # Placeholder: actual steps would be domain-specific
        data[f"step_{step}"] = "processed"
        return data


class CognitiveStack:
    """Manages and orchestrates domain-specific cognitive engines.

    Loads engines from:
    - 7_Intelligents (domain engines)
    - Cognitive_Stack (cognitive capabilities)
    """

    INTELLIGENCES = [
        "AMOS_Biology_And_Cognition_Engine",
        "AMOS_Design_Language_Engine",
        "AMOS_Deterministic_Logic_And_Law_Engine",
        "AMOS_Econ_Finance_Engine",
        "AMOS_Electrical_Power_Engine",
        "AMOS_Engineering_And_Mathematics_Engine",
        "AMOS_Mechanical_Structural_Engine",
        "AMOS_Numerical_Methods_Engine",
        "AMOS_Physics_Cosmos_Engine",
        "AMOS_Signal_Processing_Engine",
        "AMOS_Society_Culture_Engine",
        "AMOS_Strategy_Game_Engine",
    ]

    def __init__(self, core_path: str | None = None):
        self.core_path = core_path
        self.engines: dict[str, DomainEngine] = {}
        self._routing_table: dict[str, list[str]] = {}
        self._load_engines()

    def _load_engines(self) -> None:
        """Load engines from brain specifications."""
        # Initialize with default engines based on 7 Intelligences
        for intel_name in self.INTELLIGENCES:
            domain = self._extract_domain(intel_name)
            engine = DomainEngine(
                name=intel_name,
                domain=domain,
                version="v0",
                description=f"Engine for {domain} domain",
                core_principles={
                    "rule_of_2": "Compare complementary views",
                    "rule_of_4": "Map across four quadrants",
                },
                processing_pipeline=["interpret", "analyze", "synthesize", "validate"],
                safety_constraints={"no_harm": True, "verify_constraints": True},
            )
            self.engines[intel_name] = engine

        # Build routing table
        self._build_routing_table()

    def _extract_domain(self, engine_name: str) -> str:
        """Extract domain from engine name."""
        # Remove AMOS_ prefix and _Engine suffix
        name = engine_name.replace("AMOS_", "").replace("_Engine", "")
        return name.replace("_", " ")

    def _build_routing_table(self) -> None:
        """Build routing table for query-to-engine mapping."""
        keywords = {
            "biology": ["AMOS_Biology_And_Cognition_Engine"],
            "cognition": ["AMOS_Biology_And_Cognition_Engine"],
            "design": ["AMOS_Design_Language_Engine"],
            "logic": ["AMOS_Deterministic_Logic_And_Law_Engine"],
            "law": ["AMOS_Deterministic_Logic_And_Law_Engine"],
            "economics": ["AMOS_Econ_Finance_Engine"],
            "finance": ["AMOS_Econ_Finance_Engine"],
            "electrical": ["AMOS_Electrical_Power_Engine"],
            "power": ["AMOS_Electrical_Power_Engine"],
            "engineering": [
                "AMOS_Engineering_And_Mathematics_Engine",
                "AMOS_Mechanical_Structural_Engine",
            ],
            "math": ["AMOS_Engineering_And_Mathematics_Engine", "AMOS_Numerical_Methods_Engine"],
            "mechanical": ["AMOS_Mechanical_Structural_Engine"],
            "physics": ["AMOS_Physics_Cosmos_Engine"],
            "cosmos": ["AMOS_Physics_Cosmos_Engine"],
            "signal": ["AMOS_Signal_Processing_Engine"],
            "society": ["AMOS_Society_Culture_Engine"],
            "culture": ["AMOS_Society_Culture_Engine"],
            "strategy": ["AMOS_Strategy_Game_Engine"],
            "game": ["AMOS_Strategy_Game_Engine"],
        }
        self._routing_table = keywords

    def route_query(self, query: str) -> list[str]:
        """Determine which engines should handle a query."""
        query_lower = query.lower()
        matched_engines = set()

        for keyword, engines in self._routing_table.items():
            if keyword in query_lower:
                matched_engines.update(engines)

        # Default to a narrow general-purpose subset if no match
        if not matched_engines:
            fallback = [
                "AMOS_Deterministic_Logic_And_Law_Engine",
                "AMOS_Strategy_Game_Engine",
                "AMOS_Engineering_And_Mathematics_Engine",
            ]
            return [name for name in fallback if name in self.engines]

        return list(matched_engines)

    def execute(self, query: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
        """Execute query through appropriate engines."""
        engines_to_use = self.route_query(query)
        results = []

        for engine_name in engines_to_use:
            engine = self.engines.get(engine_name)
            if engine and engine.active:
                result = engine.process({"query": query, "context": context or {}})
                results.append(result)

        return {
            "query": query,
            "engines_used": engines_to_use,
            "results": results,
            "coverage": len(results) / len(engines_to_use) if engines_to_use else 0,
        }

    def get_engine(self, name: str) -> DomainEngine | None:
        """Get specific engine by name."""
        return self.engines.get(name)

    def list_engines(self) -> list[str]:
        """List all available engines."""
        return list(self.engines.keys())

    def enable_engine(self, name: str) -> bool:
        """Enable an engine."""
        if name in self.engines:
            self.engines[name].active = True
            return True
        return False

    def disable_engine(self, name: str) -> bool:
        """Disable an engine."""
        if name in self.engines:
            self.engines[name].active = False
            return True
        return False

    def get_domain_coverage(self) -> dict[str, list[str]]:
        """Get coverage by domain category."""
        coverage = {}
        for engine in self.engines.values():
            domain = engine.domain
            if domain not in coverage:
                coverage[domain] = []
            coverage[domain].append(engine.name)
        return coverage
