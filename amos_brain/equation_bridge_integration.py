#!/usr/bin/env python3
"""Equation Bridge Integration - Connects SuperBrain Equation Bridge.

Architecture Pattern: Adapter + Facade
- Adapts amos_superbrain_equation_bridge to amos_brain interfaces
- Provides canonical access to 145+ equations across 33 domains
- Integrates with SuperBrainRuntime governance

Author: AMOS SuperBrain
Version: 7.0.0
Date: April 2026
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional

# Import from package-local module (no sys.path hack needed)
from .superbrain_equation_bridge import (
    AMOSSuperBrainBridge,
    Domain,
    MathematicalPattern,
)


class EquationDomain(Enum):
    """Canonical domain categories for AMOS Brain integration."""

    ML_AI = "machine_learning"
    DISTRIBUTED_SYSTEMS = "distributed_systems"
    PROGRAMMING_LANGUAGES = "programming_languages"
    DATA_STRUCTURES = "data_structures"
    SYSTEMS_INFRA = "systems_infrastructure"
    NETWORKING = "networking"
    DATABASES = "databases"
    GRAPH_ALGORITHMS = "graph_algorithms"
    INFORMATION_RETRIEVAL = "information_retrieval"
    COMPILERS = "compilers"
    CRYPTOGRAPHY = "cryptography"
    COMPUTER_GRAPHICS = "computer_graphics"
    QUANTUM_COMPUTING = "quantum_computing"
    CONTROL_THEORY = "control_theory"
    INFORMATION_THEORY = "information_theory"
    COMPUTABILITY = "computability"
    ROBOTICS = "robotics"
    COMPUTER_VISION = "computer_vision"
    SIGNAL_PROCESSING = "signal_processing"
    NLP = "nlp"
    GAME_PHYSICS = "game_physics"
    REAL_TIME_SYSTEMS = "real_time_systems"
    DIFFERENTIAL_PRIVACY = "differential_privacy"
    EPIDEMIOLOGY = "epidemiology"
    FEDERATED_LEARNING = "federated_learning"
    TPU_XLA = "tpu_xla"
    EFFECT_SYSTEMS = "effect_systems"
    REFINEMENT_TYPES = "refinement_types"
    PROBABILISTIC_PROGRAMMING = "probabilistic_programming"
    NEURAL_VERIFICATION = "neural_verification"
    CRDTS = "crdts"


@dataclass
class EquationComputeRequest:
    """Request to compute an equation."""

    equation_name: str
    inputs: dict[str, Any]
    validate_invariants: bool = True
    track_in_history: bool = True


@dataclass
class EquationComputeResponse:
    """Response from equation computation."""

    equation_name: str
    outputs: dict[str, Any]
    invariants_valid: bool
    invariant_violations: list[str]
    execution_time_ms: float
    pattern_detected: str
    cross_domain_links: list[str]
    success: bool
    error: Optional[str] = None


class EquationBridgeIntegration:
    """Integration layer between SuperBrainRuntime and Equation Bridge.

    This class provides:
    1. Canonical access to all 145+ equations
    2. Integration with AMOS governance (ActionGate, MemoryGovernance)
    3. Cross-domain pattern analysis
    4. Equation registry management
    """

    def __init__(self) -> None:
        self._bridge = AMOSSuperBrainBridge()
        self._execution_history: list[EquationComputeResponse] = []
        self._initialized = False

    def initialize(self) -> bool:
        """Initialize the equation bridge integration."""
        try:
            self._initialized = True
            return True
        except Exception as e:
            print(f"Equation Bridge initialization failed: {e}")
            return False

    def compute(self, request: EquationComputeRequest) -> EquationComputeResponse:
        """Execute equation computation with governance integration."""
        try:
            # Execute through the bridge
            result = self._bridge.compute(request.equation_name, request.inputs)

            response = EquationComputeResponse(
                equation_name=result.equation_name,
                outputs=result.outputs,
                invariants_valid=result.invariants_valid,
                invariant_violations=result.invariant_violations,
                execution_time_ms=result.execution_time_ms,
                pattern_detected=(
                    result.pattern_detected.value if result.pattern_detected else None
                ),
                cross_domain_links=result.cross_domain_links,
                success=True,
            )

            if request.track_in_history:
                self._execution_history.append(response)

            return response

        except Exception as e:
            return EquationComputeResponse(
                equation_name=request.equation_name,
                outputs={},
                invariants_valid=False,
                invariant_violations=[str(e)],
                execution_time_ms=0.0,
                pattern_detected=None,
                cross_domain_links=[],
                success=False,
                error=str(e),
            )

    def list_equations(self, domain: Optional[str] = None) -> list[str]:
        """List available equations, optionally filtered by domain."""
        if domain:
            try:
                dom = Domain(domain)
                return self._bridge.registry.get_by_domain(dom)
            except ValueError:
                return []
        return list(self._bridge.registry.equations.keys())

    def get_equation_info(self, equation_name: str) -> dict[str, Any]:
        """Get metadata for an equation."""
        if equation_name not in self._bridge.registry.metadata:
            return None

        meta = self._bridge.registry.metadata[equation_name]
        return {
            "name": meta.name,
            "domain": meta.domain.value,
            "pattern": meta.pattern.value,
            "formula": meta.formula,
            "description": meta.description,
            "invariants": meta.invariants,
            "phase": meta.phase,
            "hash": self._bridge.registry.generate_equation_hash(equation_name),
        }

    def get_pattern_analysis(self) -> dict[str, Any]:
        """Get cross-domain pattern analysis."""
        return self._bridge.get_pattern_analysis()

    def batch_compute(
        self, requests: list[EquationComputeRequest]
    ) -> list[EquationComputeResponse]:
        """Execute multiple equation computations."""
        return [self.compute(req) for req in requests]

    def get_execution_history(self, limit: int = 100) -> list[EquationComputeResponse]:
        """Get recent execution history."""
        return self._execution_history[-limit:]

    def search_by_pattern(self, pattern: str) -> list[str]:
        """Search equations by mathematical pattern."""
        try:
            pat = MathematicalPattern(pattern)
            return self._bridge.registry.get_by_pattern(pat)
        except ValueError:
            return []

    def export_knowledge(self) -> dict[str, Any]:
        """Export equation knowledge for AMOS knowledge loader."""
        return self._bridge.export_to_amos_knowledge()


# Singleton instance for AMOS Brain integration
_equation_bridge_instance: Optional[EquationBridgeIntegration] = None


def get_equation_bridge() -> EquationBridgeIntegration:
    """Get the canonical EquationBridgeIntegration instance."""
    global _equation_bridge_instance
    if _equation_bridge_instance is None:
        _equation_bridge_instance = EquationBridgeIntegration()
    return _equation_bridge_instance


def compute_equation(
    equation_name: str, inputs: dict[str, Any], validate: bool = True
) -> EquationComputeResponse:
    """Convenience function to compute an equation."""
    bridge = get_equation_bridge()
    request = EquationComputeRequest(
        equation_name=equation_name, inputs=inputs, validate_invariants=validate
    )
    return bridge.compute(request)


# Export all equation functionality
__all__ = [
    "EquationBridgeIntegration",
    "EquationComputeRequest",
    "EquationComputeResponse",
    "EquationDomain",
    "get_equation_bridge",
    "compute_equation",
]
