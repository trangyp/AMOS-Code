"""AMOS Brain-Powered LLM Router

Intelligent LLM request routing using BrainClient cognitive capabilities.
Analyzes request content, complexity, and requirements to select optimal provider.

Creator: Trang Phan
Version: 1.0.0
"""

import asyncio
import time
from collections.abc import AsyncGenerator
from datetime import datetime, timezone

UTC = timezone.utc
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

# Import BrainClient facade
try:
    from clawspring.agents.amos_brain.facade import BrainClient
    from clawspring.agents.amos_brain.master_orchestrator import MasterOrchestrator

    _BRAIN_AVAILABLE = True
except ImportError:
    _BRAIN_AVAILABLE = False

# Import LLM types from existing provider system
from backend.llm_providers import (
    LLMRequest,
)
from backend.llm_providers import (
    llm_router as base_llm_router,
)

router = APIRouter(prefix="/api/v1/brain/llm", tags=["Brain LLM Router"])


class BrainRoutingRequest(BaseModel):
    """Request for brain-powered LLM routing."""

    messages: List[dict[str, Any]]
    model: Optional[str] = None
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    stream: bool = False
    priority: int = Field(default=5, ge=1, le=10)
    context: Dict[str, Any] = Field(default_factory=dict)
    require_privacy: bool = False  # Force local/ollama
    require_quality: bool = False  # Force premium models
    budget_limit: Optional[float] = None  # Cost constraint


class RoutingDecision(BaseModel):
    """Brain's routing decision with reasoning."""

    provider: str
    model: str
    confidence: float
    reasoning: str
    estimated_cost: float
    estimated_latency_ms: int
    privacy_compliant: bool
    quality_score: float
    legality_score: float
    alternatives: List[dict[str, Any]]
    timestamp: str


class BrainLLMResponse(BaseModel):
    """Response with brain routing metadata."""

    content: str
    model: str
    provider: str
    routing_decision: RoutingDecision
    usage: Dict[str, int]
    latency_ms: float
    timestamp: str


class BrainLLMRouter:
    """Brain-powered intelligent LLM router."""

    def __init__(self):
        self._routing_history: List[dict[str, Any]] = []
        self._performance_cache: Dict[str, dict[str, Any]] = {}
        self._lock = asyncio.Lock()

    async def route_with_brain(
        self,
        request: BrainRoutingRequest,
    ) -> RoutingDecision:
        """Use brain to make optimal routing decision."""
        start_time = time.time()

        if not _BRAIN_AVAILABLE:
            return self._fallback_decision(request)

        try:
            client = BrainClient()

            # Build decision context
            decision_context = {
                "request_type": "llm_routing",
                "message_count": len(request.messages),
                "total_chars": sum(len(str(m.get("content", ""))) for m in request.messages),
                "temperature": request.temperature,
                "max_tokens": request.max_tokens,
                "priority": request.priority,
                "require_privacy": request.require_privacy,
                "require_quality": request.require_quality,
                "budget_limit": request.budget_limit,
                "available_providers": self._get_available_providers(),
            }

            # Get brain recommendation
            brain_result = await client.decide(
                decision_context=decision_context,
                options=self._build_provider_options(request),
                criteria=self._build_routing_criteria(request),
            )

            # Extract decision from brain result
            selection = brain_result.get("selection", {})
            provider = selection.get("provider", "ollama")
            model = selection.get("model", self._get_default_model(provider))

            # Calculate scores
            confidence = brain_result.get("confidence", 0.7)
            legality_score = brain_result.get("legality_score", 0.8)

            # Estimate cost and latency
            estimated_cost = self._estimate_cost(provider, model, request)
            estimated_latency = self._estimate_latency(provider, request)

            # Build alternatives
            alternatives = self._build_alternatives(brain_result, provider)

            decision = RoutingDecision(
                provider=provider,
                model=model,
                confidence=confidence,
                reasoning=brain_result.get("reasoning", "Routed via brain decision"),
                estimated_cost=estimated_cost,
                estimated_latency_ms=estimated_latency,
                privacy_compliant=provider in ("ollama",),
                quality_score=self._calculate_quality_score(provider, model),
                legality_score=legality_score,
                alternatives=alternatives,
                timestamp=datetime.now(UTC).isoformat(),
            )

            # Cache the decision
            async with self._lock:
                self._routing_history.append(
                    {
                        "request": request.model_dump(),
                        "decision": decision.model_dump(),
                        "latency_ms": (time.time() - start_time) * 1000,
                    }
                )

            return decision

        except Exception as e:
            return self._fallback_decision(request, error=str(e))

    async def complete(self, request: BrainRoutingRequest) -> BrainLLMResponse:
        """Complete request with brain-powered routing."""
        start_time = time.time()

        # Get routing decision from brain
        decision = await self.route_with_brain(request)

        # Build base LLM request
        llm_req = LLMRequest(
            messages=[
                type(
                    "Message",
                    (),
                    {
                        "role": m.get("role", "user"),
                        "content": m.get("content", ""),
                        "metadata": m.get("metadata"),
                    },
                )()
                for m in request.messages
            ],
            model=decision.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            stream=False,
        )

        # Route through base router with brain's recommendation
        try:
            response = await base_llm_router.route_request(
                llm_req,
                preference=decision.provider,
            )

            latency_ms = (time.time() - start_time) * 1000

            return BrainLLMResponse(
                content=response.content,
                model=response.model,
                provider=response.provider,
                routing_decision=decision,
                usage=response.usage,
                latency_ms=latency_ms,
                timestamp=datetime.now(UTC).isoformat(),
            )

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"LLM completion failed: {e!s}",
            )

    async def complete_stream(
        self,
        request: BrainRoutingRequest,
    ) -> AsyncGenerator[str, None]:
        """Stream completion with brain routing."""
        # Get routing decision
        decision = await self.route_with_brain(request)

        # Build base request
        llm_req = LLMRequest(
            messages=[
                type(
                    "Message",
                    (),
                    {
                        "role": m.get("role", "user"),
                        "content": m.get("content", ""),
                        "metadata": m.get("metadata"),
                    },
                )()
                for m in request.messages
            ],
            model=decision.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            stream=True,
        )

        # Yield routing metadata first
        yield f"data: {decision.model_dump_json()}\n\n"

        # Stream from selected provider
        try:
            async for chunk in base_llm_router.route_stream(
                llm_req,
                preference=decision.provider,
            ):
                yield f"data: {chunk}\n\n"
        except Exception as e:
            yield f"data: Error: {e!s}\n\n"

        yield "data: [DONE]\n\n"

    def _fallback_decision(
        self,
        request: BrainRoutingRequest,
        error: Optional[str] = None,
    ) -> RoutingDecision:
        """Fallback decision when brain unavailable."""
        # Prefer ollama if privacy required, otherwise use first available
        if request.require_privacy:
            provider = "ollama"
            model = "llama3.1"
        else:
            provider = "openai"
            model = "gpt-4o"

        return RoutingDecision(
            provider=provider,
            model=model,
            confidence=0.5,
            reasoning=f"Brain unavailable - using fallback ({error or 'unknown'})",
            estimated_cost=0.0,
            estimated_latency_ms=500,
            privacy_compliant=provider == "ollama",
            quality_score=0.7,
            legality_score=0.5,
            alternatives=[],
            timestamp=datetime.now(UTC).isoformat(),
        )

    def _get_available_providers(self) -> List[dict[str, Any]]:
        """Get list of available providers from base router."""
        return base_llm_router.get_available_providers()

    def _build_provider_options(
        self,
        request: BrainRoutingRequest,
    ) -> List[dict[str, Any]]:
        """Build provider options for brain decision."""
        options = []
        providers = self._get_available_providers()

        for provider in providers:
            for model in provider.get("models", []):
                option = {
                    "provider": provider["name"],
                    "model": model,
                    "privacy": provider["name"] == "ollama",
                    "quality": self._calculate_quality_score(provider["name"], model),
                    "cost": self._estimate_cost(provider["name"], model, request),
                }
                options.append(option)

        return options

    def _build_routing_criteria(self, request: BrainRoutingRequest) -> List[str]:
        """Build routing criteria based on request."""
        criteria = ["quality", "latency"]

        if request.require_privacy:
            criteria.insert(0, "privacy")

        if request.budget_limit:
            criteria.append("cost")

        if request.priority >= 8:
            criteria.insert(0, "speed")

        return criteria

    def _get_default_model(self, provider: str) -> str:
        """Get default model for provider."""
        defaults = {
            "openai": "gpt-4o",
            "anthropic": "claude-3-opus",
            "ollama": "llama3.1",
            "mock": "mock-model",
        }
        return defaults.get(provider, "unknown")

    def _estimate_cost(
        self,
        provider: str,
        model: str,
        request: BrainRoutingRequest,
    ) -> float:
        """Estimate cost for provider/model."""
        # Simplified cost estimation
        base_costs = {
            "openai": 0.002,
            "anthropic": 0.003,
            "ollama": 0.0,
            "mock": 0.0,
        }

        estimated_tokens = sum(len(str(m.get("content", ""))) // 4 for m in request.messages)
        if request.max_tokens:
            estimated_tokens += request.max_tokens

        base = base_costs.get(provider, 0.001)
        return round(base * (estimated_tokens / 1000), 4)

    def _estimate_latency(self, provider: str, request: BrainRoutingRequest) -> int:
        """Estimate latency for provider."""
        base_latencies = {
            "openai": 500,
            "anthropic": 600,
            "ollama": 200,
            "mock": 50,
        }

        complexity = sum(len(str(m.get("content", ""))) for m in request.messages)
        base = base_latencies.get(provider, 500)

        # Adjust for complexity
        if complexity > 10000:
            base += 300
        elif complexity > 5000:
            base += 150

        return base

    def _calculate_quality_score(self, provider: str, model: str) -> float:
        """Calculate quality score for provider/model."""
        scores = {
            ("openai", "gpt-4o"): 0.95,
            ("openai", "gpt-4"): 0.93,
            ("openai", "gpt-4o-mini"): 0.88,
            ("anthropic", "claude-3-opus"): 0.96,
            ("anthropic", "claude-3-sonnet"): 0.90,
            ("ollama", "llama3.1"): 0.82,
            ("ollama", "llama3"): 0.80,
            ("mock", "mock-model"): 0.30,
        }
        return scores.get((provider, model), 0.70)

    def _build_alternatives(
        self,
        brain_result: Dict[str, Any],
        selected_provider: str,
    ) -> List[dict[str, Any]]:
        """Build list of alternative providers."""
        alternatives = []
        all_options = brain_result.get("all_scores", {})

        for provider, score in all_options.items():
            if provider != selected_provider:
                alternatives.append(
                    {
                        "provider": provider,
                        "score": score,
                        "reason": f"Score: {score:.2f}",
                    }
                )

        # Sort by score
        alternatives.sort(key=lambda x: x["score"], reverse=True)
        return alternatives[:3]  # Top 3 alternatives

    def get_stats(self) -> Dict[str, Any]:
        """Get router statistics."""
        total = len(self._routing_history)
        if total == 0:
            return {"total_routes": 0, "avg_confidence": 0.0}

        avg_confidence = sum(r["decision"]["confidence"] for r in self._routing_history) / total

        return {
            "total_routes": total,
            "avg_confidence": round(avg_confidence, 2),
            "brain_available": _BRAIN_AVAILABLE,
        }


# Global brain LLM router
brain_llm_router = BrainLLMRouter()


@router.post("/route", response_model=RoutingDecision)
async def route_llm_request(request: BrainRoutingRequest) -> RoutingDecision:
    """Get brain-powered routing decision."""
    return await brain_llm_router.route_with_brain(request)


@router.post("/complete", response_model=BrainLLMResponse)
async def complete_with_brain(request: BrainRoutingRequest) -> BrainLLMResponse:
    """Complete LLM request with brain routing."""
    return await brain_llm_router.complete(request)


@router.post("/complete/stream", response_model=None)
async def complete_stream(request: BrainRoutingRequest):
    """Stream LLM completion with brain routing."""
    return brain_llm_router.complete_stream(request)


@router.get("/stats")
async def get_router_stats() -> Dict[str, Any]:
    """Get brain LLM router statistics."""
    return brain_llm_router.get_stats()


@router.get("/providers")
async def get_available_providers() -> List[dict[str, Any]]:
    """Get available LLM providers."""
    return base_llm_router.get_available_providers()
