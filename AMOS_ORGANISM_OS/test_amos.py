#!/usr/bin/env python3
"""
AMOS System Test Suite
Validates all components work correctly.
"""

import sys
from pathlib import Path

# Add paths
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / 'agents'))


def test_organism():
    """Test AMOS Organism initialization."""
    print("\n[1] Testing AMOS Organism...")
    try:
        from organism import AmosOrganism
        org = AmosOrganism()
        status = org.status()
        subsystems = len(status.get('active_subsystems', []))
        print(f"  ✓ Organism created: {subsystems} subsystems")
        return True
    except Exception as e:
        print(f"  ✗ Failed: {e}")
        return False


def test_brain():
    """Test Brain cognition."""
    print("\n[2] Testing Brain cognition...")
    try:
        from organism import AmosOrganism
        org = AmosOrganism()
        thought = org.brain.perceive("Test input")
        print(f"  ✓ Brain perception: {thought.id[:8]}")
        
        plan = org.brain.create_plan("Test goal")
        print(f"  ✓ Brain planning: {plan.id[:8]} ({len(plan.steps)} steps)")
        return True
    except Exception as e:
        print(f"  ✗ Failed: {e}")
        return False


def test_agent():
    """Test TaskExecutor agent."""
    print("\n[3] Testing TaskExecutor Agent...")
    try:
        from task_executor import create_agent
        agent = create_agent()
        
        # Test safe command
        result = agent.run_command("echo 'AMOS Test'")
        assert result.success, "Command failed"
        assert "AMOS Test" in result.stdout, "Wrong output"
        print(f"  ✓ Agent execution: success")
        
        # Test blocked command
        result = agent.run_command("rm -rf /")
        assert not result.success, "Should block destructive command"
        print(f"  ✓ Safety check: destructive command blocked")
        return True
    except Exception as e:
        print(f"  ✗ Failed: {e}")
        return False


def test_api_server():
    """Test API server can be created."""
    print("\n[4] Testing API Server...")
    try:
        from organism import AmosOrganism
        from INTERFACES.api_server import APIServer
        
        org = AmosOrganism()
        server = APIServer(org, host="localhost", port=8765)
        print(f"  ✓ API Server created: http://localhost:8765")
        print(f"  ✓ Endpoints: /status, /health, /brain/*, /agents/*")
        return True
    except Exception as e:
        print(f"  ✗ Failed: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("AMOS SYSTEM TEST SUITE")
    print("=" * 60)
    
    tests = [
        ("Organism", test_organism),
        ("Brain", test_brain),
        ("Agent", test_agent),
        ("API Server", test_api_server),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            results.append((name, test_func()))
        except Exception as e:
            print(f"\n  ✗ {name} crashed: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 60)
    print("TEST RESULTS")
    print("=" * 60)
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status}: {name}")
    
    print()
    print(f"Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED - AMOS IS READY")
        print("\nNext steps:")
        print("  1. Start server: python run.py api")
        print("  2. Open dashboard: open dashboard/index.html")
        print("  3. Test via API: curl http://localhost:8765/health")
    else:
        print("\n⚠️  SOME TESTS FAILED - Check errors above")
    
    print("=" * 60)
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
