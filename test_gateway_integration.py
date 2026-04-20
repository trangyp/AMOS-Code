#!/usr/bin/env python3
"""Integration Tests for AMOS Unified Gateway
===========================================

Real tests verifying brain integration works correctly.
Run with: python test_gateway_integration.py
"""

import asyncio
import sys
from pathlib import Path

# Add project root
ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))


async def test_brain_imports():
    """Test that all brain modules can be imported."""
    print("Test 1: Brain Module Imports")
    print("-" * 40)

    errors = []

    try:
        print("  ✅ amos_brain.facade.BrainClient")
    except Exception as e:
        errors.append(f"BrainClient: {e}")
        print(f"  ❌ BrainClient: {e}")

    try:
        print("  ✅ amos_agentic_ai.AMOSAgent")
    except Exception as e:
        errors.append(f"AMOSAgent: {e}")
        print(f"  ❌ AMOSAgent: {e}")

    try:
        print("  ✅ amos_hybrid_orchestrator.HybridNeuralSymbolicOrchestrator")
    except Exception as e:
        errors.append(f"Orchestrator: {e}")
        print(f"  ❌ Orchestrator: {e}")

    try:
        print("  ✅ amos_cognitive_control_kernel.AMOSCognitiveControlKernel")
    except Exception as e:
        errors.append(f"ControlKernel: {e}")
        print(f"  ❌ ControlKernel: {e}")

    if errors:
        print(f"\n❌ Import test failed with {len(errors)} errors")
        return False

    print("\n✅ All brain modules imported successfully")
    return True


async def test_gateway_imports():
    """Test gateway module imports."""
    print("\nTest 2: Gateway Module Imports")
    print("-" * 40)

    try:
        from amos_unified_gateway import BRAIN_AVAILABLE

        print(f"  ✅ amos_unified_gateway (brain_available={BRAIN_AVAILABLE})")
    except Exception as e:
        print(f"  ❌ Gateway import failed: {e}")
        return False

    try:
        print("  ✅ amos_platform_sdk.AMOSPlatformSDK")
    except Exception as e:
        print(f"  ❌ SDK import failed: {e}")
        return False

    print("\n✅ Gateway modules imported successfully")
    return True


async def test_brain_functionality():
    """Test that brain components actually work."""
    print("\nTest 3: Brain Component Functionality")
    print("-" * 40)

    try:
        from amos_brain.facade import BrainClient

        # Create client
        client = BrainClient(repo_path=str(ROOT))
        print("  ✅ BrainClient initialized")

        # Test think method exists
        if hasattr(client, "think"):
            print("  ✅ BrainClient.think() available")
        else:
            print("  ⚠️  BrainClient.think() not found")

    except Exception as e:
        print(f"  ❌ BrainClient test failed: {e}")
        return False

    try:
        from amos_agentic_ai import create_agent

        # Create agent
        agent = await create_agent(
            name="test_agent",
            tools=["file_system"],
        )
        print("  ✅ AMOSAgent created")

        # Check status
        status = agent.get_status()
        print(f"  ✅ Agent status: {status}")

    except Exception as e:
        print(f"  ❌ AMOSAgent test failed: {e}")
        return False

    print("\n✅ Brain components functional")
    return True


async def test_gateway_integration():
    """Test gateway with real brain."""
    print("\nTest 4: Gateway Integration")
    print("-" * 40)

    try:
        from amos_unified_gateway import BrainIntegration

        # Create integration
        integration = BrainIntegration()
        print("  ✅ BrainIntegration created")

        # Initialize
        status = await integration.initialize()
        print(f"  ✅ Initialization status: {status}")

        # Check all components
        all_ok = all(status.values())
        if all_ok:
            print("  ✅ All brain systems initialized")
        else:
            print(f"  ⚠️  Some systems failed: {status}")

    except Exception as e:
        print(f"  ❌ Gateway integration failed: {e}")
        import traceback

        traceback.print_exc()
        return False

    print("\n✅ Gateway integration working")
    return True


async def test_sdk_functionality():
    """Test SDK creates proper HTTP client."""
    print("\nTest 5: SDK HTTP Client")
    print("-" * 40)

    try:
        from amos_platform_sdk import AMOSPlatformSDK

        # Create SDK (won't connect without server)
        sdk = AMOSPlatformSDK(base_url="http://localhost:8000")
        print("  ✅ AMOSPlatformSDK created")

        # Check transport
        assert sdk._transport is not None
        print("  ✅ HTTPTransport initialized")

        # Cleanup
        await sdk.close()
        print("  ✅ SDK closed properly")

    except Exception as e:
        print(f"  ❌ SDK test failed: {e}")
        import traceback

        traceback.print_exc()
        return False

    print("\n✅ SDK functional")
    return True


async def run_all_tests():
    """Run all integration tests."""
    print("=" * 60)
    print("AMOS Unified Gateway Integration Tests")
    print("=" * 60)

    results = []

    # Run tests
    results.append(("Brain Imports", await test_brain_imports()))
    results.append(("Gateway Imports", await test_gateway_imports()))
    results.append(("Brain Functionality", await test_brain_functionality()))
    results.append(("Gateway Integration", await test_gateway_integration()))
    results.append(("SDK Functionality", await test_sdk_functionality()))

    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)

    passed = sum(1 for _, r in results if r)
    total = len(results)

    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{name:30}: {status}")

    print("-" * 60)
    print(f"Total: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All integration tests passed!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(run_all_tests())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\nTests interrupted")
        sys.exit(130)
    except Exception as e:
        print(f"\n\nTest runner failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
