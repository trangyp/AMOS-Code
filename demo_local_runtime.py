#!/usr/bin/env python3
"""Demo: AMOS Local Runtime with Local LLMs.

Shows how to use the new local-model-first architecture with:
- Ollama backend
- AMOS governance layer
- Streaming responses
- Metrics tracking
"""

from __future__ import annotations

import os
import sys

# Add project to path  # noqa: E402
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # noqa: E402

from amos_brain.local_runtime import create_local_runtime  # noqa: E402


def demo_basic_usage():
    """Demo: Basic usage with default Ollama backend."""
    print("=" * 60)
    print("Demo 1: Basic Usage with Ollama")
    print("=" * 60)
    print()

    # Create runtime with default settings (Ollama)
    # Requires: export AMOS_MODEL=llama3.2:latest
    runtime = create_local_runtime()

    print("Initializing...")
    status = runtime.initialize()

    if not status.get("ready"):
        print("Failed to initialize:")
        print(f"  Backend: {status.get('backend', {}).get('error')}")
        print("\nMake sure Ollama is running: ollama serve")
        return False

    print(f"✓ Backend: {status['backend']['backend']}")
    print(f"✓ Model: {status['backend']['model']}")
    print()

    # Single query
    print("Query: What is the Rule of 2 in AMOS?")
    print("-" * 40)
    response = runtime.reply("What is the Rule of 2 in AMOS?")

    if response.get("ok"):
        print(f"Response: {response['text'][:200]}...")
        print()
        print(f"Routing: {response.get('routing')}")
    else:
        print(f"Error: {response.get('error')}")

    return True


def demo_metrics():
    """Demo: Metrics tracking."""
    print()
    print("=" * 60)
    print("Demo 2: Metrics Tracking")
    print("=" * 60)
    print()

    runtime = create_local_runtime()

    # Initialize if not already
    if not runtime.is_ready:
        runtime.initialize()

    # Make a few queries
    queries = [
        "What is machine learning?",
        "Explain quantum computing",
    ]

    for query in queries:
        print(f"Query: {query}")
        response = runtime.reply(query)
        if response.get("ok"):
            print("  ✓ Success")
        else:
            err = response.get("error")
            print(f"  ✗ Failed: {err}")
        print()

    # Get metrics summary
    metrics = runtime.get_metrics_summary()
    print("Metrics Summary:")
    print(f"  Total requests: {metrics.get('total_requests', 0)}")
    print(f"  Success rate: {metrics.get('success_rate', 0):.1%}")
    print(f"  Avg latency: {metrics.get('avg_latency_ms', 0):.0f}ms")
    print(f"  P95 latency: {metrics.get('p95_latency_ms', 0):.0f}ms")


def demo_health_check():
    """Demo: Health check functionality."""
    print()
    print("=" * 60)
    print("Demo 3: Health Check")
    print("=" * 60)
    print()

    runtime = create_local_runtime()
    status = runtime.get_status()

    print(f"Runtime ready: {status.get('ready')}")
    print()

    if status.get("backend"):
        backend = status["backend"]
        print(f"Backend status: {backend.get('status')}")
        print(f"Backend type: {backend.get('backend')}")
        print(f"Model: {backend.get('model')}")

        if backend.get("error"):
            print(f"Error: {backend['error']}")
        if backend.get("help"):
            print(f"Help: {backend['help']}")


def main():
    """Run all demos."""
    print(r"""
╔══════════════════════════════════════════════════════════════╗
║                                                                ║
║   AMOS Local Runtime - Demo                                    ║
║                                                                ║
║   Demonstrates:                                                ║
║   • Ollama/LM Studio/vLLM backends                             ║
║   • AMOS governance layer                                      ║
║   • Streaming responses                                        ║
║   • Metrics tracking                                           ║
║                                                                ║
╚══════════════════════════════════════════════════════════════╝
    """)

    print("Prerequisites:")
    print("  1. Ollama installed and running: ollama serve")
    print("  2. Model pulled: ollama pull llama3.2:latest")
    print("  3. Or set custom model: export AMOS_MODEL=your-model")
    print()
    input("Press Enter to start demo...")
    print()

    # Run demos
    if not demo_basic_usage():
        print("\nDemo stopped - backend not available")
        return 1

    demo_metrics()
    demo_health_check()

    print()
    print("=" * 60)
    print("Demo Complete!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("  python amos_local.py           # Interactive mode")
    print("  python amos_local.py --check   # Health check only")
    print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
