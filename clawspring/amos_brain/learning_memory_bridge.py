from __future__ import annotations

from typing import Any, Dict, List, Optional

"""
AMOS Learning-Memory Bridge

Integrates Learning+Memory Kernel with existing AMOS brain systems.
Connects cognitive reasoning with persistent learning capabilities.

Integration points:
    - Brain orchestration adapter
    - Verification system
    - Decision engine
    - Task processor

Provides:
    - Outcome capture from reasoning
    - Error learning from verification
    - Memory injection into reasoning
    - Policy updates from experience
"""

import asyncio
import logging

try:
    from .learning_memory_kernel import (
        AMOSLearningMemoryKernel,
        LearningType,
        MemoryType,
        encode_and_learn,
        get_learning_memory_kernel,
        retrieve_relevant_memories,
    )
    from .learning_memory_persistence import persist_memory_state, restore_memory_state
except ImportError:
    from learning_memory_kernel import (
        AMOSLearningMemoryKernel,
        LearningType,
        MemoryType,
        get_learning_memory_kernel,
    )
    from learning_memory_persistence import persist_memory_state, restore_memory_state

logger = logging.getLogger(__name__)


class LearningMemoryBridge:
    """
    Bridge between AMOS brain and Learning-Memory Kernel.

    Captures outcomes from cognitive processes and enables
    learning from experience across sessions.

    Core loop:
        Reasoning → Verification → Outcome Capture → Learning → Memory Update
    """

    _instance: Optional[LearningMemoryBridge] = None

    def __init__(self):
        self.lmk: Optional[AMOSLearningMemoryKernel] = None
        self.initialized = False

    @classmethod
    def get_instance(cls) -> LearningMemoryBridge:
        """Singleton access."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    async def initialize(self) -> None:
        """Initialize bridge with learning-memory kernel."""
        self.lmk = get_learning_memory_kernel()
        await self.lmk.initialize()

        # Try to restore previous memory state
        try:
            restore_result = await restore_memory_state()
            logger.info(f"Memory restored: {restore_result}")
        except Exception as e:
            logger.warning(f"Could not restore memory: {e}")

        self.initialized = True
        logger.info("LearningMemoryBridge initialized")

    async def capture_reasoning_outcome(
        self,
        reasoning_input: Dict[str, Any],
        reasoning_output: Dict[str, Any],
        verification_result: Dict[str, Any] = None,
        context: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """
        Capture outcome from reasoning process.

        Records:
            - Input (observation)
            - Reasoning action
            - Output (outcome)
            - Verification status
            - Any errors
        """
        if not self.lmk:
            return {"error": "Bridge not initialized"}

        # Build observation from input
        observation = {"type": "reasoning", "input": reasoning_input, "context": context or {}}

        # Build action from reasoning process
        action = {
            "type": "cognitive_reasoning",
            "method": reasoning_output.get("method"),
            "steps": reasoning_output.get("steps", []),
        }

        # Build outcome
        success = verification_result.get("valid", True) if verification_result else True
        outcome = {
            "success": success,
            "output": reasoning_output.get("result"),
            "verification": verification_result,
        }

        # Add errors if present
        if not success and verification_result:
            {
                "magnitude": 0.8,
                "type": "verification_failure",
                "details": verification_result.get("errors", []),
            }

        # Process through learning-memory kernel
        result = await self.lmk.process_outcome(
            observation=observation,
            action=action,
            context=context or {},
            outcome=outcome,
            prediction=reasoning_output.get("predicted_outcome"),
        )

        return result

    async def learn_from_verification_failure(
        self,
        failed_check: str,
        failure_context: Dict[str, Any],
        correction: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """
        Learn specifically from verification failures.

        This is critical for LMI03: High-error experiences stored.
        """
        if not self.lmk:
            return {"error": "Bridge not initialized"}

        observation = {
            "type": "verification_failure",
            "check": failed_check,
            "context": failure_context,
        }

        action = {"type": "verify", "check": failed_check}

        outcome = {"success": False, "failure_type": "verification", "correction": correction}

        error_signal = {"magnitude": 1.0, "type": "verification_failure", "check": failed_check}

        # Encode with high importance
        record = self.lmk.memory_kernel.encode_experience(
            observation, action, failure_context, outcome, error_signal, MemoryType.ERROR
        )
        record.importance = 0.95  # Very important

        stored = self.lmk.memory_kernel.store_memory(record)

        # Update policy
        self.lmk.learning_kernel.update_policy(
            {"check": failed_check, "effectiveness": 0.0}, LearningType.VERIFICATION
        )

        return {"stored": stored, "memory_id": record.id, "policy_updated": True}

    async def inject_relevant_memories(
        self, query: str | dict[str, Any], into_context: Dict[str, Any], k: int = 3
    ) -> Dict[str, Any]:
        """
        Retrieve and inject relevant memories into reasoning context.

        This enables LMI01: Memory must influence future cognition.
        """
        if not self.lmk:
            return {"error": "Bridge not initialized", "memories": []}

        # Retrieve memories
        memories = await self.lmk.retrieve(query, k=k)

        # Inject into context
        if memories:
            into_context["retrieved_memories"] = [
                {
                    "id": m.id,
                    "type": m.type.value,
                    "observation": m.observation,
                    "outcome": m.outcome,
                    "importance": m.importance,
                }
                for m in memories
            ]
            into_context["memory_guidance"] = self._extract_guidance(memories)

        return {"memories_injected": len(memories), "memory_ids": [m.id for m in memories]}

    def _extract_guidance(self, memories: List[Any]) -> List[str]:
        """Extract actionable guidance from memories."""
        guidance = []

        for m in memories:
            if m.type == MemoryType.ERROR:
                guidance.append(f"Avoid: {m.observation.get('check', 'unknown')}")
            elif m.outcome.get("success"):
                guidance.append(f"Consider: {m.action.get('type', 'action')}")

        return guidance

    async def consolidate_and_persist(self) -> Dict[str, Any]:
        """
        Run consolidation and persist to storage.

        Called periodically or at shutdown to ensure continuity.
        """
        if not self.lmk:
            return {"error": "Bridge not initialized"}

        # Consolidate
        cons_result = await self.lmk.consolidate()

        # Persist
        persist_result = await persist_memory_state()

        return {"consolidated": cons_result, "persisted": persist_result}

    async def run_replay_learning(self, k: int = 10) -> Dict[str, Any]:
        """Run replay learning on critical memories."""
        if not self.lmk:
            return {"error": "Bridge not initialized"}

        return await self.lmk.learn_from_replay(k=k)

    def get_stats(self) -> Dict[str, Any]:
        """Get learning-memory statistics."""
        if not self.lmk:
            return {"error": "Bridge not initialized"}

        return self.lmk.get_learning_stats()


# Convenience functions for direct use


async def learn_from_reasoning(
    reasoning_input: Dict[str, Any],
    reasoning_output: Dict[str, Any],
    verification_result: Dict[str, Any] = None,
) -> Dict[str, Any]:
    """Convenience: learn from reasoning outcome."""
    bridge = LearningMemoryBridge.get_instance()
    if not bridge.initialized:
        await bridge.initialize()

    return await bridge.capture_reasoning_outcome(
        reasoning_input, reasoning_output, verification_result
    )


async def remember_for_reasoning(query: str, context: Dict[str, Any], k: int = 3) -> Dict[str, Any]:
    """Convenience: retrieve memories for reasoning context."""
    bridge = LearningMemoryBridge.get_instance()
    if not bridge.initialized:
        await bridge.initialize()

    return await bridge.inject_relevant_memories(query, context, k)


async def learn_from_mistake(
    check: str, context: Dict[str, Any], correction: Dict[str, Any] = None
) -> Dict[str, Any]:
    """Convenience: learn from verification failure."""
    bridge = LearningMemoryBridge.get_instance()
    if not bridge.initialized:
        await bridge.initialize()

    return await bridge.learn_from_verification_failure(check, context, correction)


# Integration hooks for existing AMOS components


class BrainOrchestrationLearningHook:
    """
    Hook for brain orchestration adapter to capture outcomes.
    """

    @staticmethod
    async def on_reasoning_complete(
        input_data: Dict[str, Any], output_data: Dict[str, Any], metadata: Dict[str, Any]
    ) -> None:
        """Called when reasoning completes."""
        try:
            await learn_from_reasoning(input_data, output_data)
        except Exception as e:
            logger.debug(f"Learning capture failed (non-critical): {e}")

    @staticmethod
    async def on_verification_failure(check_name: str, failure_details: Dict[str, Any]) -> None:
        """Called when verification fails."""
        try:
            await learn_from_mistake(check_name, failure_details)
        except Exception as e:
            logger.debug(f"Error learning failed (non-critical): {e}")


# Demonstration
if __name__ == "__main__":

    async def demo():
        """Demonstrate bridge integration."""
        print("Learning-Memory Bridge Demo")
        print("-" * 40)

        # Initialize
        bridge = LearningMemoryBridge.get_instance()
        await bridge.initialize()

        # Simulate reasoning outcome
        reasoning_input = {"query": "optimize_softmax", "constraints": ["fast"]}
        reasoning_output = {
            "method": "equation_selection",
            "result": "softmax_v2",
            "steps": ["analyze", "select", "apply"],
        }
        verification = {"valid": True, "checks_passed": 3}

        result = await bridge.capture_reasoning_outcome(
            reasoning_input, reasoning_output, verification
        )
        print(f"Learning captured: {result}")

        # Inject memories
        context = {}
        inject_result = await bridge.inject_relevant_memories("optimize_softmax", context, k=2)
        print(f"Memory injection: {inject_result}")
        print(f"Context now has: {list(context.keys())}")

        # Get stats
        stats = bridge.get_stats()
        print(f"Stats: {stats}")

        print("Demo complete")

    asyncio.run(demo())
