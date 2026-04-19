#!/usr/bin/env python3
"""
Test script for local LLM integration.
Verifies that downloaded Ollama models are accessible from AMOS.

Usage:
    python test_local_llm.py

Creator: Trang Phan
Version: 3.0.0
"""

import asyncio

from llm_providers import LLMRequest, Message, llm_router


async def test_local_llm():
    """Test connection to local Ollama LLMs."""
    print("=" * 60)
    print("AMOS Local LLM Integration Test")
    print("=" * 60)

    # Check available providers
    providers = llm_router.get_available_providers()
    print(f"\n📡 Available Providers: {len(providers)}")
    for p in providers:
        print(f"  - {p['name']}: {', '.join(p['models'][:5])}...")

    # Test if Ollama is available
    if "ollama" not in [p["name"] for p in providers]:
        print("\n❌ Ollama not available. Is it running?")
        print("   Start Ollama: ollama serve")
        return

    print("\n✅ Ollama detected! Testing local LLM...")

    # Test simple completion
    request = LLMRequest(
        messages=[
            Message(role="system", content="You are AMOS AI, a helpful assistant."),
            Message(role="user", content="Hello! What model are you?"),
        ],
        model="llama3.2",  # Change to your downloaded model
        temperature=0.7,
    )

    print("\n📝 Sending test message...")
    try:
        response = await llm_router.route_request(request, preference="ollama")
        print("\n✅ Response received!")
        print(f"   Model: {response.model}")
        print(f"   Provider: {response.provider}")
        print(f"   Latency: {response.latency_ms:.0f}ms")
        print(f"   Content: {response.content[:200]}...")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("   Make sure the model is downloaded: ollama pull llama3.2")

    # Test streaming
    print("\n📝 Testing streaming...")
    request.stream = True
    try:
        chunks = []
        async for chunk in llm_router.route_stream(request, preference="ollama"):
            chunks.append(chunk)
            print(chunk, end="", flush=True)
        print(f"\n✅ Stream complete! ({len(chunks)} chunks)")
    except Exception as e:
        print(f"\n❌ Streaming error: {e}")

    print("\n" + "=" * 60)
    print("Test complete!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_local_llm())
