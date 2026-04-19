"""Axiom One Test Suite

Comprehensive tests for Axiom One platform components.
Tests real features with actual execution - no mocks.
"""

import os
import tempfile
from pathlib import Path

import pytest


class TestAxiomOneGraph:
    """Test unified graph infrastructure."""

    def test_graph_imports(self):
        """Test graph module imports."""
        from axiom_one_graph import DomainType, EdgeType, NodeType

        assert DomainType.CODE.value == "code"
        assert NodeType.FILE.value == "file"
        assert EdgeType.DEPENDS_ON.value == "depends_on"

    def test_node_creation(self):
        """Test creating nodes."""
        from axiom_one_graph import AxiomNode, DomainType, NodeType

        node = AxiomNode(
            id="test-node-1",
            node_type=NodeType.FILE,
            domain=DomainType.CODE,
            name="test.py",
            properties={"path": "/test.py"},
        )
        assert node.id == "test-node-1"
        assert node.node_type == NodeType.FILE
        assert node.domain == DomainType.CODE


class TestAxiomOneRepoAutopsy:
    """Test repo autopsy engine."""

    def test_autopsy_imports(self):
        """Test autopsy module imports."""
        from axiom_one_repo_autopsy import (
            IssueCategory,
            IssueSeverity,
        )

        assert IssueSeverity.CRITICAL.value == "critical"
        assert IssueCategory.PACKAGING.value == "packaging"

    def test_issue_creation(self):
        """Test creating repo issues."""
        from axiom_one_repo_autopsy import IssueCategory, IssueSeverity, RepoIssue

        issue = RepoIssue(
            id="test-001",
            category=IssueCategory.PACKAGING,
            severity=IssueSeverity.HIGH,
            title="Missing requirements.txt",
            description="No packaging configuration found",
            affected_files=["/"],
            root_cause="Missing file",
            suggested_fix="Create requirements.txt",
            auto_fixable=True,
        )
        assert issue.id == "test-001"
        assert issue.severity == IssueSeverity.HIGH
        assert issue.auto_fixable is True

    @pytest.mark.asyncio
    async def test_static_graph_builder(self):
        """Test static graph building on temp directory."""
        from axiom_one_graph import AxiomGraph
        from axiom_one_repo_autopsy import StaticGraphBuilder

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test files
            (Path(tmpdir) / "test.py").write_text("def hello(): pass")
            (Path(tmpdir) / "README.md").write_text("# Test")

            graph = AxiomGraph()
            builder = StaticGraphBuilder(graph)
            stats = await builder.build(tmpdir, "test-repo", "test-owner")

            assert "files_added" in stats
            assert stats["repo_name"] == "test-repo"


class TestAxiomOneAgentTools:
    """Test agent tool execution - real execution."""

    def test_tool_registry(self):
        """Test tool registry initialization."""
        from axiom_one_agent_tools import get_tool_registry

        registry = get_tool_registry()
        tools = registry.list_tools()
        assert len(tools) >= 10

        tool_names = [t["name"] for t in tools]
        assert "read_file" in tool_names
        assert "write_file" in tool_names
        assert "execute_command" in tool_names

    def test_read_file_tool(self):
        """Test real file reading."""
        from axiom_one_agent_tools import execute_tool

        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("test content")
            f.flush()
            path = f.name

        try:
            result = execute_tool("read_file", file_path=path)
            assert result.success is True
            assert result.output == "test content"
        finally:
            os.unlink(path)

    def test_write_file_tool(self):
        """Test real file writing."""
        from axiom_one_agent_tools import execute_tool

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test_write.txt"
            result = execute_tool("write_file", file_path=str(path), content="written content")

            assert result.success is True
            assert path.exists()
            assert path.read_text() == "written content"

    def test_execute_command_tool(self):
        """Test real command execution."""
        from axiom_one_agent_tools import execute_tool

        result = execute_tool("execute_command", command="echo 'hello world'")

        assert result.success is True
        assert "hello world" in result.output

    def test_check_syntax_tool(self):
        """Test Python syntax checking."""
        from axiom_one_agent_tools import execute_tool

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("def valid(): pass")
            f.flush()
            path = f.name

        try:
            result = execute_tool("check_syntax", file_path=path)
            assert result.success is True
            assert "Syntax OK" in result.output
        finally:
            os.unlink(path)

    def test_analyze_imports_tool(self):
        """Test import analysis."""
        from axiom_one_agent_tools import execute_tool

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("import os\nfrom pathlib import Path\n")
            f.flush()
            path = f.name

        try:
            result = execute_tool("analyze_imports", file_path=path)
            assert result.success is True
            assert result.data is not None
            assert "count" in result.data
        finally:
            os.unlink(path)


class TestAxiomOneWebSocket:
    """Test WebSocket streaming infrastructure."""

    def test_stream_manager(self):
        """Test stream manager initialization."""
        from axiom_one_websocket import StreamEventType, get_stream_manager

        manager = get_stream_manager()
        assert manager is not None

        # Test event creation
        event = manager.create_autopsy_start_event("session-1", "/repo", "my-repo")
        assert event.event_type == StreamEventType.AUTOPSY_START.value
        assert event.session_id == "session-1"
        assert "my-repo" in event.payload["message"]

    def test_event_history(self):
        """Test event history tracking."""
        from axiom_one_websocket import get_stream_manager

        manager = get_stream_manager()

        # Create events
        for i in range(5):
            event = manager.create_autopsy_step_event(
                "test-session", f"step-{i}", "running", i * 0.25
            )
            manager._event_history.setdefault("test-session", []).append(event)

        # Retrieve history
        history = manager.get_event_history("test-session", limit=3)
        assert len(history) == 3


class TestAxiomOneFixGenerator:
    """Test fix generator."""

    def test_fix_generator_imports(self):
        """Test fix generator imports."""
        from axiom_one_fix_generator import (
            FixGenerator,
            GeneratedFix,
        )

        assert GeneratedFix is not None
        assert FixGenerator is not None


class TestAxiomOneBrainIntegration:
    """Test brain integration."""

    def test_brain_facade_imports(self):
        """Test brain facade imports."""
        from clawspring.amos_brain.facade import BrainClient, BrainThinkResponse

        assert BrainClient is not None
        assert BrainThinkResponse is not None

    def test_brain_bridge_imports(self):
        """Test brain bridge imports."""
        from axiom_one_brain_bridge import AxiomOneBrainBridge, get_brain_bridge

        assert AxiomOneBrainBridge is not None
        assert get_brain_bridge is not None


class TestAxiomOneAgentPlane:
    """Test agent plane."""

    def test_agent_plane_imports(self):
        """Test agent plane imports."""
        from axiom_one_agent_plane import AgentPlane, AgentRole

        assert AgentPlane is not None
        assert AgentRole is not None

    def test_agent_roles(self):
        """Test agent role definitions."""
        from axiom_one_agent_plane import AgentRole

        roles = list(AgentRole)
        assert len(roles) >= 15
        assert AgentRole.REPO_DEBUGGER in roles
        assert AgentRole.CODE_GENERATOR in roles


class TestAxiomOneIntegration:
    """Integration tests across components."""

    @pytest.mark.asyncio
    async def test_full_autopsy_workflow(self):
        """Test complete autopsy workflow with graph building."""
        from axiom_one_graph import AxiomGraph
        from axiom_one_repo_autopsy import RepoAutopsyEngine

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a minimal Python project
            (Path(tmpdir) / "main.py").write_text("print('hello')")
            (Path(tmpdir) / "requirements.txt").write_text("pytest\n")

            graph = AxiomGraph()
            engine = RepoAutopsyEngine(graph)
            report = await engine.autopsy(tmpdir, "test-repo", "test-owner")

            assert report is not None
            assert report.repo_name == "test-repo"
            assert len(report.validation_results) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
