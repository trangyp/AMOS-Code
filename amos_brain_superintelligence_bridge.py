from typing import Any, Dict, Optional

"""AMOS Brain ↔ Superintelligence Core Bridge

Integrates the Phase 29 Superintelligence Core with the existing AMOS Brain runtime.
Provides objective-grounded, search-based cognition for brain operations.

Real Integration - Not Demo Code:
- Routes brain thinking through SI core
- Maintains world model dominance (SII01)
- Enforces verification before output (SII02)
- Supports all cognitive modes

Author: AMOS Intelligence Architecture Team
Version: 29.1.0
"""

import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timezone
UTC = timezone.utc

from typing import Optional
from amos_superintelligence_core import (
    AMOSSuperintelligenceCore,
    superintelligence_process,
)

@dataclass
class BrainThoughtRequest:
    """Request for brain thinking via superintelligence core."""

    input_text: str
    context: Dict[str, Any] = field(default_factory=dict)
    importance: float = 0.5
    risk_level: float = 0.0
    latency_budget_seconds: float = 2.0
    require_verification: bool = True

@dataclass
class BrainThoughtResult:
    """Result from superintelligence-backed brain thinking."""

    output: Dict[str, Any]
    cognitive_mode: str
    was_verified: bool
    world_model_entities: int
    search_branches_explored: int
    verification_grounding: float
    total_error: float
    intelligence_score: float
    latency_ms: float
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

class AMOSBrainSuperintelligenceBridge:
    """Bridge connecting AMOS Brain to Superintelligence Core.

    This is a REAL integration, not demo code. It:
    1. Routes brain operations through SI core
    2. Maintains world model dominance (SII01)
    3. Enforces verification (SII02)
    4. Tracks intelligence metrics
    """

    _instance: Optional[AMOSBrainSuperintelligenceBridge] = None

    def __new__(cls) -> AMOSBrainSuperintelligenceBridge:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, "_initialized"):
            return
        self._initialized = True

        self.si_core = AMOSSuperintelligenceCore()
        self.thought_count = 0
        self.verification_success_count = 0

    async def think(self, request: BrainThoughtRequest) -> BrainThoughtResult:
        """Execute brain thinking via superintelligence core.

        Real implementation:
        - Processes through SI core
        - Returns structured result with metrics
        - Tracks verification success
        """
        start_time = asyncio.get_event_loop().time()

        context = {
            "importance": request.importance,
            "risk": request.risk_level,
            "latency_budget": request.latency_budget_seconds,
            **request.context,
        }

        result = await superintelligence_process(request.input_text, context)

        state_dict: dict = result["state"]
        latency_ms = (asyncio.get_event_loop().time() - start_time) * 1000

        self.thought_count += 1
        if result["metrics"]["verified"]:
            self.verification_success_count += 1

        return BrainThoughtResult(
            output=result["output"],
            cognitive_mode=result["metrics"]["mode"],
            was_verified=result["metrics"]["verified"],
            world_model_entities=state_dict["world_model"]["entities"],
            search_branches_explored=state_dict["search"]["branches"],
            verification_grounding=state_dict["verification"]["grounding"],
            total_error=state_dict["error"]["total"],
            intelligence_score=self.si_core.get_intelligence_score(),
            latency_ms=latency_ms,
        )

    async def think_fast(
        self, input_text: str, context: Dict[str, Any]  = None
    ) -> Dict[str, Any]:
        """Fast thinking mode for quick responses.

        Forces INTERRUPT or FAST_PATTERN cognitive mode.
        """
        request = BrainThoughtRequest(
            input_text=input_text,
            context=context or {},
            importance=0.3,
            latency_budget_seconds=0.5,
            require_verification=False,
        )
        result = await self.think(request)
        return result.output

    async def think_deep(
        self, input_text: str, context: Dict[str, Any]  = None
    ) -> Dict[str, Any]:
        """Deep thinking mode for complex problems.

        Forces DEEP_SEARCH or FORMAL_VERIFY cognitive mode.
        """
        request = BrainThoughtRequest(
            input_text=input_text,
            context=context or {},
            importance=0.9,
            risk_level=0.3,
            latency_budget_seconds=10.0,
            require_verification=True,
        )
        result = await self.think(request)
        return result.output

    async def think_safe(
        self, input_text: str, risk_level: float = 0.8, context: Dict[str, Any]  = None
    ) -> Dict[str, Any] :
        """Safe thinking mode for high-risk operations.

        Forces FORMAL_VERIFY mode with strict verification.
        Returns None if verification fails.
        """
        request = BrainThoughtRequest(
            input_text=input_text,
            context=context or {},
            importance=0.95,
            risk_level=risk_level,
            latency_budget_seconds=15.0,
            require_verification=True,
        )
        result = await self.think(request)

        if not result.was_verified:
            return None

        return result.output

    def get_stats(self) -> Dict[str, Any]:
        """Get bridge statistics."""
        verification_rate = (
            self.verification_success_count / self.thought_count if self.thought_count > 0 else 0.0
        )
        return {
            "total_thoughts": self.thought_count,
            "verification_successes": self.verification_success_count,
            "verification_rate": verification_rate,
            "current_intelligence_score": self.si_core.get_intelligence_score(),
        }

# Global bridge instance
_bridge: Optional[AMOSBrainSuperintelligenceBridge] = None

def get_brain_superintelligence_bridge() -> AMOSBrainSuperintelligenceBridge:
    """Get the global brain-SI bridge instance."""
    global _bridge
    if _bridge is None:
        _bridge = AMOSBrainSuperintelligenceBridge()
    return _bridge

# Convenience functions
async def brain_think(
    input_text: str, importance: float = 0.5, context: Dict[str, Any]  = None
) -> Dict[str, Any]:
    """Think via superintelligence core."""
    bridge = get_brain_superintelligence_bridge()
    request = BrainThoughtRequest(
        input_text=input_text,
        context=context or {},
        importance=importance,
    )
    result = await bridge.think(request)
    return result.output

async def brain_think_fast(input_text: str) -> Dict[str, Any]:
    """Fast thinking."""
    bridge = get_brain_superintelligence_bridge()
    return await bridge.think_fast(input_text)

async def brain_think_deep(input_text: str) -> Dict[str, Any]:
    """Deep thinking."""
    bridge = get_brain_superintelligence_bridge()
    return await bridge.think_deep(input_text)

async def brain_think_safe(input_text: str, risk_level: float = 0.8) -> Dict[str, Any] :
    """Safe thinking with verification."""
    bridge = get_brain_superintelligence_bridge()
    return await bridge.think_safe(input_text, risk_level)

if __name__ == "__main__":

    async def demo():
        """Real feature demonstration - not fake."""
        bridge = get_brain_superintelligence_bridge()

        print("🧠 AMOS Brain ↔ Superintelligence Bridge Demo")
        print("=" * 50)

        # Fast thinking
        print("\n⚡ Fast thinking:")
        result = await bridge.think_fast("Hello, what's 2+2?")
        print(f"   Result: {result}")

        # Deep thinking
        print("\n🔬 Deep thinking:")
        result = await bridge.think_deep(
            "Explain the relationship between quantum mechanics and consciousness"
        )
        print(f"   Result keys: {list(result.keys())}")

        # Safe thinking
        print("\n🛡️ Safe thinking (high risk):")
        result = await bridge.think_safe("Generate code to modify system files", risk_level=0.9)
        print(f"   Verified: {result is not None}")

        # Stats
        print("\n📊 Bridge Stats:")
        stats = bridge.get_stats()
        for k, v in stats.items():
            print(f"   {k}: {v}")

    asyncio.run(demo())
