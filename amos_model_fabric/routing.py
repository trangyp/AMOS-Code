"""AMOS Model Fabric - LiteLLM-style Router

Intelligent request routing based on capability, health, and load.
"""

from __future__ import annotations

import asyncio
import logging
import random
from dataclasses import dataclass, field
from datetime import datetime, timezone

UTC = timezone.utc = UTC


from amos_model_fabric.models import (
    FabricRequest,
    FabricResponse,
    ProviderHealth,
    ProviderType,
    RoutingStrategy,
)

from .providers import BaseProvider, create_provider

logger = logging.getLogger(__name__)


@dataclass
class ProviderInstance:
    """A provider instance with health tracking."""

    provider: BaseProvider
    health: ProviderHealth = field(
        default_factory=lambda: ProviderHealth(
            provider=ProviderType.OLLAMA,
            healthy=True,
            latency_ms=0.0,
            last_checked=datetime.now(UTC).isoformat(),
        )
    )
    consecutive_failures: int = 0
    total_requests: int = 0
    failed_requests: int = 0


class LiteLLMRouter:
    """LiteLLM-style router for model request routing.

    Supports multiple routing strategies:
    - SIMPLE: First available provider
    - ROUND_ROBIN: Rotate through providers
    - LEAST_LATENCY: Pick provider with lowest latency
    - CAPABILITY: Match model capabilities to request
    - FALLBACK: Primary -> fallback chain
    """

    def __init__(
        self,
        strategy: RoutingStrategy = RoutingStrategy.SIMPLE,
        default_timeout: float = 120.0,
        max_failures: int = 3,
    ):
        self.strategy = strategy
        self.default_timeout = default_timeout
        self.max_failures = max_failures
        self._providers: dict[ProviderType, ProviderInstance] = {}
        self._round_robin_index = 0
        self._lock = asyncio.Lock()

    async def register_provider(
        self,
        provider_type: ProviderType,
        base_url: str | None = None,
        api_key: str | None = None,
    ) -> None:
        """Register a new provider with the router."""
        provider = create_provider(provider_type, base_url, api_key)

        # Check initial health
        healthy = await provider.health_check()
        health = ProviderHealth(
            provider=provider_type,
            healthy=healthy,
            latency_ms=0.0,
            last_checked=datetime.now(UTC).isoformat(),
        )

        self._providers[provider_type] = ProviderInstance(
            provider=provider,
            health=health,
        )

        logger.info(f"Registered {provider_type.value} (healthy={healthy})")

    async def unregister_provider(self, provider_type: ProviderType) -> None:
        """Remove a provider from the router."""
        if provider_type in self._providers:
            instance = self._providers.pop(provider_type)
            await instance.provider.close()
            logger.info(f"Unregistered {provider_type.value}")

    async def health_check_all(self) -> dict[ProviderType, ProviderHealth]:
        """Run health checks on all providers."""
        results = {}

        for ptype, instance in self._providers.items():
            try:
                start = datetime.now(UTC)
                healthy = await instance.provider.health_check()
                latency = (datetime.now(UTC) - start).total_seconds() * 1000

                instance.health = ProviderHealth(
                    provider=ptype,
                    healthy=healthy,
                    latency_ms=latency,
                    last_checked=datetime.now(UTC).isoformat(),
                )

                if not healthy:
                    instance.consecutive_failures += 1
                else:
                    instance.consecutive_failures = 0

                results[ptype] = instance.health

            except Exception as e:
                logger.warning(f"Health check failed for {ptype.value}: {e}")
                instance.consecutive_failures += 1
                instance.health.healthy = False
                results[ptype] = instance.health

        return results

    def _get_healthy_providers(self) -> list[ProviderInstance]:
        """Get list of healthy providers."""
        return [
            p
            for p in self._providers.values()
            if p.health.healthy and p.consecutive_failures < self.max_failures
        ]

    async def _select_provider(
        self, request: Optional[FabricRequest] = None
    ) -> Optional[ProviderInstance]:
        """Select a provider based on routing strategy."""
        healthy = self._get_healthy_providers()

        if not healthy:
            # Try to recover any unhealthy providers
            await self.health_check_all()
            healthy = self._get_healthy_providers()

        if not healthy:
            return None

        if self.strategy == RoutingStrategy.SIMPLE:
            return healthy[0]

        elif self.strategy == RoutingStrategy.ROUND_ROBIN:
            async with self._lock:
                idx = self._round_robin_index % len(healthy)
                self._round_robin_index = (self._round_robin_index + 1) % len(healthy)
                return healthy[idx]

        elif self.strategy == RoutingStrategy.LEAST_LATENCY:
            return min(healthy, key=lambda p: p.health.latency_ms)

        elif self.strategy == RoutingStrategy.RANDOM:
            return random.choice(healthy)

        elif self.strategy == RoutingStrategy.CAPABILITY:
            # For capability routing, we'd need capability registry integration
            # For now, fall back to simple
            return healthy[0]

        return healthy[0]

    async def route(self, request: FabricRequest) -> FabricResponse:
        """Route a request to the appropriate provider."""
        instance = await self._select_provider(request)

        if not instance:
            raise RuntimeError("No healthy providers available")

        start = datetime.now(UTC)
        try:
            response = await instance.provider.complete(request)

            # Update metrics
            instance.total_requests += 1
            instance.health.latency_ms = (datetime.now(UTC) - start).total_seconds() * 1000

            return response

        except Exception as e:
            instance.failed_requests += 1
            instance.consecutive_failures += 1
            logger.error(f"Request failed on {instance.provider.provider_type.value}: {e}")
            raise

    async def route_stream(self, request: FabricRequest):
        """Route a streaming request to the appropriate provider."""
        instance = await self._select_provider(request)

        if not instance:
            raise RuntimeError("No healthy providers available")

        try:
            async for chunk in instance.provider.complete_stream(request):
                yield chunk

            instance.total_requests += 1

        except Exception as e:
            instance.failed_requests += 1
            instance.consecutive_failures += 1
            logger.error(f"Stream failed on {instance.provider.provider_type.value}: {e}")
            raise

    async def get_available_providers(self) -> list[dict]:
        """Get list of registered providers with health status."""
        return [
            {
                "type": p.provider.provider_type.value,
                "base_url": p.provider.base_url,
                "healthy": p.health.healthy,
                "latency_ms": p.health.latency_ms,
                "total_requests": p.total_requests,
                "failed_requests": p.failed_requests,
            }
            for p in self._providers.values()
        ]

    async def close_all(self) -> None:
        """Close all provider connections."""
        for instance in self._providers.values():
            await instance.provider.close()
        self._providers.clear()
