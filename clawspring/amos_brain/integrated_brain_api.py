"""Integrated Brain API - Combines all brain components

Unified interface to AMOS Brain with:
- ReAct Agent (reasoning + acting)
- Proactive Inference (fast path + background refinement)
- Self-Reflection (generate-critic-revise)
- Kernel Runtime (state management + law enforcement)
"""

import asyncio
import json
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

try:
    from .amos_kernel_runtime import AMOSKernelRuntime, get_kernel_runtime_async
    from .learning_memory_bridge import LearningMemoryBridge
    from .organism_bridge import get_organism_bridge
    from .proactive_inference_engine import (
        InferenceResult,
        ProactiveInferenceEngine,
    )
    from .react_agent import AMOSReActAgent, SimpleToolExecutor
    from .reflection_system import (
        Revision,
        SelfReflectionSystem,
    )

    _LEARNING_MEMORY_AVAILABLE = True
except ImportError:
    from amos_kernel_runtime import AMOSKernelRuntime, get_kernel_runtime_async
    from proactive_inference_engine import (
        ProactiveInferenceEngine,
    )
    from react_agent import AMOSReActAgent
    from reflection_system import (
        SelfReflectionSystem,
    )

    from organism_bridge import get_organism_bridge

    try:
        from learning_memory_bridge import LearningMemoryBridge

        _LEARNING_MEMORY_AVAILABLE = True
    except ImportError:
        _LEARNING_MEMORY_AVAILABLE = False


@dataclass
class BrainResponse:
    """Unified response from brain system."""

    response: str
    latency_ms: float
    mode: str
    confidence: float
    components_used: List[str]
    metadata: Dict[str, Any]


class IntegratedBrainAPI:
    """
    Unified brain API combining all components with SIKS integration.

    Usage:
        brain = IntegratedBrainAPI()
        result = await brain.process("What is 2+2?")
    """

    def __init__(self):
        # Core kernel - initialized async via get_kernel_runtime_async
        self.kernel: Optional[AMOSKernelRuntime] = None
        self._kernel_ready = False

        # Component systems
        self.react_agent: Optional[AMOSReActAgent] = None
        self.proactive_engine: Optional[ProactiveInferenceEngine] = None
        self.reflection_system: Optional[SelfReflectionSystem] = None

        # Organism bridge for SIKS and organism components
        self._organism_bridge: Optional[Any] = get_organism_bridge()

        # Learning memory bridge for experience-based improvements
        self._learning_memory: Optional[Any] = None
        if _LEARNING_MEMORY_AVAILABLE:
            try:
                self._learning_memory = LearningMemoryBridge.get_instance()
            except Exception:
                self._learning_memory = None

        # Metrics
        self._request_count = 0
        self._total_latency = 0.0

    async def _ensure_initialized(self) -> None:
        """Ensure all components are initialized."""
        if self._kernel_ready:
            return

        # Initialize kernel with SIKS support
        self.kernel = await get_kernel_runtime_async()
        self._kernel_ready = True

        # Initialize component systems
        self.react_agent = AMOSReActAgent(kernel=self.kernel)
        self.proactive_engine = ProactiveInferenceEngine(kernel=self.kernel)
        self.reflection_system = SelfReflectionSystem(kernel=self.kernel)

        # Initialize learning memory if available
        if self._learning_memory and not self._learning_memory.initialized:
            try:
                await self._learning_memory.initialize()
            except Exception:
                pass

    async def process(
        self,
        query: str,
        mode: str = "auto",
        context: Dict[str, Any] = None,
    ) -> BrainResponse:
        """
        Process query using brain system.

        Args:
            query: User query
            mode: Processing mode (fast, react, reflect, auto)
            context: Additional context

        Returns:
            BrainResponse with answer and metadata
        """
        # Ensure all components initialized
        await self._ensure_initialized()

        start_time = time.perf_counter()
        self._request_count += 1

        components_used: List[str] = []

        # Inject relevant memories into context for improved reasoning
        if self._learning_memory and self._learning_memory.initialized:
            try:
                memory_context = context.copy() if context else {}
                await self._learning_memory.inject_relevant_memories(query, memory_context, k=2)
                if memory_context.get("retrieved_memories"):
                    context = memory_context
                    components_used.append("memory_retrieval")
            except Exception:
                pass

        # Get references to initialized components
        kernel = self.kernel
        proactive_engine = self.proactive_engine
        react_agent = self.react_agent
        reflection_system = self.reflection_system

        assert kernel is not None
        assert proactive_engine is not None
        assert react_agent is not None
        assert reflection_system is not None

        # Use OrganismBridge for SIKS-enhanced cognitive analysis
        organism_enhancement = None
        if self._organism_bridge:
            try:
                organism_enhancement = self._organism_bridge.enhance_cognitive_analysis(query)
                components_used.append("organism_bridge")
            except Exception:
                pass

        # Choose processing strategy
        if mode == "fast":
            # Fast proactive inference
            result = await proactive_engine.infer(query, context)
            response = result.response
            confidence = result.confidence
            components_used.append("proactive_inference")

        elif mode == "react":
            # Full ReAct loop
            react_result = await react_agent.run(query)
            response = react_result.get("answer", "No answer")
            confidence = 0.7
            components_used.append("react_agent")

        elif mode == "reflect":
            # Generate then refine
            initial = f"Draft: {query}"
            revision = await reflection_system.refine(initial, context)
            response = revision.output
            confidence = revision.confidence
            components_used.append("reflection")

        else:  # auto mode
            # Use kernel to decide strategy (with SIKS enhancement)
            observation = {
                "query": query,
                "complexity": self._estimate_complexity(query),
                "organism_enhancement": organism_enhancement,
            }
            goal = {"type": "select_strategy", "target": query}

            cycle_result = await kernel.execute_cycle(observation, goal)

            # Route based on legality/drift
            legality = cycle_result.get("legality", 0.5)

            if legality > 0.8:
                # Simple query -> fast path
                result = await proactive_engine.infer(query, context)
                response = result.response
                confidence = result.confidence
                components_used.append("proactive_inference")
            elif legality > 0.5:
                # Moderate -> ReAct
                react_result = await react_agent.run(query)
                response = react_result.get("answer", "No answer")
                confidence = 0.7
                components_used.append("react_agent")
            else:
                # Complex -> ReAct + Reflection
                react_result = await react_agent.run(query)
                draft = react_result.get("answer", "")
                revision = await reflection_system.refine(draft, context)
                response = revision.output
                confidence = revision.confidence
                components_used.extend(["react_agent", "reflection"])

        latency = (time.perf_counter() - start_time) * 1000
        self._total_latency += latency

        # Always use kernel for final check
        final_obs = {"response": response, "query": query}
        final_goal = {"type": "validate", "target": "output"}
        validation = await kernel.execute_cycle(final_obs, final_goal)

        # Learn from this interaction
        if self._learning_memory and self._learning_memory.initialized:
            try:
                await self._learning_memory.capture_reasoning_outcome(
                    reasoning_input={"query": query, "mode": mode},
                    reasoning_output={
                        "response": response,
                        "confidence": confidence,
                        "components_used": components_used,
                    },
                    verification_result={
                        "valid": validation.get("legality", 0.5) > 0.5,
                        "legality": validation.get("legality", 0.5),
                    },
                    context=context,
                )
                components_used.append("learning_capture")
            except Exception:
                pass

        # Build metadata
        metadata: Dict[str, Any] = {
            "validation": validation,
            "avg_latency": self._total_latency / self._request_count,
        }
        if organism_enhancement:
            metadata["organism_enhancement"] = organism_enhancement

        return BrainResponse(
            response=response,
            latency_ms=latency,
            mode=mode,
            confidence=confidence * validation.get("legality", 0.5),
            components_used=components_used,
            metadata=metadata,
        )

    def _estimate_complexity(self, query: str) -> float:
        """Estimate query complexity."""
        # Simple heuristic
        words = len(query.split())
        complexity = min(1.0, words / 20.0)
        return complexity

    def get_stats(self) -> Dict[str, Any]:
        """Get brain system statistics."""
        stats = {
            "requests": self._request_count,
            "avg_latency_ms": self._total_latency / max(1, self._request_count),
            "components": ["kernel", "react", "proactive", "reflection"],
        }
        if self._learning_memory and self._learning_memory.initialized:
            try:
                lm_stats = self._learning_memory.get_stats()
                stats["learning_memory"] = lm_stats
            except Exception:
                pass
        return stats


# Global API instance
_global_brain_api: Optional[IntegratedBrainAPI] = None


def get_brain_api() -> IntegratedBrainAPI:
    """Get or create global brain API."""
    global _global_brain_api
    if _global_brain_api is None:
        _global_brain_api = IntegratedBrainAPI()
    return _global_brain_api


if __name__ == "__main__":

    async def test():
        brain = get_brain_api()

        # Test different modes
        print("=" * 60)
        print("INTEGRATED BRAIN API TEST")
        print("=" * 60)

        modes = ["fast", "react", "auto"]
        query = "Explain quantum computing"

        for mode in modes:
            print(f"\n--- Mode: {mode} ---")
            result = await brain.process(query, mode=mode)
            print(f"Response: {result.response[:60]}...")
            print(f"Latency: {result.latency_ms:.1f}ms")
            print(f"Confidence: {result.confidence:.2f}")
            print(f"Components: {result.components_used}")

        print("\n" + "=" * 60)
        print("Stats:", json.dumps(brain.get_stats(), indent=2))
        print("=" * 60)

    asyncio.run(test())
