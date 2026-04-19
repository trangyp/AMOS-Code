#!/usr/bin/env python3
"""AMOS Model Fabric + SuperBrain Integration Demo

This script demonstrates real integration between:
- SuperBrain (model router)
- Model Fabric Gateway (provider abstraction)
- Local LLM providers (Ollama, LM Studio, etc.)
"""

import asyncio
import sys

# Add repo to path
sys.path.insert(0, "/Users/nguyenxuanlinh/Documents/Trang Phan/Downloads/AMOS-code")

from amos_brain.model_router import ModelConfig, ModelRouter
from amos_model_fabric import get_gateway


async def demo_model_fabric():
    """Demo the Model Fabric Gateway."""
    print("=" * 70)
    print("AMOS MODEL FABRIC + SUPERBRAIN INTEGRATION DEMO")
    print("=" * 70)

    # Initialize Model Fabric Gateway
    print("\n[1] Initializing Model Fabric Gateway...")
    gateway = get_gateway()
    await gateway.initialize()
    print("   ✅ Gateway initialized")

    # Check provider health
    print("\n[2] Checking Provider Health...")
    health = await gateway.health_check()
    for provider, is_healthy in health.items():
        status = "✅" if is_healthy else "❌"
        print(f"   {status} {provider.value}")

    # List available models
    print("\n[3] Available Models:")
    models = gateway.list_available_models()
    if models:
        for model in models[:5]:
            caps = ", ".join([c.name for c in model.capabilities.capabilities])[:40]
            avail = "✅" if model.is_available else "❌"
            print(f"   {avail} {model.name} ({model.provider.value}) - {caps}")
    else:
        print("   No models discovered (providers may be offline)")

    # Test SuperBrain ModelRouter integration
    print("\n[4] Testing SuperBrain ModelRouter...")
    router = ModelRouter(memory_governance=None)

    # Register a test model if Ollama is available
    if health.get(ProviderType.OLLAMA):
        router.register_model(
            ModelConfig(
                model_id="qwen2.5-coder:14b",
                provider="ollama",
                healthy=True,
            )
        )
        print("   ✅ Registered qwen2.5-coder:14b with ModelRouter")

    # Show metrics
    print("\n[5] Gateway Metrics:")
    metrics = gateway.get_metrics()
    print(f"   Total requests: {metrics.total_requests}")
    print(f"   Successful: {metrics.successful_requests}")
    print(f"   Failed: {metrics.failed_requests}")
    print(f"   Avg latency: {metrics.avg_latency_ms:.1f}ms")

    # Test actual completion if Ollama available
    if health.get(ProviderType.OLLAMA) and models:
        print("\n[6] Testing Real Completion...")
        try:
            from amos_model_fabric.schemas import FabricRequest

            request = FabricRequest(
                messages=[{"role": "user", "content": "Say 'AMOS is working' and nothing else"}],
                model="qwen2.5-coder:14b",
                temperature=0.1,
                max_tokens=50,
            )

            response = await asyncio.wait_for(gateway.complete(request), timeout=30)
            print(f"   Response: {response.content[:100]}...")
            print(f"   Latency: {response.latency_ms:.0f}ms")
            print(f"   Provider: {response.provider.value}")
        except Exception as e:
            print(f"   ⚠️  Could not test completion: {e}")

    # Cleanup
    await gateway.close()

    print("\n" + "=" * 70)
    print("Demo complete!")
    print("=" * 70)


if __name__ == "__main__":
    from amos_model_fabric.schemas import ProviderType

    asyncio.run(demo_model_fabric())
