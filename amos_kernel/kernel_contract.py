"""
Kernel Contract - Initialization and Runtime Contract

Formal contract for kernel-first initialization.

Chain:
    ULK → DeterministicCore → UniversalState → SelfObserver → RepairExecutor

All runtime/build/repair paths must validate through this stack.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
UTC = timezone.utc
from typing import Any, Optional

from amos_kernel.contracts import CORE_INVARIANTS, KernelResult


@dataclass
class KernelInitialization:
    """Result of kernel initialization."""

    ulk_ready: bool
    deterministic_core_ready: bool
    state_model_ready: bool
    self_observer_ready: bool
    repair_executor_ready: bool
    invariants_valid: bool
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))

    @property
    def all_ready(self) -> bool:
        """Check if all kernel layers are ready."""
        return (
            self.ulk_ready
            and self.deterministic_core_ready
            and self.state_model_ready
            and self.self_observer_ready
            and self.repair_executor_ready
            and self.invariants_valid
        )


@dataclass
class KernelRuntimeContext:
    """Runtime context for kernel operations."""

    session_id: str
    trace_id: str
    entry_point: str  # "cli", "api", "ci", "repair", "observation"
    constraints: dict[str, Any]
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))


class KernelContract:
    """
    Kernel initialization contract.

    Enforces proper initialization order and validation.
    """

    _instance: Optional[KernelContract] = None
    _initialized: bool = False

    def __new__(cls) -> KernelContract:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def initialize(self) -> KernelResult[KernelInitialization]:
        """
        Initialize the kernel stack in correct order.

        Order:
        1. Universal Law Kernel (K0)
        2. Deterministic Core (K1)
        3. Universal State Model (K2)
        4. Interaction Engine (K3)
        5. Self Observer (K4)
        6. Repair Executor (K5)
        """
        result = KernelInitialization(
            ulk_ready=False,
            deterministic_core_ready=False,
            state_model_ready=False,
            self_observer_ready=False,
            repair_executor_ready=False,
            invariants_valid=False,
        )

        try:
            # Step 1: Initialize ULK
            from amos_kernel.L0_universal_law_kernel import get_universal_law_kernel

            ulk = get_universal_law_kernel()
            result.ulk_ready = ulk._initialized

            # Step 2: Initialize Deterministic Core
            from amos_kernel.L1_deterministic_core import get_deterministic_core

            core = get_deterministic_core()
            result.deterministic_core_ready = core._initialized

            # Step 3: Initialize State Model
            from amos_kernel.L2_universal_state_model import get_universal_state_model

            state_model = get_universal_state_model()
            result.state_model_ready = state_model._initialized

            # Step 4: Initialize Interaction Engine
            from amos_kernel.L3_interaction_engine import get_interaction_engine

            interaction = get_interaction_engine()
            result.self_observer_ready = interaction._initialized  # Reuse flag

            # Step 5: Initialize Self Observer
            from amos_kernel.L4_self_observer import get_self_observer

            observer = get_self_observer()
            result.self_observer_ready = observer._initialized

            # Step 6: Initialize Repair Executor
            from amos_kernel.L5_repair_executor import get_repair_executor

            repair = get_repair_executor()
            result.repair_executor_ready = repair._initialized

            # Validate invariants
            result.invariants_valid = self._validate_invariants()

            self._initialized = True

            if result.all_ready:
                return KernelResult.ok(result, "KernelContract")
            else:
                errors = []
                if not result.ulk_ready:
                    errors.append("ULK not ready")
                if not result.deterministic_core_ready:
                    errors.append("DeterministicCore not ready")
                if not result.state_model_ready:
                    errors.append("StateModel not ready")
                if not result.self_observer_ready:
                    errors.append("SelfObserver not ready")
                if not result.repair_executor_ready:
                    errors.append("RepairExecutor not ready")
                if not result.invariants_valid:
                    errors.append("Invariants not valid")

                return KernelResult.fail(errors, "KernelContract")

        except Exception as e:
            return KernelResult.fail([f"Initialization error: {e}"], "KernelContract")

    def validate_runtime_path(
        self,
        path_type: str,  # "build", "runtime", "repair", "cli", "ci"
        context: dict[str, Any],
    ) -> KernelResult[bool]:
        """
        Validate a runtime path through the kernel.

        All paths must pass through ULK.
        """
        if not self._initialized:
            return KernelResult.fail(["Kernel not initialized"], "KernelContract")

        from amos_kernel.L0_universal_law_kernel import get_universal_law_kernel
        from amos_kernel.L2_universal_state_model import get_universal_state_model

        # Normalize context into state tensor
        state_model = get_universal_state_model()
        state = state_model.normalize(context)

        # Validate through ULK
        ulk = get_universal_law_kernel()
        validation = ulk.validate_invariants(state, {"path_type": path_type})

        if validation.success:
            return KernelResult.ok(True, "KernelContract")

        return KernelResult.fail(validation.errors, "KernelContract")

    def create_runtime_context(
        self, entry_point: str, constraints: Optional[dict[str, Any]] = None
    ) -> KernelRuntimeContext:
        """Create a validated runtime context."""
        import uuid

        return KernelRuntimeContext(
            session_id=str(uuid.uuid4()),
            trace_id=str(uuid.uuid4()),
            entry_point=entry_point,
            constraints=constraints or {},
        )

    def _validate_invariants(self) -> bool:
        """Validate core invariants are loadable."""
        return len(CORE_INVARIANTS) > 0

    def is_initialized(self) -> bool:
        """Check if kernel is initialized."""
        return self._initialized


def get_kernel_contract() -> KernelContract:
    """Get the singleton kernel contract."""
    return KernelContract()


def initialize_kernel() -> KernelResult[KernelInitialization]:
    """Convenience function to initialize kernel."""
    contract = get_kernel_contract()
    return contract.initialize()
