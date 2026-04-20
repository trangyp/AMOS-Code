"""
Test Suite for Axiom Core Components

Tests the complete Axiom kernel infrastructure including:
- State model operations
- Control directory lifecycle
- Integration bus messaging
- NL processor command lifecycle
- Persistence layer
- CLI commands
"""

from __future__ import annotations

import tempfile
from datetime import UTC, datetime
from pathlib import Path

import pytest

# Import all Axiom components
from axiom_state import (
    AxiomState,
    ClassicalState,
    QuantumState,
    get_state_manager,
)
from control_directory import (
    ControlDirectoryManager,
    GlossaryEntry,
)
from integration_bus import (
    BusMessage,
    BusType,
    MemoryBus,
    ToolBus,
    get_bus_coordinator,
)
from nl_processor import (
    IntentIR,
    PatchProposal,
    get_nl_processor,
)
from persistence import (
    PersistenceConfig,
    get_persistence,
)


class TestAxiomState:
    """Test suite for AxiomState - coupled hyperbundle state model."""

    def test_state_creation(self) -> None:
        """Test creating a basic state."""
        state = AxiomState()
        assert state is not None
        assert state.timestamp is not None
        assert state.version == "1.0"

    def test_classical_state(self) -> None:
        """Test classical state component."""
        classical = ClassicalState(
            coherence=0.9,
            activation=0.8,
            code_files=["test.py"],
        )
        assert classical.coherence == 0.9
        assert classical.activation == 0.8
        assert "test.py" in classical.code_files

    def test_quantum_state(self) -> None:
        """Test quantum state component."""
        quantum = QuantumState(
            superposition=True,
            entanglement_links=["link1", "link2"],
        )
        assert quantum.superposition is True
        assert len(quantum.entanglement_links) == 2

    def test_state_manager_singleton(self) -> None:
        """Test state manager singleton pattern."""
        sm1 = get_state_manager()
        sm2 = get_state_manager()
        assert sm1 is sm2

    def test_state_hash_stability(self) -> None:
        """Test that state hash is stable for same input."""
        state1 = AxiomState()
        state2 = AxiomState()
        # Hash should be same if content is same
        assert state1.canonical_hash == state2.canonical_hash


class TestControlDirectory:
    """Test suite for ControlDirectoryManager."""

    def test_control_dir_init(self, tmp_path: Path) -> None:
        """Test control directory initialization."""
        with tempfile.TemporaryDirectory() as tmp:
            config = PersistenceConfig(db_path=f"{tmp}/test.db")
            manager = ControlDirectoryManager(Path(tmp))

            result = manager.init_control_dir(
                name="test-repo",
                language="python",
                description="Test repository",
            )

            assert result is True
            assert (Path(tmp) / ".amos" / "repo.yaml").exists()

    def test_glossary_management(self) -> None:
        """Test glossary CRUD operations."""
        with tempfile.TemporaryDirectory() as tmp:
            manager = ControlDirectoryManager(Path(tmp))
            manager.init_control_dir(name="test", language="python")

            entry = GlossaryEntry(
                term="TestTerm",
                definition="A test term",
                domain="testing",
            )

            manager.add_glossary_entry(entry)
            glossary = manager.load_glossary()

            assert "TestTerm" in glossary.terms
            assert glossary.terms["TestTerm"].definition == "A test term"


class TestIntegrationBus:
    """Test suite for integration buses."""

    @pytest.mark.asyncio
    async def test_memory_bus(self) -> None:
        """Test MemoryBus operations."""
        bus = MemoryBus()

        # Test store
        entry = await bus.store(
            content="Test memory",
            importance=0.8,
            tags=["test"],
            memory_type="short_term",
        )

        assert entry is not None
        assert entry.content == "Test memory"
        assert entry.importance == 0.8

        # Test retrieve
        retrieved = await bus.retrieve(entry.entry_id)
        assert retrieved is not None
        assert retrieved.content == "Test memory"

    @pytest.mark.asyncio
    async def test_tool_bus(self) -> None:
        """Test ToolBus operations."""
        bus = ToolBus()

        # Register a test tool
        def test_tool(x: int) -> int:
            return x * 2

        bus.register("test_tool", test_tool, "Test tool")

        # Execute the tool
        result = await bus.execute("test_tool", {"x": 5})
        assert result.success is True
        assert result.result == 10

    @pytest.mark.asyncio
    async def test_bus_message(self) -> None:
        """Test BusMessage creation and routing."""
        msg = BusMessage(
            bus_type=BusType.MEMORY,
            topic="test.topic",
            payload={"data": "test"},
        )

        assert msg.bus_type == BusType.MEMORY
        assert msg.topic == "test.topic"
        assert msg.payload["data"] == "test"


class TestNLProcessor:
    """Test suite for NLProcessor."""

    def test_intent_ir_creation(self) -> None:
        """Test IntentIR creation."""
        intent = IntentIR(
            intent_id="test-123",
            raw_text="Create a new file",
            command_type="file.create",
            entities={"filename": "test.py"},
        )

        assert intent.intent_id == "test-123"
        assert intent.raw_text == "Create a new file"
        assert intent.command_type == "file.create"

    def test_patch_proposal(self) -> None:
        """Test PatchProposal creation."""
        proposal = PatchProposal(
            proposal_id="prop-1",
            target_file="test.py",
            patch_content="print('hello')",
            operation="create",
        )

        assert proposal.proposal_id == "prop-1"
        assert proposal.target_file == "test.py"
        assert proposal.operation == "create"

    def test_processor_singleton(self) -> None:
        """Test NLProcessor singleton."""
        p1 = get_nl_processor()
        p2 = get_nl_processor()
        assert p1 is p2


class TestPersistence:
    """Test suite for persistence layer."""

    def test_persistence_singleton(self) -> None:
        """Test persistence singleton."""
        p1 = get_persistence()
        p2 = get_persistence()
        assert p1 is p2

    def test_memory_persistence(self) -> None:
        """Test memory entry persistence."""
        with tempfile.TemporaryDirectory() as tmp:
            config = PersistenceConfig(db_path=f"{tmp}/test.db")
            persistence = get_persistence(config)

            from integration_bus import MemoryEntry

            entry = MemoryEntry(
                entry_id="mem-1",
                content="Test memory",
                memory_type="short_term",
                importance=0.8,
                tags=["test"],
                created_at=datetime.now(UTC),
            )

            # Store
            result = persistence.store_memory(entry)
            assert result is True

            # Retrieve
            retrieved = persistence.retrieve_memory("mem-1")
            assert retrieved is not None
            assert retrieved.content == "Test memory"

    def test_stats(self) -> None:
        """Test database statistics."""
        with tempfile.TemporaryDirectory() as tmp:
            config = PersistenceConfig(db_path=f"{tmp}/test.db")
            persistence = get_persistence(config)

            stats = persistence.get_stats()
            assert "database_path" in stats
            assert "memory_entries" in stats


class TestIntegration:
    """Integration tests combining multiple components."""

    def test_full_command_lifecycle(self) -> None:
        """Test complete NL command lifecycle."""
        processor = get_nl_processor()

        # Process a command
        intent, proposals, explanation = processor.process(
            "Create a new Python file called test.py",
            auto_commit=False,
        )

        assert intent is not None
        assert intent.command_type == "file.create"
        assert "test.py" in str(intent.entities)

        # Verify proposals generated
        assert len(proposals) > 0

        # Get ledger
        ledger = processor.get_ledger(intent.intent_id)
        assert ledger is not None
        assert ledger.intent_id == intent.intent_id

    @pytest.mark.asyncio
    async def test_bus_coordinator(self) -> None:
        """Test bus coordinator with multiple buses."""
        coordinator = get_bus_coordinator()

        # Start buses
        await coordinator.start_all()

        # Get bus status
        status = coordinator.get_status()
        assert BusType.MEMORY in status
        assert BusType.TOOL in status

        # Stop buses
        await coordinator.stop_all()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
