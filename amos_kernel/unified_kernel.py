"""
Unified AMOS Kernel (UAK)

Integrates semantic and numeric kernels into one lawful system.

Architecture:
    Semantic Kernel (L0-L5)     Numeric Kernel (CNK)
    -----------------------     ---------------------
    - Intent parsing              - Calculations
    - Ambiguity resolution        - Scoring
    - Planning                    - Routing
    - Explanation                 - Invariant eval
    - Governance                  - Vectorized ops

    Event-Driven Transition Engine (glue)
    -------------------------------------
    event -> semantic_interp -> numeric_compute -> commit

This is the "one shared kernel" the user requested.
Not reinstantiated. Not rebuilt. Kept alive across cycles.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional

# Numeric kernel imports
from amos_kernel.compiled_numeric_kernel import (
    CompiledState,
    create_initial_state,
    get_compiled_numeric_kernel,
)

# Event-driven engine
from amos_kernel.event_driven_transitions import (
    StateEvent,
    get_event_driven_engine,
)

# Semantic kernel imports
from amos_kernel.L0_universal_law_kernel import UniversalLawKernel
from amos_kernel.L1_deterministic_core import DeterministicCore
from amos_kernel.L2_universal_state_model import StateTensor, UniversalStateModel
from amos_kernel.L3_interaction_engine import InteractionEngine
from amos_kernel.L4_self_observer import SelfObserver
from amos_kernel.L5_repair_executor import RepairExecutor

# ============================================================================
# Unified State
# ============================================================================


@dataclass
class UnifiedState:
    """
    Combined semantic and numeric state.

    Both representations are kept in sync.
    Semantic: StateTensor (for reasoning)
    Numeric: CompiledState (for fast compute)
    """

    # Semantic state (L2)
    semantic: StateTensor

    # Numeric state (CNK)
    numeric: CompiledState

    # Synchronization timestamp
    last_sync: float = field(default_factory=lambda: datetime.now(UTC).timestamp())

    def is_fresh(self, threshold_ms: float = 100.0) -> bool:
        """Check if state is fresh."""
        age_ms = (datetime.now(UTC).timestamp() - self.last_sync) * 1000
        return age_ms < threshold_ms


# ============================================================================
# Unified Kernel
# ============================================================================


class UnifiedAmosKernel:
    """
    The one shared kernel.

    Not reinstantiated. Not rebuilt. Kept alive across cycles.

    Combines:
    - Semantic kernel (L0-L5): For interpretation, planning, governance
    - Numeric kernel (CNK): For calculations, scoring, routing
    - Event engine: For event-driven transitions

    Usage:
        kernel = get_unified_kernel()
        kernel.initialize()
        result = kernel.process_event(event)
    """

    _instance: Optional[UnifiedAmosKernel] = None

    def __new__(cls) -> UnifiedAmosKernel:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        if self._initialized:
            return

        # Semantic kernel components
        self._law_kernel = UniversalLawKernel()
        self._deterministic_core = DeterministicCore()
        self._state_model = UniversalStateModel()
        self._interaction_engine = InteractionEngine()
        self._self_observer = SelfObserver()
        self._repair_executor = RepairExecutor()

        # Numeric kernel
        self._numeric_kernel = get_compiled_numeric_kernel()

        # Event-driven engine
        self._event_engine = get_event_driven_engine()

        # Unified state
        self._unified_state: Optional[UnifiedState] = None

        # Configuration
        self._config = {
            "semantic_enabled": True,
            "numeric_enabled": True,
            "event_driven": True,
            "cache_projections": True,
            "early_invariant_check": True,
        }

        # Statistics
        self._stats = {
            "total_cycles": 0,
            "semantic_cycles": 0,
            "numeric_cycles": 0,
            "cache_hits": 0,
            "avg_cycle_ms": 0.0,
        }

        self._initialized = True

    # ========================================================================
    # Initialization
    # ========================================================================

    def initialize(self, initial_data: Optional[dict[str, Any]] = None) -> bool:
        """
        Initialize the unified kernel.

        Creates both semantic and numeric initial states.
        Called ONCE at system startup.
        """
        if initial_data is None:
            initial_data = {
                "system_load": 0.0,
                "health_score": 1.0,
                "paths": {"claimed": "/", "actual": "/"},
            }

        # Create semantic state
        semantic_state = self._state_model.normalize(initial_data)

        # Create numeric state
        numeric_state = create_initial_state(tensor_shape=(4, 8))

        # Sync them
        self._unified_state = UnifiedState(
            semantic=semantic_state,
            numeric=numeric_state,
        )

        # Initialize event engine with numeric state
        self._event_engine.initialize(numeric_state)

        return True

    # ========================================================================
    # Main Entry Point
    # ========================================================================

    async def process_event(self, event: StateEvent) -> dict[str, Any]:
        """
        Main entry point for all processing.

        Pipeline:
            1. Semantic interpretation (if needed)
            2. Numeric transition (fast path)
            3. State synchronization
            4. Result projection

        This is where the magic happens:
        - Semantic work happens ONCE at entry
        - Numeric work happens in compiled fast path
        - State stays synchronized
        """
        start_time = time.perf_counter()
        self._stats["total_cycles"] += 1

        # Route based on event type
        if event.event_type in ("query", "explain", "plan"):
            # Semantic-heavy events go through semantic kernel
            result = await self._semantic_path(event)
            self._stats["semantic_cycles"] += 1
        else:
            # Numeric events go through numeric kernel (fast path)
            result = await self._numeric_path(event)
            self._stats["numeric_cycles"] += 1

        # Update timing stats
        cycle_ms = (time.perf_counter() - start_time) * 1000
        self._stats["avg_cycle_ms"] = self._stats["avg_cycle_ms"] * 0.9 + cycle_ms * 0.1

        return result

    async def emit(
        self,
        event_type: str,
        source: str,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        """Convenience method to emit and process event."""
        event = StateEvent(
            event_id=f"{source}:{datetime.now(UTC).timestamp()}",
            event_type=event_type,
            source=source,
            timestamp=datetime.now(UTC).timestamp(),
            payload=payload,
        )
        return await self.process_event(event)

    # ========================================================================
    # Processing Paths
    # ========================================================================

    async def _semantic_path(self, event: StateEvent) -> dict[str, Any]:
        """
        Semantic processing path.

        For events requiring interpretation, planning, explanation.
        Uses L0-L5 semantic kernel.
        """
        if self._unified_state is None:
            return {"error": "Kernel not initialized"}

        # 1. Update semantic state from event
        semantic_data = {
            "system_load": event.payload.get("load", 0.0),
            "health_score": self._unified_state.semantic.integrity.get("health_score", 1.0),
            "paths": event.payload.get("paths", {}),
        }

        updated_semantic = self._state_model.normalize(semantic_data)

        # 2. Run through interaction engine
        internal = {"mu": updated_semantic.mu, "nu": updated_semantic.nu}
        external = {"beta": updated_semantic.beta, "context": event.payload}

        interaction = self._interaction_engine.operate(internal, external)

        # 3. Validate through law kernel
        action = {"type": event.event_type, "payload": event.payload}
        validation = self._law_kernel.validate_invariants(updated_semantic, action)

        # 4. Apply deterministic transition
        inputs = {"internal": internal, "external": external, "interaction": interaction}
        transition_result = self._deterministic_core.transition(
            state=updated_semantic.to_dict(),
            inputs=inputs,
            constraints={"semantic": True},
        )

        # 5. Sync to numeric state
        if transition_result.success and transition_result.value:
            await self._sync_semantic_to_numeric(updated_semantic, transition_result.value)

        return {
            "success": transition_result.success,
            "validation_passed": validation.success if hasattr(validation, "success") else False,
            "interaction": interaction,
            "state_hash": updated_semantic.canonical_hash,
            "cycle_type": "semantic",
        }

    async def _numeric_path(self, event: StateEvent) -> dict[str, Any]:
        """
        Numeric processing path (FAST).

        For signal, control, command events.
        Uses compiled numeric kernel directly.
        """
        # Pass to event-driven engine
        result = await self._event_engine.emit_event(event)

        if result is None:
            return {"error": "Event processing failed", "cycle_type": "numeric"}

        # Sync numeric result back to semantic state
        if result.success and result.new_state:
            await self._sync_numeric_to_semantic(result.new_state)

        return {
            "success": result.success,
            "cache_hit": result.cache_hit,
            "compute_time_ms": result.compute_time_ms,
            "invariant_passed": result.invariant_result.passed,
            "state_hash": result.new_state.canonical_hash if result.new_state else None,
            "cycle_type": "numeric",
        }

    # ========================================================================
    # State Synchronization
    # ========================================================================

    async def _sync_semantic_to_numeric(
        self, semantic: StateTensor, semantic_result: dict[str, Any]
    ) -> None:
        """Sync semantic state changes to numeric state."""
        if self._unified_state is None:
            return

        # Convert semantic tensor to numeric tensor
        # This is a projection - we extract numeric features
        import numpy as np

        # Extract features from semantic state
        mu_vec = np.array(
            [
                semantic.mu.get("load", 0.0),
                semantic.mu.get("stress", 0.0),
                semantic.mu.get("health_score", 1.0),
            ]
        )

        nu_vec = np.array(
            [
                semantic.nu.get("prediction_error", 0.0),
                semantic.nu.get("cognitive_load", 0.0),
                semantic.nu.get("contradiction_score", 0.0),
            ]
        )

        alpha_vec = np.array(
            [
                semantic.alpha.get("policy_state", 0),
                semantic.alpha.get("system_ready", 0),
            ]
        )

        beta_vec = np.array(
            [
                semantic.beta.get("stable", 1.0),
                semantic.beta.get("risk", 0.0),
            ]
        )

        # Pad to match tensor shape
        def pad_to(vec: np.ndarray, target_len: int) -> np.ndarray:
            if len(vec) < target_len:
                return np.pad(vec, (0, target_len - len(vec)))
            return vec[:target_len]

        target_len = self._unified_state.numeric.tensor.shape[1]
        new_tensor = np.array(
            [
                pad_to(mu_vec, target_len),
                pad_to(nu_vec, target_len),
                pad_to(alpha_vec, target_len),
                pad_to(beta_vec, target_len),
            ]
        )

        # Create new numeric state
        from amos_kernel.compiled_numeric_kernel import CompiledState, hashlib

        tensor_bytes = new_tensor.tobytes()
        features = self._unified_state.numeric.features
        feature_bytes = features.tobytes()

        new_hash = hashlib.sha256(tensor_bytes + feature_bytes).hexdigest()[:32]

        new_numeric = CompiledState(
            canonical_hash=new_hash,
            tensor=new_tensor,
            features=features.copy(),
            timestamp=datetime.now(UTC).timestamp(),
            version=self._unified_state.numeric.version + 1,
        )

        # Update unified state
        self._unified_state = UnifiedState(
            semantic=semantic,
            numeric=new_numeric,
            last_sync=datetime.now(UTC).timestamp(),
        )

    async def _sync_numeric_to_semantic(self, numeric: CompiledState) -> None:
        """Sync numeric state changes to semantic state."""
        if self._unified_state is None:
            return

        # Convert numeric tensor to semantic state dict
        semantic_data = {
            "system_load": float(numeric.mu[0]) if len(numeric.mu) > 0 else 0.0,
            "health_score": float(numeric.mu[2]) if len(numeric.mu) > 2 else 1.0,
            "paths": {"claimed": "/", "actual": "/"},
            "prediction_error": float(numeric.nu[0]) if len(numeric.nu) > 0 else 0.0,
            "cognitive_load": float(numeric.nu[1]) if len(numeric.nu) > 1 else 0.0,
        }

        new_semantic = self._state_model.normalize(semantic_data)

        # Update unified state
        self._unified_state = UnifiedState(
            semantic=new_semantic,
            numeric=numeric,
            last_sync=datetime.now(UTC).timestamp(),
        )

    # ========================================================================
    # Queries
    # ========================================================================

    def get_state(self) -> Optional[UnifiedState]:
        """Get current unified state."""
        return self._unified_state

    def get_stats(self) -> dict[str, Any]:
        """Get kernel statistics."""
        numeric_stats = self._numeric_kernel.get_stats()

        return {
            **self._stats,
            "numeric_kernel": numeric_stats,
            "state_fresh": self._unified_state.is_fresh() if self._unified_state else False,
        }

    def configure(self, **kwargs: Any) -> None:
        """Configure kernel behavior."""
        self._config.update(kwargs)

    def health_check(self) -> dict[str, Any]:
        """Quick health check."""
        return {
            "initialized": self._initialized,
            "semantic_ready": self._unified_state is not None,
            "numeric_ready": self._unified_state is not None,
            "state_fresh": self._unified_state.is_fresh() if self._unified_state else False,
            "total_cycles": self._stats["total_cycles"],
        }


# ============================================================================
# Factory
# ============================================================================


def get_unified_kernel() -> UnifiedAmosKernel:
    """
    Get the singleton unified kernel.

    This is THE shared kernel - use this everywhere.
    Don't create new instances. Don't rebuild. Keep it alive.
    """
    return UnifiedAmosKernel()


async def quick_test() -> dict[str, Any]:
    """Quick test of unified kernel."""
    kernel = get_unified_kernel()
    kernel.initialize()

    # Emit a signal event
    result = await kernel.emit(
        event_type="signal",
        source="test",
        payload={"load": 0.5, "confidence": 0.8, "trusted": True},
    )

    # Emit a control event
    result2 = await kernel.emit(
        event_type="control",
        source="test",
        payload={"urgency": 0.3, "priority": 0.7, "authorized": True, "permission_ok": True},
    )

    stats = kernel.get_stats()

    return {
        "signal_result": result,
        "control_result": result2,
        "stats": stats,
        "health": kernel.health_check(),
    }


if __name__ == "__main__":
    import asyncio

    output = asyncio.run(quick_test())
    print(json.dumps(output, indent=2, default=str))
