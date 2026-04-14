#!/usr/bin/env python3
"""AMOS Brain Kernel - 01_BRAIN Subsystem

Responsible for:
- Reasoning, planning, decomposition
- Memory management
- Routing decisions
- Cognitive engine orchestration
"""

from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("amos.brain")


class ReasoningMode(Enum):
    EXPLORATORY = "exploratory"
    DIAGNOSTIC = "diagnostic"
    DESIGN = "design"
    AUDIT = "audit"
    MEASUREMENT = "measurement"


@dataclass
class CognitiveEvent:
    """A single cognitive event in the brain's processing pipeline."""

    timestamp: str
    event_type: str
    source: str
    payload: dict[str, Any]
    trace_id: str = ""
    parent_id: Optional[str] = None


@dataclass
class ReasoningThread:
    """A thread of reasoning with its own assumptions and evidence."""

    thread_id: str
    mode: ReasoningMode
    assumptions: list[str] = field(default_factory=list)
    evidence_refs: list[str] = field(default_factory=list)
    status: str = "open"  # open, closed, suspended
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())


@dataclass
class EngineResponse:
    """Response from a cognitive engine."""

    engine_name: str
    status: str
    output: dict[str, Any]
    confidence: float = 0.0
    risk_flags: list[str] = field(default_factory=list)


class BrainKernel:
    """The Brain Kernel orchestrates cognitive processing across multiple engines."""

    def __init__(self, organism_root: Path):
        self.root = organism_root
        self.brain_path = organism_root / "01_BRAIN"
        self.memory_path = self.brain_path / "memory"
        self.logs_path = self.brain_path / "logs"

        # Ensure directories exist
        self.memory_path.mkdir(parents=True, exist_ok=True)
        self.logs_path.mkdir(parents=True, exist_ok=True)

        # Working memory (short-term buffer)
        self.working_memory: list[CognitiveEvent] = []
        self.working_memory_capacity = 16

        # Canonical memory (stable laws and frameworks)
        self.canonical_memory: dict[str, Any] = {}

        # Case memory (patterns and resolved examples)
        self.case_memory: list[dict[str, Any]] = []

        # Active reasoning threads
        self.active_threads: dict[str, ReasoningThread] = {}

        # Registered engines
        self.engines: dict[str, Callable] = {}

        # Load canonical memory
        self._load_canonical_memory()

        logger.info(f"BrainKernel initialized at {self.brain_path}")

    def _load_canonical_memory(self):
        """Load canonical frameworks and laws into memory."""
        # Try to load from shared engines directory
        engines_path = self.root / "_shared" / "engines"
        if engines_path.exists():
            for engine_file in engines_path.glob("*.json"):
                try:
                    with open(engine_file) as f:
                        data = json.load(f)
                        self.canonical_memory[engine_file.stem] = data
                        logger.info(f"Loaded canonical engine: {engine_file.stem}")
                except Exception as e:
                    logger.warning(f"Failed to load {engine_file}: {e}")

    def register_engine(self, name: str, engine_fn: Callable) -> None:
        """Register a cognitive engine."""
        self.engines[name] = engine_fn
        logger.info(f"Registered engine: {name}")

    def create_thread(self, mode: ReasoningMode, assumptions: list[str] = None) -> ReasoningThread:
        """Create a new reasoning thread."""
        import uuid

        thread_id = str(uuid.uuid4())[:8]
        thread = ReasoningThread(
            thread_id=thread_id,
            mode=mode,
            assumptions=assumptions or [],
        )
        self.active_threads[thread_id] = thread

        # Manage working memory
        if len(self.working_memory) >= self.working_memory_capacity:
            self._evict_low_value()

        return thread

    def _evict_low_value(self):
        """Evict lowest value items from working memory."""
        if self.working_memory:
            # Simple FIFO eviction - could be improved with scoring
            self.working_memory.pop(0)

    def log_event(self, event: CognitiveEvent) -> None:
        """Log a cognitive event."""
        self.working_memory.append(event)

        # Persist to logs
        log_file = self.logs_path / f"{datetime.utcnow().strftime('%Y%m%d')}.log"
        with open(log_file, "a") as f:
            f.write(json.dumps(asdict(event), ensure_ascii=False) + "\n")

    def process(
        self,
        input_data: dict[str, Any],
        mode: ReasoningMode = ReasoningMode.EXPLORATORY,
        engines: list[str] = None,
    ) -> dict[str, Any]:
        """Main processing pipeline.

        Args:
            input_data: The input to process
            mode: Reasoning mode to use
            engines: List of engine names to invoke (None = all)

        Returns:
            Processing result with outputs from all engines
        """
        # Create reasoning thread
        thread = self.create_thread(mode)

        # Log input event
        event = CognitiveEvent(
            timestamp=datetime.utcnow().isoformat(),
            event_type="input_received",
            source="brain_kernel",
            payload={"input": input_data, "mode": mode.value, "thread_id": thread.thread_id},
            trace_id=thread.thread_id,
        )
        self.log_event(event)

        # Run through engines
        results = {}
        engine_list = engines or list(self.engines.keys())

        for engine_name in engine_list:
            if engine_name in self.engines:
                try:
                    engine_fn = self.engines[engine_name]
                    output = engine_fn(input_data, thread)
                    results[engine_name] = EngineResponse(
                        engine_name=engine_name,
                        status="success",
                        output=output,
                        confidence=output.get("confidence", 0.5),
                    )
                except Exception as e:
                    results[engine_name] = EngineResponse(
                        engine_name=engine_name,
                        status="error",
                        output={"error": str(e)},
                        confidence=0.0,
                        risk_flags=["engine_failure"],
                    )
                    logger.error(f"Engine {engine_name} failed: {e}")

        # Log completion
        complete_event = CognitiveEvent(
            timestamp=datetime.utcnow().isoformat(),
            event_type="processing_complete",
            source="brain_kernel",
            payload={
                "thread_id": thread.thread_id,
                "engines_used": engine_list,
                "results_summary": {k: v.status for k, v in results.items()},
            },
            trace_id=thread.thread_id,
        )
        self.log_event(complete_event)

        return {
            "thread_id": thread.thread_id,
            "mode": mode.value,
            "results": {k: asdict(v) for k, v in results.items()},
            "timestamp": datetime.utcnow().isoformat(),
        }

    def get_state(self) -> dict[str, Any]:
        """Get current brain state."""
        return {
            "working_memory_size": len(self.working_memory),
            "active_threads": len(self.active_threads),
            "canonical_memory_keys": list(self.canonical_memory.keys()),
            "registered_engines": list(self.engines.keys()),
            "timestamp": datetime.utcnow().isoformat(),
        }


# Default engines
def meta_logic_engine(input_data: dict[str, Any], thread: ReasoningThread) -> dict[str, Any]:
    """Apply meta-logic rules to input."""
    return {
        "rule_of_2_applied": True,
        "rule_of_4_applied": True,
        "structural_integrity_check": "passed",
        "confidence": 0.85,
        "next_steps": ["decompose_problem", "check_assumptions"],
    }


def structural_reasoning_engine(
    input_data: dict[str, Any], thread: ReasoningThread
) -> dict[str, Any]:
    """Apply structural reasoning."""
    return {
        "problem_decomposition": "mece_complete",
        "scenario_tree": {"root": input_data.get("goal", "unknown"), "branches": 3},
        "risk_lattice": {"identified_risks": [], "propagation_paths": []},
        "confidence": 0.75,
    }


def scenario_engine(input_data: dict[str, Any], thread: ReasoningThread) -> dict[str, Any]:
    """Generate and evaluate scenarios."""
    goal = input_data.get("goal", "unknown")
    return {
        "baseline_state": "current",
        "target_states": [goal],
        "intermediate_pivots": ["step_1", "step_2", "step_3"],
        "evaluation_metrics": ["stability", "alignment", "risk", "cost"],
        "confidence": 0.70,
    }


if __name__ == "__main__":
    # Test the brain kernel
    root = Path(__file__).parent.parent
    brain = BrainKernel(root)

    # Register default engines
    brain.register_engine("meta_logic", meta_logic_engine)
    brain.register_engine("structural", structural_reasoning_engine)
    brain.register_engine("scenario", scenario_engine)

    # Test processing
    result = brain.process(
        input_data={"goal": "map_global_requirements", "context": "AMOS_organism_bootstrap"},
        mode=ReasoningMode.DESIGN,
    )

    print(json.dumps(result, indent=2))
    print("\nBrain State:")
    print(json.dumps(brain.get_state(), indent=2))
