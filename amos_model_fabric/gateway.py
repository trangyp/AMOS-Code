from __future__ import annotations

from typing import Optional

"""AMOS Model Fabric Gateway - Unified LLM Gateway

Connects SuperBrain to local/offline LLM backends with intelligent routing.
Integrates: Ollama, LM Studio, llama.cpp, vLLM, SGLang via LiteLLM proxy.
"""

import asyncio
import logging
import subprocess
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone

UTC = timezone.utc
from pathlib import Path

from amos_model_fabric.schemas import (
    FabricRequest,
    FabricResponse,
    ModelCapability,
    ModelInfo,
    ProviderHealth,
    ProviderType,
)

# LiteLLM for unified API
from .capability_registry import CapabilityRegistry, get_capability_registry
from .providers import (
    BaseProvider,
    LlamaCppProvider,
    LMStudioProvider,
    OllamaProvider,
    SGLangProvider,
    VLLMProvider,
    create_provider,
)

logger = logging.getLogger(__name__)


@dataclass
class RoutingDecision:
    """Result of routing logic."""

    provider_type: ProviderType
    model: str
    provider_instance: BaseProvider
    reason: str
    estimated_latency_ms: float
    confidence: float  # 0.0-1.0


@dataclass
class GatewayMetrics:
    """Runtime metrics for the gateway."""

    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    avg_latency_ms: float = 0.0
    cache_hits: int = 0
    provider_health: dict[ProviderType, ProviderHealth] = field(default_factory=dict)

    def record_request(self, success: bool, latency_ms: float):
        """Record a request metric."""
        self.total_requests += 1
        if success:
            self.successful_requests += 1
        else:
            self.failed_requests += 1
        # Update rolling average
        self.avg_latency_ms = (
            self.avg_latency_ms * (self.total_requests - 1) + latency_ms
        ) / self.total_requests


class LiteLLMRouter:
    """LiteLLM-based router for unified API access."""

    def __init__(self):
        self._model_list: list[dict] = []
        self._litellm_proxy_process: subprocess.Optional[Popen] = None
        self._proxy_url: str = "http://localhost:4000"

    def build_model_list(self, registry: CapabilityRegistry) -> list[dict]:
        """Build LiteLLM model list from capability registry."""
        models = []

        for model_info in registry.list_models(available_only=False):
            # Map AMOS providers to LiteLLM model names
            litellm_model = self._map_to_litellm(model_info)
            if litellm_model:
                models.append(litellm_model)

        self._model_list = models
        return models

    def _map_to_litellm(self, model_info: ModelInfo) -> dict:
        """Map AMOS ModelInfo to LiteLLM config format."""
        provider = model_info.provider

        # Build LiteLLM model ID
        if provider == ProviderType.OLLAMA:
            model_id = f"ollama/{model_info.provider_model_id}"
            api_base = model_info.endpoint_url or "http://localhost:11434"
        elif provider == ProviderType.LM_STUDIO:
            model_id = f"openai/{model_info.provider_model_id}"
            api_base = model_info.endpoint_url or "http://localhost:1234/v1"
        elif provider == ProviderType.LLAMA_CPP:
            model_id = f"openai/{model_info.provider_model_id}"
            api_base = model_info.endpoint_url or "http://localhost:8080/v1"
        elif provider == ProviderType.VLLM:
            model_id = f"openai/{model_info.provider_model_id}"
            api_base = model_info.endpoint_url or "http://localhost:8000/v1"
        elif provider == ProviderType.SGLANG:
            model_id = f"openai/{model_info.provider_model_id}"
            api_base = model_info.endpoint_url or "http://localhost:30000/v1"
        else:
            return None

        return {
            "model_name": model_info.id,
            "litellm_params": {
                "model": model_id,
                "api_base": api_base,
            },
            "model_info": {
                "id": model_info.id,
                "max_tokens": model_info.capabilities.max_output_tokens,
                "context_window": model_info.capabilities.context_window,
            },
        }

    def start_proxy(self, config_path: Optional[Path] = None) -> bool:
        """Start LiteLLM proxy server if available."""
        try:
            # Check if litellm proxy is already running
            import requests

            try:
                resp = requests.get(f"{self._proxy_url}/health", timeout=2)
                if resp.status_code == 200:
                    logger.info("LiteLLM proxy already running")
                    return True
            except Exception:
                pass

            # Start proxy in background
            if config_path and config_path.exists():
                cmd = ["litellm", "--config", str(config_path), "--port", "4000"]
            else:
                # Start with environment-based config
                cmd = ["litellm", "--port", "4000", "--detailed_debug"]

            self._litellm_proxy_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            # Wait for startup
            time.sleep(3)

            # Verify it's running
            try:
                import requests

                resp = requests.get(f"{self._proxy_url}/health", timeout=5)
                return resp.status_code == 200
            except Exception:
                return False

        except Exception as e:
            logger.warning(f"Failed to start LiteLLM proxy: {e}")
            return False

    def stop_proxy(self):
        """Stop the LiteLLM proxy server."""
        if self._litellm_proxy_process:
            self._litellm_proxy_process.terminate()
            self._litellm_proxy_process = None


class RoutingStrategy:
    """Strategy for selecting the best provider."""

    def __init__(self, registry: CapabilityRegistry):
        self.registry = registry

    def select_provider(
        self,
        required_capabilities: list[ModelCapability],
        preferred_provider: Optional[ProviderType] = None,
        task_type: str = "general",
    ) -> RoutingDecision:
        """Select the best provider for a task."""

        # Get candidates with required capabilities
        candidates = self.registry.find_models_with_capabilities(
            required_capabilities,
            preferred_provider=preferred_provider,
        )

        if not candidates:
            # Fallback to any available provider
            return RoutingDecision(
                provider_type=preferred_provider or ProviderType.OLLAMA,
                model="qwen2.5-coder:14b",
                provider_instance=None,
                reason="No matching models found - using default",
                estimated_latency_ms=1000.0,
                confidence=0.3,
            )

        # Score candidates
        best = candidates[0]  # Already sorted by priority

        # Estimate latency based on model size/quantization
        latency = self._estimate_latency(best)

        # Create provider instance
        provider_instance = create_provider(best.provider, best.endpoint_url)

        return RoutingDecision(
            provider_type=best.provider,
            model=best.provider_model_id,
            provider_instance=provider_instance,
            reason=f"Best match: {best.id} with capabilities {required_capabilities}",
            estimated_latency_ms=latency,
            confidence=0.9 if best.is_available else 0.5,
        )

    def _estimate_latency(self, model_info: ModelInfo) -> float:
        """Estimate latency for a model."""
        base_latency = 500.0  # 500ms base

        # Adjust for quantization
        if model_info.capabilities.quantization:
            q = model_info.capabilities.quantization
            if "Q4" in q:
                base_latency *= 0.8
            elif "Q8" in q:
                base_latency *= 1.0
            elif "FP16" in q or "fp16" in q:
                base_latency *= 1.5

        # Adjust for context window (larger = slower)
        ctx = model_info.capabilities.context_window
        if ctx > 100000:
            base_latency *= 1.2

        return base_latency


class ModelFabricGateway:
    """
    Main gateway for the AMOS Model Fabric.

    Connects SuperBrain to all local/offline LLM backends.
    Provides unified interface with intelligent routing.
    """

    def __init__(self):
        self.registry = get_capability_registry()
        self.router = LiteLLMRouter()
        self.routing_strategy = RoutingStrategy(self.registry)
        self.metrics = GatewayMetrics()
        self._providers: dict[ProviderType, BaseProvider] = {}
        self._initialized = False
        self._last_health_check: Optional[datetime] = None

    async def initialize(self) -> bool:
        """Initialize the gateway and discover available providers."""
        logger.info("Initializing Model Fabric Gateway...")

        # Discover local providers
        await self._discover_providers()

        # Build LiteLLM model list
        self.router.build_model_list(self.registry)

        self._initialized = True
        logger.info(f"Gateway initialized with {len(self._providers)} providers")
        return True

    async def _discover_providers(self):
        """Auto-discover available local LLM providers."""
        discovery_order = [
            (ProviderType.OLLAMA, "http://localhost:11434", OllamaProvider),
            (ProviderType.LM_STUDIO, "http://localhost:1234", LMStudioProvider),
            (ProviderType.VLLM, "http://localhost:8000", VLLMProvider),
            (ProviderType.SGLANG, "http://localhost:30000", SGLangProvider),
            (ProviderType.LLAMA_CPP, "http://localhost:8080", LlamaCppProvider),
        ]

        for provider_type, default_url, provider_class in discovery_order:
            try:
                provider = provider_class(base_url=default_url)
                is_healthy = await provider.health_check()

                if is_healthy:
                    self._providers[provider_type] = provider
                    models = await provider.list_models()

                    # Register discovered models
                    for model_name in models:
                        caps = self.registry.infer_capabilities(model_name)
                        model_info = ModelInfo(
                            id=f"{provider_type.value}:{model_name}",
                            name=model_name,
                            provider=provider_type,
                            provider_model_id=model_name,
                            capabilities=caps,
                            endpoint_url=default_url,
                            is_available=True,
                        )
                        self.registry.register_model(model_info)

                    logger.info(f"✅ Discovered {provider_type.value} with {len(models)} models")
                else:
                    logger.debug(f"Provider {provider_type.value} not available")

            except Exception as e:
                logger.debug(f"Failed to discover {provider_type.value}: {e}")

    async def complete(self, request: FabricRequest) -> FabricResponse:
        """Execute a completion request."""
        start = datetime.now(UTC)

        # Determine required capabilities
        required_caps = self._infer_required_capabilities(request)

        # Route to best provider
        decision = self.routing_strategy.select_provider(
            required_capabilities=required_caps,
            preferred_provider=ProviderType(request.preferred_provider)
            if request.preferred_provider
            else None,
            task_type=request.task_type or "general",
        )

        # Execute via selected provider
        provider = decision.provider_instance
        if provider is None:
            # Create provider on-the-fly
            provider = create_provider(decision.provider_type)

        try:
            response = await provider.complete(request)
            latency_ms = (datetime.now(UTC) - start).total_seconds() * 1000

            self.metrics.record_request(success=True, latency_ms=latency_ms)
            self.registry.update_model_health(
                f"{decision.provider_type.value}:{decision.model}", True
            )

            return response

        except Exception as e:
            latency_ms = (datetime.now(UTC) - start).total_seconds() * 1000
            self.metrics.record_request(success=False, latency_ms=latency_ms)
            self.registry.update_model_health(
                f"{decision.provider_type.value}:{decision.model}", False, str(e)
            )

            # Return error response
            return FabricResponse(
                content="",
                model=decision.model,
                provider=decision.provider_type,
                latency_ms=latency_ms,
                finish_reason="error",
                error=str(e),
            )

    async def complete_stream(self, request: FabricRequest):
        """Stream a completion request."""
        # Same routing logic as complete()
        required_caps = self._infer_required_capabilities(request)

        decision = self.routing_strategy.select_provider(
            required_capabilities=required_caps,
            preferred_provider=ProviderType(request.preferred_provider)
            if request.preferred_provider
            else None,
        )

        provider = decision.provider_instance or create_provider(decision.provider_type)

        async for chunk in provider.complete_stream(request):
            yield chunk

    def _infer_required_capabilities(self, request: FabricRequest) -> list[ModelCapability]:
        """Infer required capabilities from request."""
        caps = [ModelCapability.CHAT]

        if request.tools:
            caps.append(ModelCapability.TOOL_USE)
            caps.append(ModelCapability.FUNCTION_CALLING)

        if request.task_type == "code":
            caps.append(ModelCapability.CODE)
        elif request.task_type == "edit":
            caps.append(ModelCapability.CODE)
            caps.append(ModelCapability.EDIT)

        return caps

    async def health_check(self) -> dict[ProviderType, bool]:
        """Check health of all providers."""
        results = {}

        for provider_type, provider in self._providers.items():
            try:
                is_healthy = await provider.health_check()
                results[provider_type] = is_healthy
            except Exception:
                results[provider_type] = False

        self._last_health_check = datetime.now(UTC)
        return results

    def get_metrics(self) -> GatewayMetrics:
        """Get current gateway metrics."""
        return self.metrics

    def list_available_models(self) -> list[ModelInfo]:
        """List all available models."""
        return self.registry.list_models()

    async def close(self):
        """Close all provider connections."""
        for provider in self._providers.values():
            await provider.close()
        self.router.stop_proxy()


# Singleton instance
_gateway: Optional[ModelFabricGateway] = None


def get_gateway() -> ModelFabricGateway:
    """Get the global Model Fabric Gateway instance."""
    global _gateway
    if _gateway is None:
        _gateway = ModelFabricGateway()
    return _gateway


async def test_gateway():
    """Test the gateway functionality."""
    print("=" * 70)
    print("MODEL FABRIC GATEWAY - TEST")
    print("=" * 70)

    gateway = get_gateway()
    await gateway.initialize()

    # Health check
    print("\n[1] Health Check:")
    health = await gateway.health_check()
    for provider, is_healthy in health.items():
        status = "✅" if is_healthy else "❌"
        print(f"    {status} {provider.value}")

    # List models
    print("\n[2] Available Models:")
    models = gateway.list_available_models()
    for model in models[:5]:  # Show first 5
        caps = ", ".join([c.name for c in model.capabilities.capabilities])[:50]
        print(f"    - {model.name} ({model.provider.value}) [{caps}...]")

    # Test completion (if Ollama available)
    if any(p == ProviderType.OLLAMA for p in gateway._providers):
        print("\n[3] Test Completion:")
        request = FabricRequest(
            messages=[{"role": "user", "content": "Say 'Gateway working' and nothing else"}],
            model="qwen2.5-coder:14b",
            temperature=0.1,
        )

        try:
            response = await asyncio.wait_for(gateway.complete(request), timeout=30)
            print(f"    Response: {response.content[:100]}...")
            print(f"    Latency: {response.latency_ms:.0f}ms")
        except Exception as e:
            print(f"    Error: {e}")

    print("\n[4] Metrics:")
    metrics = gateway.get_metrics()
    print(f"    Total requests: {metrics.total_requests}")
    print(f"    Avg latency: {metrics.avg_latency_ms:.1f}ms")

    print("\n" + "=" * 70)
    print("Test complete!")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(test_gateway())
