#!/usr/bin/env python3
"""AMOS SuperBrain CLI - Rich Terminal Interface

Modern CLI for AMOS SuperBrain v3.0 using Typer and Rich.
Provides interactive terminal UI for system management at 75% health.

Usage:
    python amos_superbrain_cli.py [command]

Commands:
    status      - Show system health and components
    tools       - List and test all 10 MCP tools
    agents      - Manage A2A multi-agent system
    memory      - Inspect tiered memory architecture
    task        - Create and route tasks to agents
    config      - Validate and show configuration

References:
- Typer: Modern Python CLI framework (2025)
- Rich: Terminal formatting and UI (2025)
"""

import typer
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.tree import Tree

# Initialize console
console = Console()

# Create Typer app
app = typer.Typer(
    name="amos",
    help="AMOS SuperBrain v3.0 - AI Agent System CLI",
    add_completion=True,
    rich_markup_mode="rich",
)


def print_banner():
    """Print AMOS SuperBrain banner."""
    banner = """
[bold cyan]╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║              [bold white]AMOS SUPERBRAIN v3.0[/bold white]                            ║
║              [dim]AI Agent System - 75% Health[/dim]                    ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝[/bold cyan]
    """
    console.print(banner)


@app.callback()
def main(
    version: bool = typer.Option(False, "--version", "-v", help="Show version"),
):
    """AMOS SuperBrain CLI - Manage your AI agent system."""
    if version:
        console.print("[bold green]AMOS SuperBrain v3.0[/bold green] - 75% Health")
        raise typer.Exit()


@app.command()
def status(
    detailed: bool = typer.Option(False, "--detailed", "-d", help="Show detailed status"),
):
    """Show system health and component status."""
    print_banner()

    try:
        from amos_brain import get_super_brain
        from amos_brain.a2a_orchestrator import get_a2a_orchestrator
        from amos_brain.memory_architecture import get_memory_manager
        from clawspring.amos_brain.mathematical_framework_engine import get_framework_engine

        # Get SuperBrain state
        brain = get_super_brain()
        state = brain.get_state()

        # Health panel
        health_color = (
            "green"
            if state.health_score >= 0.75
            else "yellow"
            if state.health_score >= 0.5
            else "red"
        )
        health_panel = Panel(
            f"[bold {health_color}]Health Score: {state.health_score:.0%}[/bold {health_color}]\n"
            f"Status: {state.status}\n"
            f"Core Frozen: {state.core_frozen}",
            title="[bold]System Health[/bold]",
            border_style=health_color,
        )
        console.print(health_panel)

        # Components table
        table = Table(
            title="[bold]System Components[/bold]",
            box=box.ROUNDED,
            show_header=True,
            header_style="bold cyan",
        )
        table.add_column("Component", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Details", style="dim")

        # Math Framework
        try:
            engine = get_framework_engine()
            math_stats = engine.get_stats()
            table.add_row(
                "Math Framework", "✅ Active", f"{math_stats.get('total_equations', 0)} equations"
            )
        except Exception as e:
            table.add_row("Math Framework", "❌ Error", str(e)[:30])

        # Tools
        table.add_row("Tool Ecosystem", "✅ Active", f"{len(state.loaded_tools)} MCP tools")

        # Memory
        try:
            mem_manager = get_memory_manager()
            mem_stats = mem_manager.get_stats()
            table.add_row(
                "Memory Architecture",
                "✅ Active",
                f"L1: {mem_stats.get('l1_cache_size', 0)} entries",
            )
        except Exception as e:
            table.add_row("Memory Architecture", "❌ Error", str(e)[:30])

        # A2A
        try:
            a2a = get_a2a_orchestrator()
            a2a_stats = a2a.get_stats()
            table.add_row(
                "A2A Protocol", "✅ Active", f"{a2a_stats.get('registered_agents', 0)} agents"
            )
        except Exception as e:
            table.add_row("A2A Protocol", "❌ Error", str(e)[:30])

        # Models
        model_count = len(state.available_models)
        model_status = "✅ Active" if model_count > 0 else "⚠️  No API Keys"
        table.add_row("LLM Models", model_status, f"{model_count} providers (need keys for 100%)")

        console.print(table)

        if detailed:
            # Show loaded tools
            console.print("\n[bold]Loaded Tools:[/bold]")
            for tool in state.loaded_tools:
                console.print(f"  • {tool}")

            # Show A2A agents
            try:
                a2a = get_a2a_orchestrator()
                agents = a2a.discover_agents()
                if agents:
                    console.print("\n[bold]A2A Agents:[/bold]")
                    for agent in agents:
                        console.print(f"  • {agent.name}: {', '.join(agent.capabilities[:3])}")
            except Exception:
                pass

        # Next steps
        console.print("\n[bold yellow]Next Steps:[/bold yellow]")
        console.print(
            "  1. Set API keys for 100% health: [cyan]./scripts/configure_api_keys.sh[/cyan]"
        )
        console.print("  2. Deploy: [cyan]docker-compose up -d[/cyan]")
        console.print("  3. Create task: [cyan]amos task 'Calculate 2+2'[/cyan]")

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(1)


@app.command()
def tools(
    test: str = typer.Option(None, "--test", "-t", help="Test a specific tool"),
    list_all: bool = typer.Option(False, "--list", "-l", help="List all tools"),
):
    """List and test MCP tools."""
    try:
        from amos_brain import get_super_brain
        from amos_brain.tools_extended import (
            calculate,
            file_read_write,
            git_operations,
            web_search,
        )

        brain = get_super_brain()
        state = brain.get_state()

        console.print("[bold]MCP Tools Ecosystem[/bold]\n")

        # Built-in tools
        builtin_tree = Tree("[bold cyan]Built-in Tools (5)[/bold cyan]")
        builtin_tools = [
            ("analyze_code_structure", "Analyze Python code structure"),
            ("execute_shell_command", "Execute safe shell commands"),
            ("search_files", "Search files with patterns"),
            ("get_system_info", "Get system information"),
            ("validate_json", "Validate JSON data"),
        ]
        for name, desc in builtin_tools:
            builtin_tree.add(f"[green]{name}[/green]: {desc}")
        console.print(builtin_tree)

        # Extended tools
        console.print()
        extended_tree = Tree("[bold cyan]Extended Tools (5)[/bold cyan]")
        extended_tools = [
            ("calculate", "Safe mathematical evaluation"),
            ("file_read_write", "File I/O operations"),
            ("database_query", "SQLite/PostgreSQL/MySQL queries"),
            ("web_search", "DuckDuckGo web search"),
            ("git_operations", "Git status/log/diff"),
        ]
        for name, desc in extended_tools:
            extended_tree.add(f"[green]{name}[/green]: {desc}")
        console.print(extended_tree)

        # Test tool if requested
        if test:
            console.print(f"\n[bold]Testing tool: {test}[/bold]")

            if test == "calculate":
                result = calculate("2 + 2 * 5")
                console.print("Input: 2 + 2 * 5")
                console.print(f"Result: {result}")
            elif test == "web_search":
                result = web_search("Python programming", max_results=2)
                console.print("Query: Python programming")
                console.print(f"Results: {len(result.get('results', []))} items")
            elif test == "file_read_write":
                import os
                import tempfile

                with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
                    temp_path = f.name

                write_result = file_read_write("write", temp_path, "Hello AMOS!")
                read_result = file_read_write("read", temp_path)
                console.print(f"Write: {write_result.get('success')}")
                console.print(f"Read: {read_result.get('content')}")
                os.unlink(temp_path)
            elif test == "git_operations":
                result = git_operations("status")
                console.print(f"Git status: {result.get('success')}")
            else:
                console.print(f"[yellow]Test for '{test}' not implemented[/yellow]")

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")


@app.command()
def agents():
    """Show A2A multi-agent system status."""
    try:
        from amos_brain.a2a_orchestrator import get_a2a_orchestrator

        orchestrator = get_a2a_orchestrator()
        stats = orchestrator.get_stats()

        console.print("[bold]A2A Multi-Agent System[/bold]\n")

        # Stats panel
        stats_panel = Panel(
            f"Registered Agents: {stats.get('registered_agents', 0)}\n"
            f"Total Tasks: {stats.get('total_tasks', 0)}\n"
            f"Completed: {stats.get('completed_tasks', 0)}\n"
            f"Working: {stats.get('working_tasks', 0)}",
            title="[bold]Orchestrator Status[/bold]",
            border_style="cyan",
        )
        console.print(stats_panel)

        # Agent list
        agents = orchestrator.discover_agents()
        if agents:
            table = Table(title="[bold]Registered Agents[/bold]", box=box.ROUNDED)
            table.add_column("Name", style="cyan")
            table.add_column("Description", style="white")
            table.add_column("Capabilities", style="green")

            for agent in agents:
                caps = ", ".join(agent.capabilities[:5])
                if len(agent.capabilities) > 5:
                    caps += "..."
                table.add_row(agent.name, agent.description[:50], caps)

            console.print(table)
        else:
            console.print("[yellow]No agents registered[/yellow]")

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")


@app.command()
def task(
    message: str = typer.Argument(..., help="Task message to route"),
    capability: str = typer.Option(None, "--capability", "-c", help="Required capability"),
):
    """Create and route a task to an agent."""
    try:
        from amos_brain.a2a_orchestrator import get_a2a_orchestrator

        console.print(f"[bold]Creating Task:[/bold] {message}\n")

        orchestrator = get_a2a_orchestrator()
        task = orchestrator.route_task(message, capability=capability)

        # Task details
        console.print(
            Panel(
                f"Task ID: {task.id}\n"
                f"State: {task.state.value}\n"
                f"Assigned: {task.assigned_agent or 'Unassigned'}",
                title="[bold]Task Created[/bold]",
                border_style="green",
            )
        )

        # Messages
        if task.messages:
            console.print("[bold]Messages:[/bold]")
            for msg in task.messages:
                role_color = "blue" if msg.role.value == "user" else "green"
                console.print(
                    f"  [{role_color}]{msg.role.value}:[/{role_color}] {msg.content[:100]}"
                )

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")


@app.command()
def memory(
    stats: bool = typer.Option(False, "--stats", "-s", help="Show memory statistics"),
):
    """Inspect tiered memory architecture."""
    try:
        from amos_brain.memory_architecture import get_memory_manager

        manager = get_memory_manager()
        mem_stats = manager.get_stats()

        console.print("[bold]Tiered Memory Architecture[/bold]\n")

        # Tier visualization
        tree = Tree("[bold cyan]Memory Tiers[/bold cyan]")

        l1 = tree.add("[bold]L1 (Hot) - In-Memory Cache[/bold]")
        l1.add(f"Entries: {mem_stats.get('l1_cache_size', 0)}")
        l1.add("Speed: Fastest")

        l2 = tree.add("[bold]L2 (Warm) - SQLite Storage[/bold]")
        l2.add("Status: Persistent")
        l2.add("Speed: Fast")

        l3 = tree.add("[bold]L3 (Cold) - File Archive[/bold]")
        l3.add("Status: Archival")
        l3.add("Speed: Slower")

        console.print(tree)

        if stats:
            console.print("\n[bold]Memory Statistics:[/bold]")
            for key, value in mem_stats.items():
                console.print(f"  {key}: {value}")

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")


@app.command()
def config(
    validate: bool = typer.Option(True, "--validate/--no-validate", help="Validate configuration"),
):
    """Show and validate system configuration."""
    try:
        from amos_brain.config_validation import ConfigValidator

        validator = ConfigValidator()
        report = validator.validate()

        console.print("[bold]Configuration Status[/bold]\n")

        # Validation status
        status_color = "green" if report["valid"] else "red"
        console.print(
            Panel(
                f"Valid: {report['valid']}\n"
                f"Environment: {report['environment']}\n"
                f"LLM Providers: {report['providers_configured']} configured",
                title="[bold]Validation Result[/bold]",
                border_style=status_color,
            )
        )

        # Issues
        if report.get("issues"):
            console.print("\n[bold yellow]Issues:[/bold yellow]")
            for issue in report["issues"]:
                icon = (
                    "🔴"
                    if issue.startswith("ERROR")
                    else "🟡"
                    if issue.startswith("WARNING")
                    else "🔵"
                )
                console.print(f"  {icon} {issue}")

        # Recommendations
        if report.get("recommendations"):
            console.print("\n[bold cyan]Recommendations:[/bold cyan]")
            for rec in report["recommendations"]:
                console.print(f"  💡 {rec}")

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")


if __name__ == "__main__":
    app()
