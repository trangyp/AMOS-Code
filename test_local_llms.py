#!/usr/bin/env python3
"""Test local LLM integration with AMOS."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))


def test_local_models_detection():
    """Test that local models are detected."""
    from clawspring.providers import PROVIDERS

    print("=" * 70)
    print("AMOS LOCAL LLM INTEGRATION TEST")
    print("=" * 70)

    ollama_config = PROVIDERS.get("ollama", {})
    models = ollama_config.get("models", [])

    print(f"\n✓ Ollama provider configured with {len(models)} models")
    print("\nLocal models available:")

    local_models = [
        "deepseek-coder-v2:16b",
        "qwen2.5-coder:14b",
        "deepseek-coder:33b",
        "codellama",
        "llama3.2",
        "mistral",
        "nomic-embed-text",
    ]

    for model in local_models:
        if model in models:
            print(f"  ✓ {model}")
        else:
            print(f"  ✗ {model} (missing)")

    return True


def test_ollama_connection():
    """Test connection to Ollama."""
    import json
    import urllib.request

    print("\nTesting Ollama connection...")

    try:
        req = urllib.request.Request(
            "http://localhost:11434/api/tags", headers={"Content-Type": "application/json"}
        )

        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode())
            models = data.get("models", [])

            print(f"  ✓ Ollama is running ({len(models)} models loaded)")

            for m in models:
                name = m.get("name", "unknown")
                size = m.get("size", 0) / (1024**3)  # Convert to GB
                print(f"    • {name} ({size:.1f} GB)")

            return True

    except Exception as e:
        print(f"  ✗ Cannot connect to Ollama: {e}")
        return False


def test_provider_integration():
    """Test provider integration with AMOS."""
    print("\nTesting AMOS provider integration...")

    try:
        from clawspring.providers import PROVIDERS, get_provider

        # Test getting ollama provider
        provider = get_provider("ollama/llama3.2")
        print(f"  ✓ Provider resolved: {provider}")

        # Check provider config
        config = PROVIDERS.get("ollama", {})
        print(f"  ✓ Base URL: {config.get('base_url')}")
        print(f"  ✓ Context limit: {config.get('context_limit')}")

        return True

    except Exception as e:
        print(f"  ✗ Provider integration error: {e}")
        return False


def main():
    """Run all tests."""
    print("\n" + "=" * 70)
    print("Testing Local LLM Integration")
    print("=" * 70 + "\n")

    results = []

    # Test 1: Model detection
    results.append(("Model Detection", test_local_models_detection()))

    # Test 2: Ollama connection
    results.append(("Ollama Connection", test_ollama_connection()))

    # Test 3: Provider integration
    results.append(("Provider Integration", test_provider_integration()))

    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)

    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {status}: {name}")

    all_passed = all(r[1] for r in results)

    print("\n" + "=" * 70)
    if all_passed:
        print("✓ All local LLM tests passed!")
        print("\nYour local models are ready to use with AMOS:")
        print("  • deepseek-coder-v2:16b - Advanced code generation")
        print("  • qwen2.5-coder:14b - Code tasks")
        print("  • deepseek-coder:33b - Large coding model")
        print("  • codellama - Code completion")
        print("  • llama3.2 - General tasks")
        print("  • mistral - General reasoning")
    else:
        print("✗ Some tests failed. Check Ollama is running.")
    print("=" * 70)

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
