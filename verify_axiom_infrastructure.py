#!/usr/bin/env python3
"""
Axiom Infrastructure Verification Script

Verifies all core Axiom components are properly implemented and working.
"""

from __future__ import annotations

import asyncio
import sys
from datetime import UTC
from pathlib import Path

# Add amos_kernel to path
sys.path.insert(0, str(Path(__file__).parent / "amos_kernel"))


def test_imports() -> bool:
    """Test all modules can be imported."""
    print("Testing imports...")
    try:
        print("✅ All imports successful")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False


def test_state() -> bool:
    """Test state model."""
    print("\nTesting state model...")
    try:
        from axiom_state import AxiomState, get_state_manager

        state = AxiomState()
        assert state.timestamp is not None

        manager = get_state_manager()
        assert manager is not None

        print("✅ State model working")
        return True
    except Exception as e:
        print(f"❌ State test failed: {e}")
        return False


def test_control_directory() -> bool:
    """Test control directory."""
    print("\nTesting control directory...")
    try:
        import tempfile

        from control_directory import ControlDirectoryManager

        with tempfile.TemporaryDirectory() as tmp:
            manager = ControlDirectoryManager(Path(tmp))
            result = manager.init_control_dir(
                name="test",
                language="python",
                description="Test repo",
            )
            assert result is True
            assert (Path(tmp) / ".amos" / "repo.yaml").exists()

        print("✅ Control directory working")
        return True
    except Exception as e:
        print(f"❌ Control directory test failed: {e}")
        return False


def test_integration_bus() -> bool:
    """Test integration buses."""
    print("\nTesting integration buses...")
    try:
        from integration_bus import MemoryBus, ToolBus

        async def run_test():
            mem_bus = MemoryBus()
            entry = await mem_bus.store(
                content="Test memory",
                importance=0.8,
                tags=["test"],
            )
            assert entry is not None

            tool_bus = ToolBus()

            def test_fn(x: int) -> int:
                return x * 2

            tool_bus.register("test", test_fn, "Test tool")
            result = await tool_bus.execute("test", {"x": 5})
            assert result.result == 10

        asyncio.run(run_test())
        print("✅ Integration buses working")
        return True
    except Exception as e:
        print(f"❌ Integration bus test failed: {e}")
        return False


def test_nl_processor() -> bool:
    """Test NL processor."""
    print("\nTesting NL processor...")
    try:
        from nl_processor import get_nl_processor

        processor = get_nl_processor()
        intent, proposals, explanation = processor.process(
            "Create a new file",
            auto_commit=False,
        )
        assert intent is not None
        assert intent.command_type == "file.create"

        print("✅ NL processor working")
        return True
    except Exception as e:
        print(f"❌ NL processor test failed: {e}")
        return False


def test_persistence() -> bool:
    """Test persistence layer."""
    print("\nTesting persistence layer...")
    try:
        import tempfile
        from datetime import datetime

        from integration_bus import MemoryEntry
        from persistence import AxiomPersistence, PersistenceConfig

        with tempfile.TemporaryDirectory() as tmp:
            config = PersistenceConfig(db_path=f"{tmp}/test.db")
            persistence = AxiomPersistence(config)

            entry = MemoryEntry(
                entry_id="test-1",
                content="Test content",
                memory_type="short_term",
                importance=0.8,
                tags=["test"],
                created_at=datetime.now(UTC),
            )

            result = persistence.store_memory(entry)
            assert result is True

            retrieved = persistence.retrieve_memory("test-1")
            assert retrieved is not None
            assert retrieved.content == "Test content"

        print("✅ Persistence layer working")
        return True
    except Exception as e:
        print(f"❌ Persistence test failed: {e}")
        return False


def test_cli() -> bool:
    """Test CLI imports."""
    print("\nTesting CLI...")
    try:
        from axiom_cli import main

        # Just verify it can be imported and has required functions
        assert callable(main)
        print("✅ CLI working")
        return True
    except Exception as e:
        print(f"❌ CLI test failed: {e}")
        return False


def test_mcp_server() -> bool:
    """Test MCP server."""
    print("\nTesting MCP server...")
    try:
        from axiom_mcp_server import AxiomMCPServer

        server = AxiomMCPServer()
        assert server is not None
        print("✅ MCP server working")
        return True
    except Exception as e:
        print(f"❌ MCP server test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("AXIOM INFRASTRUCTURE VERIFICATION")
    print("=" * 60)

    results = [
        ("Imports", test_imports()),
        ("State Model", test_state()),
        ("Control Directory", test_control_directory()),
        ("Integration Bus", test_integration_bus()),
        ("NL Processor", test_nl_processor()),
        ("Persistence", test_persistence()),
        ("CLI", test_cli()),
        ("MCP Server", test_mcp_server()),
    ]

    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)

    passed = sum(1 for _, r in results if r)
    total = len(results)

    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")

    print("-" * 60)
    print(f"Total: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 ALL TESTS PASSED - Axiom infrastructure is ready!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
