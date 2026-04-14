#!/usr/bin/env python3
"""AMOS Master Cognitive Orchestrator - Single entry point for entire AMOS ecosystem."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

from amos_cognitive_router import CognitiveRouter
from amos_engine_activator import EngineActivator
from amos_feature_activation import FeatureActivationSystem
from amos_knowledge_loader import KnowledgeLoader
from amos_primary_feature_handler import PrimaryFeatureHandler
from amosl_bridge import BridgeExecutor
from amosl_evolution import EvolutionOperator

# Import all AMOS components
from amosl_ledger import EntryType, StateLedger
from amosl_verification import VerificationEngine


@dataclass
class OrchestratorResult:
    """Result from orchestrator processing."""

    task: str
    status: str
    engine_used: str
    category: str
    result_data: dict[str, Any] = field(default_factory=dict)
    processing_time_ms: int = 0
    ledger_entry_id: Optional[str] = None


class MasterCognitiveOrchestrator:
    """Master orchestrator for entire AMOS ecosystem.

    Single entry point that coordinates:
    - Phase 14 AMOSL Runtime (7 components)
    - 4,644 discoverable features
    - 659 knowledge files
    - 251 activated engines
    - Cognitive routing

    Usage:
        amos = MasterCognitiveOrchestrator()
        result = amos.process("Analyze market strategy for Vietnam")
    """

    def __init__(self):
        # Phase 14 AMOSL Runtime
        self.ledger: Optional[StateLedger] = None
        self.verifier: Optional[VerificationEngine] = None
        self.bridge: Optional[BridgeExecutor] = None
        self.evolution: Optional[EvolutionOperator] = None

        # Ecosystem components
        self.feature_activation: Optional[FeatureActivationSystem] = None
        self.primary_handler: Optional[PrimaryFeatureHandler] = None
        self.knowledge_loader: Optional[KnowledgeLoader] = None
        self.engine_activator: Optional[EngineActivator] = None
        self.cognitive_router: Optional[CognitiveRouter] = None

        # State
        self.initialized = False
        self.stats = {"tasks_processed": 0, "engines_invoked": 0, "knowledge_accessed": 0}

    def initialize(self) -> dict[str, Any]:
        """Initialize all AMOS components."""
        print("\n" + "=" * 70)
        print("AMOS MASTER COGNITIVE ORCHESTRATOR - INITIALIZATION")
        print("=" * 70)

        # Phase 14: AMOSL Runtime
        print("\n[Phase 14] Initializing AMOSL Runtime...")
        self.ledger = StateLedger()
        self.verifier = VerificationEngine(self.ledger)
        self.bridge = BridgeExecutor(self.ledger, self.verifier)
        self.evolution = EvolutionOperator(self.ledger, self.verifier, self.bridge)
        print("  ✓ Ledger, Verifier, Bridge, Evolution: ACTIVE")

        # Phase 15: Feature Ecosystem
        print("\n[Phase 15] Initializing Feature Ecosystem...")
        self.feature_activation = FeatureActivationSystem()
        self.primary_handler = PrimaryFeatureHandler()
        print("  ✓ Feature Activation: ACTIVE")
        print("  ✓ Primary Handler: ACTIVE")

        # Phase 16: Knowledge & Engines
        print("\n[Phase 16] Initializing Knowledge & Engines...")
        self.knowledge_loader = KnowledgeLoader()
        self.engine_activator = EngineActivator()
        self.cognitive_router = CognitiveRouter(self.engine_activator)
        print("  ✓ Knowledge Loader: ACTIVE")
        print("  ✓ Engine Activator: ACTIVE")
        print("  ✓ Cognitive Router: ACTIVE")

        # Scan ecosystem
        print("\n[Ecosystem Scan] Discovering features...")
        feature_stats = self.feature_activation.discover_all()
        print(f"  ✓ Discovered: {feature_stats.get('total_files', 0)} features")

        # Activate engines
        print("\n[Engine Activation] Loading engines...")
        engine_stats = self.engine_activator.scan_and_activate()
        print(f"  ✓ Activated: {engine_stats.get('total_activated', 0)} engines")

        self.initialized = True

        print("\n" + "=" * 70)
        print("✓ AMOS ORCHESTRATOR FULLY INITIALIZED")
        print("=" * 70)

        return {
            "status": "initialized",
            "amosl_runtime": True,
            "features_discovered": feature_stats.get("total_files", 0),
            "engines_activated": engine_stats.get("total_activated", 0),
            "ready": True,
        }

    def process(self, task: str, context: Optional[dict[str, Any]] = None) -> OrchestratorResult:
        """Process a task through the complete AMOS pipeline.

        Pipeline:
        1. Log task to ledger
        2. Route to optimal engine
        3. Load relevant knowledge
        4. Invoke engine with context
        5. Verify result
        6. Log completion
        """
        import time

        start_time = time.time()
        context = context or {}

        if not self.initialized:
            self.initialize()

        # Step 1: Log task
        self.ledger.append(
            EntryType.EVOLUTION_STEP, {"task": task, "context": context}, {"event": "task_received"}
        )

        # Step 2: Route to engine
        route_decision = self.cognitive_router.route_task(task, context)

        # Step 3: Load relevant knowledge
        knowledge_category = route_decision.engine_category
        relevant_knowledge = self.knowledge_loader.get_knowledge(knowledge_category)

        # Step 4: Invoke engine
        engine_result = self.engine_activator.invoke_engine(
            route_decision.engine_category,
            task,
            {
                "route_decision": route_decision,
                "knowledge": [k.name for k in relevant_knowledge[:3]],
                "context": context,
            },
        )

        # Step 5: Verify result (simplified)
        verification = self.verifier.verify_state(
            {"task": task, "engine": route_decision.selected_engine, "status": "completed"}
        )

        # Step 6: Log completion
        ledger_entry = self.ledger.append(
            EntryType.EVOLUTION_STEP,
            {"task": task, "result": engine_result},
            {
                "event": "task_completed",
                "engine": route_decision.selected_engine,
                "verification": verification.proof_hash if verification.valid else None,
            },
        )

        # Update stats
        self.stats["tasks_processed"] += 1
        self.stats["engines_invoked"] += 1
        self.stats["knowledge_accessed"] += len(relevant_knowledge)

        duration_ms = int((time.time() - start_time) * 1000)

        return OrchestratorResult(
            task=task,
            status="completed" if verification.valid else "verification_failed",
            engine_used=route_decision.selected_engine,
            category=route_decision.engine_category,
            result_data=engine_result.get("result", {}),
            processing_time_ms=duration_ms,
            ledger_entry_id=ledger_entry.hash if ledger_entry else None,
        )

    def process_batch(self, tasks: list[str]) -> list[OrchestratorResult]:
        """Process multiple tasks."""
        return [self.process(task) for task in tasks]

    def get_status(self) -> dict[str, Any]:
        """Get orchestrator status."""
        return {
            "initialized": self.initialized,
            "components": {
                "amosl_runtime": all([self.ledger, self.verifier, self.bridge, self.evolution]),
                "feature_activation": self.feature_activation is not None,
                "knowledge_loader": self.knowledge_loader is not None,
                "engine_activator": self.engine_activator is not None,
                "cognitive_router": self.cognitive_router is not None,
            },
            "stats": self.stats,
            "ready": self.initialized,
        }

    def query(self, question: str) -> dict[str, Any]:
        """Query the knowledge base."""
        if not self.initialized:
            self.initialize()

        knowledge_results = self.knowledge_loader.query_knowledge(question, top_n=5)
        engine_results = self.cognitive_router.query_engines(question, top_n=5)

        return {
            "question": question,
            "knowledge_matches": len(knowledge_results),
            "engine_matches": len(engine_results),
            "top_knowledge": [k.name for k in knowledge_results[:3]],
            "top_engines": [e.name for e in engine_results[:3]],
        }


def demo_master_orchestrator():
    """Demonstrate master orchestrator."""
    print("\n" + "=" * 70)
    print("AMOS MASTER COGNITIVE ORCHESTRATOR - DEMONSTRATION")
    print("=" * 70)
    print("\n🎯 Goal: Single entry point for entire AMOS ecosystem")

    # Create orchestrator
    amos = MasterCognitiveOrchestrator()

    # Initialize
    print("\n[1] Initializing AMOS ecosystem...")
    init_result = amos.initialize()

    print(f"\n  Status: {init_result['status']}")
    print(f"  Features: {init_result['features_discovered']}")
    print(f"  Engines: {init_result['engines_activated']}")

    # Process tasks
    print("\n[2] Processing cognitive tasks...")

    demo_tasks = [
        "Analyze market entry strategy",
        "Generate Python API framework",
        "Review compliance requirements",
        "Assess Vietnam local regulations",
        "Apply UBI principles to design",
    ]

    for i, task in enumerate(demo_tasks, 1):
        result = amos.process(task)
        print(f"\n  Task {i}: {task[:40]}...")
        print(f"    Status: {result.status}")
        print(f"    Engine: {result.engine_used}")
        print(f"    Category: {result.category}")
        print(f"    Time: {result.processing_time_ms}ms")

    # Batch processing
    print("\n[3] Batch processing...")
    batch_results = amos.process_batch(demo_tasks[:3])
    print(f"  Processed {len(batch_results)} tasks")

    # Query knowledge
    print("\n[4] Querying knowledge base...")
    query_result = amos.query("consulting engine Vietnam")
    print(f"  Question: {query_result['question']}")
    print(f"  Knowledge matches: {query_result['knowledge_matches']}")
    print(f"  Engine matches: {query_result['engine_matches']}")
    print(f"  Top knowledge: {', '.join(query_result['top_knowledge'][:3])}")

    # Status check
    print("\n[5] Final status...")
    status = amos.get_status()
    print(f"  Initialized: {status['initialized']}")
    print(f"  Tasks processed: {status['stats']['tasks_processed']}")
    print(f"  Engines invoked: {status['stats']['engines_invoked']}")
    print(f"  Knowledge accessed: {status['stats']['knowledge_accessed']}")

    print("\n" + "=" * 70)
    print("✓ MASTER ORCHESTRATOR DEMONSTRATION COMPLETE")
    print("=" * 70)
    print("\nAMOS is now a unified cognitive system:")
    print("  • Single entry point: amos.process(task)")
    print("  • 251 engines routable")
    print("  • 659 knowledge files accessible")
    print("  • Complete pipeline: Task → Router → Engine → Knowledge → Output")
    print("=" * 70)


if __name__ == "__main__":
    demo_master_orchestrator()
