#!/usr/bin/env python3
"""AMOS Ecosystem Controller - Unified Interface for Complete System.

Round 10: The Master Controller - One entry point for all 10 tools.

This controller:
1. Provides single entry point for complete ecosystem
2. Intelligently routes requests to appropriate tools
3. Orchestrates multi-tool workflows
4. Offers unified CLI experience
5. Becomes the only interface needed

Usage:
    python amos_ecosystem_controller.py "Analyze this decision"
    python amos_ecosystem_controller.py --interactive
    python amos_ecosystem_controller.py --run-all
"""

import subprocess
import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))


class ToolType(Enum):
    """Types of ecosystem tools."""

    BRAIN_DEMO = "brain_demo"
    KNOWLEDGE = "knowledge"
    GENERATOR = "generator"
    WORKFLOW = "workflow"
    DASHBOARD = "dashboard"
    AGENT = "agent"
    SELF_DRIVING = "self_driving"
    META_COGNITIVE = "meta_cognitive"
    SHOWCASE = "showcase"
    CONTROLLER = "controller"


@dataclass
class EcosystemTool:
    """Represents an ecosystem tool."""

    name: str
    tool_type: ToolType
    description: str
    command: str
    lines: int
    keywords: list[str]


class AMOSEcosystemController:
    """Unified controller for the complete AMOS ecosystem.

    Provides single entry point to all 10 tools:
    - Intelligent routing based on user intent
    - Multi-tool orchestration
    - Unified CLI experience
    - Complete ecosystem access
    """

    def __init__(self):
        self.root = Path(__file__).parent
        self.tools: dict[ToolType, EcosystemTool] = {}
        self._register_tools()

    def _register_tools(self) -> None:
        """Register all ecosystem tools."""
        self.tools = {
            ToolType.BRAIN_DEMO: EcosystemTool(
                name="Brain Live Demo",
                tool_type=ToolType.BRAIN_DEMO,
                description="Demonstrates Rule of 2/4, L1-L6 brain analysis",
                command="python amos_brain_live_demo.py",
                lines=273,
                keywords=["analyze", "decision", "brain", "think", "rule", "demo"],
            ),
            ToolType.KNOWLEDGE: EcosystemTool(
                name="Knowledge Explorer",
                tool_type=ToolType.KNOWLEDGE,
                description="Search 1,110+ knowledge files",
                command="python amos_knowledge_explorer.py",
                lines=527,
                keywords=["search", "knowledge", "find", "explore", "lookup", "query"],
            ),
            ToolType.GENERATOR: EcosystemTool(
                name="Project Generator",
                tool_type=ToolType.GENERATOR,
                description="Generate AMOS-powered projects",
                command="python amos_project_generator.py",
                lines=560,
                keywords=["build", "create", "generate", "project", "scaffold", "make"],
            ),
            ToolType.WORKFLOW: EcosystemTool(
                name="Master Workflow",
                tool_type=ToolType.WORKFLOW,
                description="4-phase cognitive pipeline orchestration",
                command="python amos_master_workflow.py",
                lines=460,
                keywords=["workflow", "pipeline", "orchestrate", "run", "execute"],
            ),
            ToolType.DASHBOARD: EcosystemTool(
                name="Unified Dashboard",
                tool_type=ToolType.DASHBOARD,
                description="Mission Control for complete ecosystem",
                command="python amos_unified_dashboard.py",
                lines=350,
                keywords=["show", "view", "dashboard", "status", "overview", "display"],
            ),
            ToolType.AGENT: EcosystemTool(
                name="Autonomous Agent",
                tool_type=ToolType.AGENT,
                description="True agency - autonomously accomplishes goals",
                command="python amos_autonomous_agent.py",
                lines=560,
                keywords=["autonomous", "agent", "do", "accomplish", "auto", "self"],
            ),
            ToolType.SELF_DRIVING: EcosystemTool(
                name="Self-Driving Loop",
                tool_type=ToolType.SELF_DRIVING,
                description="Self-driving evolution without manual prompts",
                command="python amos_self_driving_loop.py",
                lines=520,
                keywords=["drive", "loop", "continuous", "evolve", "improve"],
            ),
            ToolType.META_COGNITIVE: EcosystemTool(
                name="Meta-Cognitive Reflector",
                tool_type=ToolType.META_COGNITIVE,
                description="Reflects on and improves decision-making",
                command="python amos_meta_cognitive_reflector.py",
                lines=520,
                keywords=["reflect", "meta", "analyze", "improve", "learn", "think"],
            ),
            ToolType.SHOWCASE: EcosystemTool(
                name="Ecosystem Showcase",
                tool_type=ToolType.SHOWCASE,
                description="Validates and demonstrates complete ecosystem",
                command="python amos_ecosystem_showcase.py",
                lines=450,
                keywords=["showcase", "validate", "demo", "demonstrate", "prove"],
            ),
            ToolType.CONTROLLER: EcosystemTool(
                name="Ecosystem Controller",
                tool_type=ToolType.CONTROLLER,
                description="This controller - unified interface (you are here)",
                command="python amos_ecosystem_controller.py",
                lines=350,
                keywords=["control", "route", "help", "guide", "interface"],
            ),
        }

    def show_welcome(self) -> None:
        """Show welcome message."""
        print("=" * 80)
        print("  🎛️  AMOS ECOSYSTEM CONTROLLER")
        print("  Unified Interface for Complete Cognitive System")
        print("=" * 80)
        print()
        print("  🧠 10 Tools | ~5,020 Lines | Complete Ecosystem")
        print()

    def show_menu(self) -> None:
        """Show tool menu."""
        print("  Available Tools:")
        print("  " + "─" * 76)

        for i, (tool_type, tool) in enumerate(self.tools.items(), 1):
            status = "🎯 YOU ARE HERE" if tool_type == ToolType.CONTROLLER else ""
            print(f"  {i}. {tool.name:<25} ({tool.lines} lines) {status}")
            print(f"     └─> {tool.description}")
            print(f"     └─> Keywords: {', '.join(tool.keywords[:4])}")
            print()

        print("  " + "=" * 76)

    def route_request(self, request: str) -> Optional[EcosystemTool]:
        """Route user request to appropriate tool.

        Uses keyword matching to determine best tool.
        """
        request_lower = request.lower()

        # Score each tool based on keyword matches
        scores: dict[ToolType, int] = {}

        for tool_type, tool in self.tools.items():
            if tool_type == ToolType.CONTROLLER:
                continue  # Don't route to self

            score = 0
            for keyword in tool.keywords:
                if keyword in request_lower:
                    score += 1
            scores[tool_type] = score

        # Find best match
        if scores:
            best_tool = max(scores.items(), key=lambda x: x[1])
            if best_tool[1] > 0:
                return self.tools[best_tool[0]]

        return None

    def execute_tool(self, tool: EcosystemTool, args: str = "") -> bool:
        """Execute a tool with arguments."""
        print(f"\n🚀 Routing to: {tool.name}")
        print(f"   {tool.description}")
        print()

        command = f"{tool.command} {args}".strip()

        try:
            # SECURITY: Use shlex.split() and shell=False to prevent injection
            import shlex

            cmd_parts = shlex.split(command)
            result = subprocess.run(
                cmd_parts,
                shell=False,
                capture_output=False,  # Show output to user
                text=True,
                timeout=120,
                cwd=str(self.root),
            )
            return result.returncode == 0
        except subprocess.TimeoutExpired:
            print("   ⚠️  Tool execution timed out")
            return False
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return False

    def run_interactive(self) -> None:
        """Run interactive mode."""
        self.show_welcome()
        self.show_menu()

        while True:
            print("\n" + "─" * 80)
            print("\n  Options:")
            print("    1-10 : Select tool by number")
            print("    text : Describe what you need (e.g., 'analyze decision')")
            print("    all  : Run complete ecosystem showcase")
            print("    menu : Show tool menu again")
            print("    help : Show help")
            print("    quit : Exit")

            user_input = input("\n  What do you need? ").strip()

            if user_input.lower() in ["quit", "exit", "q"]:
                print("\n  👋 Goodbye!")
                break

            elif user_input.lower() == "menu":
                self.show_menu()

            elif user_input.lower() == "help":
                self.show_help()

            elif user_input.lower() == "all":
                print("\n  🎬 Running complete ecosystem showcase...")
                self.execute_tool(self.tools[ToolType.SHOWCASE])

            elif user_input.isdigit():
                tool_num = int(user_input)
                if 1 <= tool_num <= len(self.tools):
                    tool = list(self.tools.values())[tool_num - 1]
                    if tool.tool_type == ToolType.CONTROLLER:
                        print("\n  ℹ️  You're already using the controller!")
                    else:
                        args = input(f"  Arguments for {tool.name} (or press Enter): ")
                        self.execute_tool(tool, args)
                else:
                    print("\n  ❌ Invalid tool number")

            else:
                # Try to route based on text
                tool = self.route_request(user_input)
                if tool:
                    self.execute_tool(tool, f'"{user_input}"')
                else:
                    print("\n  ❓ I didn't understand. Try:")
                    print("    • 'analyze decision' for brain demo")
                    print("    • 'search knowledge' for explorer")
                    print("    • 'build project' for generator")
                    print("    • Type 'menu' to see all options")

    def show_help(self) -> None:
        """Show help information."""
        print("\n" + "=" * 80)
        print("  📖 AMOS ECOSYSTEM CONTROLLER - HELP")
        print("=" * 80)
        print()
        print("  The ecosystem controller provides unified access to 10 AMOS tools.")
        print()
        print("  Usage:")
        print("    python amos_ecosystem_controller.py --interactive")
        print("    python amos_ecosystem_controller.py 'analyze this decision'")
        print("    python amos_ecosystem_controller.py --run-all")
        print()
        print("  Tool Mapping:")
        print("    • 'analyze', 'decision'     → Brain Live Demo")
        print("    • 'search', 'find'          → Knowledge Explorer")
        print("    • 'build', 'create'         → Project Generator")
        print("    • 'workflow', 'pipeline'    → Master Workflow")
        print("    • 'show', 'status'          → Unified Dashboard")
        print("    • 'autonomous', 'do'          → Autonomous Agent")
        print("    • 'drive', 'loop'           → Self-Driving Loop")
        print("    • 'reflect', 'meta'         → Meta-Cognitive Reflector")
        print("    • 'showcase', 'validate'    → Ecosystem Showcase")
        print()
        print("  The system will intelligently route your request to the")
        print("  most appropriate tool based on your input.")
        print()
        print("  " + "=" * 76)

    def run_quick(self, request: str) -> None:
        """Run a quick request."""
        self.show_welcome()

        tool = self.route_request(request)
        if tool:
            self.execute_tool(tool, f'"{request}"')
        else:
            print("  ❓ Couldn't determine best tool for: '{request}'")
            print("\n  Try:")
            print("    • 'analyze decision'")
            print("    • 'search knowledge'")
            print("    • 'build project'")
            print("\n  Or use --interactive for menu")

    def run_all(self) -> None:
        """Run complete ecosystem showcase."""
        self.show_welcome()
        print("  🎬 Running complete ecosystem showcase...\n")
        self.execute_tool(self.tools[ToolType.SHOWCASE])


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="AMOS Ecosystem Controller - Unified Interface")
    parser.add_argument("request", nargs="?", help="What you need (e.g., 'analyze decision')")
    parser.add_argument("--interactive", action="store_true", help="Interactive mode with menu")
    parser.add_argument("--run-all", action="store_true", help="Run complete ecosystem showcase")
    parser.add_argument("--help-tools", action="store_true", help="Show tool descriptions")

    args = parser.parse_args()

    controller = AMOSEcosystemController()

    if args.help_tools:
        controller.show_welcome()
        controller.show_menu()
    elif args.run_all:
        controller.run_all()
    elif args.interactive:
        controller.run_interactive()
    elif args.request:
        controller.run_quick(args.request)
    else:
        # Default to interactive
        controller.run_interactive()

    return 0


if __name__ == "__main__":
    sys.exit(main())
