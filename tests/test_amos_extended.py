"""Comprehensive test suite for AMOS SuperBrain extended components.

Tests all tools, health monitoring, and integrations without requiring API keys.
Validates system functionality at 75% health level.

References:
- pytest best practices 2025
- AI agent testing patterns (Microsoft, Dagster)
- Property-based testing for agent validation
"""

import os
import tempfile

import pytest


class TestMathFramework:
    """Test mathematical framework engine."""

    def test_framework_initialization(self):
        """Test that math framework initializes correctly."""
        from clawspring.amos_brain.mathematical_framework_engine import get_framework_engine

        engine = get_framework_engine()
        stats = engine.get_stats()

        assert stats["total_equations"] >= 22, "Should have 22+ equations"
        assert stats["total_invariants"] >= 4, "Should have 4+ invariants"

    def test_equation_query(self):
        """Test querying equations by domain."""
        from clawspring.amos_brain.mathematical_framework_engine import get_framework_engine

        engine = get_framework_engine()

        # Test UI/UX equations
        ui_eqs = engine.query_by_domain("UI_UX")
        assert len(ui_eqs) > 0, "Should have UI/UX equations"

        # Test AI equations
        ai_eqs = engine.query_by_domain("AI_ML")
        assert len(ai_eqs) > 0, "Should have AI/ML equations"

    def test_architecture_analysis(self):
        """Test architecture analysis capability."""
        from clawspring.amos_brain.mathematical_framework_engine import get_framework_engine

        engine = get_framework_engine()
        analysis = engine.analyze_architecture("Design responsive layout")

        assert "detected_domains" in analysis
        assert "recommended_frameworks" in analysis
        assert len(analysis["detected_domains"]) > 0


class TestExtendedTools:
    """Test extended tool suite."""

    def test_calculate_basic(self):
        """Test basic calculation tool."""
        from amos_brain.tools_extended import calculate

        result = calculate("2 + 2")
        assert result["result"] == 4
        assert "error" not in result

    def test_calculate_with_variables(self):
        """Test calculation with variables."""
        from amos_brain.tools_extended import calculate

        result = calculate("x * 2", {"x": 5})
        assert result["result"] == 10

    def test_calculate_math_functions(self):
        """Test mathematical functions."""
        from amos_brain.tools_extended import calculate

        result = calculate("sqrt(16)")
        assert result["result"] == 4.0

    def test_calculate_safety(self):
        """Test that unsafe operations are blocked."""
        from amos_brain.tools_extended import calculate

        result = calculate("__import__('os').system('ls')")
        assert "error" in result
        assert "Unsafe operation" in result["error"]

    def test_file_read_write(self):
        """Test file operations."""
        from amos_brain.tools_extended import file_read_write

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
            temp_path = f.name

        try:
            # Test write
            write_result = file_read_write("write", temp_path, "Hello AMOS!")
            assert write_result["success"] is True

            # Test read
            read_result = file_read_write("read", temp_path)
            assert read_result["content"] == "Hello AMOS!"
        finally:
            os.unlink(temp_path)

    def test_file_read_nonexistent(self):
        """Test reading non-existent file."""
        from amos_brain.tools_extended import file_read_write

        result = file_read_write("read", "/nonexistent/file.txt")
        assert "error" in result
        assert result["error"] == "File not found"

    def test_database_query_sqlite(self):
        """Test SQLite database operations."""
        from amos_brain.tools_extended import database_query

        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name

        try:
            # Create table
            create_result = database_query(
                "CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT)", connection_string=db_path
            )

            # Insert data
            insert_result = database_query(
                "INSERT INTO test (name) VALUES ('AMOS')", connection_string=db_path
            )

            # Query data
            select_result = database_query("SELECT * FROM test", connection_string=db_path)

            assert select_result["row_count"] == 1
            assert select_result["results"][0]["name"] == "AMOS"
        finally:
            os.unlink(db_path)

    def test_git_operations_status(self):
        """Test git status operation."""
        from amos_brain.tools_extended import git_operations

        result = git_operations("status", repo_path=".")

        # Should either succeed or fail gracefully
        assert "success" in result or "error" in result
        assert "timestamp" in result

    def test_web_search_structure(self):
        """Test web search returns correct structure."""
        from amos_brain.tools_extended import web_search

        result = web_search("Python programming", max_results=3)

        assert "query" in result
        assert "results" in result
        assert "timestamp" in result
        assert isinstance(result["results"], list)


class TestHealthMonitor:
    """Test health monitoring system."""

    def test_health_monitor_initialization(self):
        """Test health monitor initializes."""
        from amos_observability.health_monitor import HealthMonitor, HealthStatus

        monitor = HealthMonitor(check_interval=30)
        assert monitor.check_interval == 30

        # Test without starting
        health = monitor.check_health()
        assert health.overall_status == HealthStatus.UNKNOWN

    def test_component_registration(self):
        """Test registering components."""

        from amos_observability.health_monitor import ComponentHealth, HealthMonitor, HealthStatus

        monitor = HealthMonitor()

        def mock_check():
            return ComponentHealth(
                name="test_component",
                status=HealthStatus.HEALTHY,
                health_score=1.0,
                last_check=datetime.now(UTC),
                message="OK",
            )

        monitor.register_component("test", mock_check)
        assert "test" in monitor._components

    def test_health_check_execution(self):
        """Test health check runs and aggregates."""

        from amos_observability.health_monitor import ComponentHealth, HealthMonitor, HealthStatus

        monitor = HealthMonitor()

        # Register healthy component
        def healthy_check():
            return ComponentHealth(
                name="healthy",
                status=HealthStatus.HEALTHY,
                health_score=1.0,
                last_check=datetime.now(UTC),
                message="All good",
            )

        monitor.register_component("healthy", healthy_check)

        health = monitor.check_health()
        assert health.overall_score == 1.0
        assert health.overall_status == HealthStatus.HEALTHY
        assert "healthy" in health.components

    def test_alert_generation(self):
        """Test alerts are generated for unhealthy components."""

        from amos_observability.health_monitor import ComponentHealth, HealthMonitor, HealthStatus

        monitor = HealthMonitor()
        alerts = []

        def alert_handler(message: str):
            alerts.append(message)

        monitor.register_alert_handler(alert_handler)

        # Register unhealthy component
        def unhealthy_check():
            return ComponentHealth(
                name="unhealthy",
                status=HealthStatus.UNHEALTHY,
                health_score=0.0,
                last_check=datetime.now(UTC),
                message="Critical failure",
            )

        monitor.register_component("unhealthy", unhealthy_check)
        monitor.check_health()

        assert len(alerts) == 1
        assert "CRITICAL" in alerts[0]


class TestSuperBrainIntegration:
    """Test SuperBrain integration with all components."""

    def test_superbrain_initialization(self):
        """Test SuperBrain initializes all subsystems."""
        from amos_brain import get_super_brain, initialize_super_brain

        result = initialize_super_brain()
        assert result is True

        brain = get_super_brain()
        state = brain.get_state()

        assert state.health_score > 0
        assert len(state.loaded_tools) == 10

    def test_tool_discovery(self):
        """Test all tools are discoverable."""
        from amos_brain import get_super_brain

        brain = get_super_brain()
        state = brain.get_state()

        expected_tools = [
            "analyze_code_structure",
            "execute_shell_command",
            "search_files",
            "get_system_info",
            "validate_json",
            "web_search",
            "database_query",
            "file_read_write",
            "calculate",
            "git_operations",
        ]

        for tool in expected_tools:
            assert tool in state.loaded_tools, f"Tool {tool} not registered"

    def test_math_framework_integration(self):
        """Test Math Framework is integrated."""
        from amos_brain import get_super_brain

        brain = get_super_brain()
        state = brain.get_state()

        assert state.math_framework_status == "active"


class TestMCPCompliance:
    """Test MCP protocol compliance."""

    def test_tool_schemas_valid(self):
        """Test all tool schemas are valid JSON Schema."""
        from amos_brain.tools_builtin import TOOL_SCHEMAS as BUILTIN
        from amos_brain.tools_extended import TOOL_SCHEMAS as EXTENDED

        all_schemas = {**BUILTIN, **EXTENDED}

        for name, schema in all_schemas.items():
            assert schema["type"] == "object", f"{name} must be object type"
            assert "properties" in schema, f"{name} must have properties"

    def test_tool_descriptions(self):
        """Test all tools have descriptions."""
        from amos_brain.tools_builtin import TOOL_DESCRIPTIONS as BUILTIN
        from amos_brain.tools_extended import TOOL_DESCRIPTIONS as EXTENDED

        all_descs = {**BUILTIN, **EXTENDED}

        for name, desc in all_descs.items():
            assert len(desc) > 0, f"{name} must have description"
            assert len(desc) < 200, f"{name} description too long"


class TestSecurityPatterns:
    """Test security patterns are enforced."""

    def test_no_api_keys_in_code(self):
        """Verify no hardcoded API keys."""
        import inspect

        import amos_brain.tools_extended as tools_module

        source = inspect.getsource(tools_module)

        # Check for suspicious patterns
        dangerous_patterns = [
            "sk-",  # OpenAI key prefix
            "sk-ant-",  # Anthropic key prefix
        ]

        for pattern in dangerous_patterns:
            assert pattern not in source, "Potential hardcoded key found"

    def test_safe_evaluation(self):
        """Test calculation uses safe evaluation."""
        from amos_brain.tools_extended import calculate

        # Test that dangerous operations are blocked
        dangerous = [
            "__import__('os').system('rm -rf /')",
            "open('/etc/passwd').read()",
            'eval(\'__import__("os").system("ls")\')',
        ]

        for expr in dangerous:
            result = calculate(expr)
            assert "error" in result, f"Dangerous expression not blocked: {expr}"


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
