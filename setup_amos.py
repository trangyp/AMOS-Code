#!/usr/bin/env python3
"""AMOS Setup Diagnostic & Fix Script

Checks environment and fixes common setup issues.
Run: python setup_amos.py
"""

import json
import os
import sys
from pathlib import Path


# Colors for output
class C:
    GREEN = "\033[32m"
    RED = "\033[31m"
    YELLOW = "\033[33m"
    CYAN = "\033[36m"
    RESET = "\033[0m"
    BOLD = "\033[1m"


def ok(msg):
    print(f"{C.GREEN}✓{C.RESET} {msg}")


def err(msg):
    print(f"{C.RED}✗{C.RESET} {msg}")


def warn(msg):
    print(f"{C.YELLOW}⚠{C.RESET} {msg}")


def info(msg):
    print(f"{C.CYAN}ℹ{C.RESET} {msg}")


def check_python_path():
    """Check if AMOS is in Python path."""
    print(f"\n{C.BOLD}Checking Python Path...{C.RESET}")

    amos_root = Path(__file__).parent.absolute()

    if str(amos_root) in sys.path:
        ok(f"AMOS root in sys.path: {amos_root}")
        return True
    else:
        warn("AMOS root NOT in sys.path")
        info(f"Adding {amos_root} to path...")
        sys.path.insert(0, str(amos_root))
        return True


def check_clawspring_path():
    """Check clawspring directory."""
    print(f"\n{C.BOLD}Checking ClawSpring Path...{C.RESET}")

    clawspring_path = Path(__file__).parent / "clawspring"

    if clawspring_path.exists():
        ok(f"clawspring directory exists: {clawspring_path}")
        if str(clawspring_path) not in sys.path:
            info("Adding clawspring to path...")
            sys.path.insert(0, str(clawspring_path))
        return True
    else:
        err(f"clawspring directory NOT found at {clawspring_path}")
        return False


def check_amos_brain():
    """Check if amos_brain can be imported."""
    print(f"\n{C.BOLD}Checking AMOS Brain Module...{C.RESET}")

    try:
        from amos_brain import get_amos_integration, get_brain

        ok("amos_brain module imports successfully")

        # Try to get integration
        try:
            amos = get_amos_integration()
            status = amos.get_status()
            if status.get("initialized"):
                ok(f"AMOS Brain initialized: {status.get('engines_count', 0)} engines")
            else:
                warn("AMOS Brain not initialized")
        except Exception as e:
            warn(f"AMOS Brain integration failed: {e}")

        return True
    except ImportError as e:
        err(f"Cannot import amos_brain: {e}")
        return False


def check_clawspring():
    """Check if clawspring can be imported."""
    print(f"\n{C.BOLD}Checking ClawSpring Module...{C.RESET}")

    try:
        from clawspring.clawspring import main as clawspring_main

        ok("clawspring module imports successfully")
        return True
    except ImportError as e:
        err(f"Cannot import clawspring: {e}")
        return False


def check_mcp_config():
    """Check MCP server configuration."""
    print(f"\n{C.BOLD}Checking MCP Configuration...{C.RESET}")

    user_mcp = Path.home() / ".clawspring" / "mcp.json"
    project_mcp = Path(__file__).parent / ".mcp.json"

    if user_mcp.exists():
        ok(f"User MCP config exists: {user_mcp}")
        try:
            with open(user_mcp) as f:
                config = json.load(f)
            servers = config.get("mcpServers", {})
            info(f"  Configured servers: {list(servers.keys())}")
        except Exception as e:
            err(f"Failed to parse user MCP config: {e}")
    else:
        warn(f"User MCP config not found: {user_mcp}")
        info("Creating default MCP config...")
        create_default_mcp_config(user_mcp)

    if project_mcp.exists():
        ok(f"Project MCP config exists: {project_mcp}")
    else:
        info(f"No project MCP config (optional): {project_mcp}")


def create_default_mcp_config(path: Path):
    """Create default MCP config file."""
    path.parent.mkdir(parents=True, exist_ok=True)

    amos_server_path = Path(__file__).parent / "amos_mcp_server.py"

    config = {
        "mcpServers": {
            "amos": {"type": "stdio", "command": "python3", "args": [str(amos_server_path)]}
        }
    }

    with open(path, "w") as f:
        json.dump(config, f, indent=2)

    ok(f"Created default MCP config: {path}")


def check_environment_vars():
    """Check environment variables."""
    print(f"\n{C.BOLD}Checking Environment Variables...{C.RESET}")

    important_vars = [
        "OPENAI_API_KEY",
        "ANTHROPIC_API_KEY",
        "GITHUB_TOKEN",
    ]

    for var in important_vars:
        if os.environ.get(var):
            ok(f"{var} is set")
        else:
            info(f"{var} not set (may be needed for some features)")


def check_agent_definition():
    """Check AMOS agent definition."""
    print(f"\n{C.BOLD}Checking Agent Definition...{C.RESET}")

    agent_path = Path(__file__).parent / ".clawspring" / "agents" / "amos.md"

    if agent_path.exists():
        ok(f"AMOS agent definition exists: {agent_path}")
    else:
        warn(f"AMOS agent definition not found: {agent_path}")
        info("Creating default agent definition...")
        create_default_agent(agent_path)


def create_default_agent(path: Path):
    """Create default agent definition."""
    path.parent.mkdir(parents=True, exist_ok=True)

    content = """---
description: "AMOS Brain-powered agent with cognitive architecture, global laws, and reasoning engines"
model: ""
tools: [Read, Write, Edit, Bash, Glob, Grep, AMOSReasoning, AMOSLaws, AMOSEngines, AMOSStatus, AMOSEnhancePrompt]
---

You are an AMOS Brain-powered cognitive agent...
"""

    with open(path, "w") as f:
        f.write(content)

    ok(f"Created default agent: {path}")


def run_test_import():
    """Test basic AMOS functionality."""
    print(f"\n{C.BOLD}Testing AMOS Functionality...{C.RESET}")

    try:
        from amos_brain import get_amos_integration

        amos = get_amos_integration()
        status = amos.get_status()

        if status.get("initialized"):
            ok("AMOS Brain is ready to use!")
            print(f"\n  Engines: {status.get('engines_count', 0)}")
            print(f"  Laws: {len(status.get('laws_active', []))}")
            print(f"  Domains: {len(status.get('domains_covered', []))}")
        else:
            err("AMOS Brain failed to initialize")
    except Exception as e:
        err(f"Test failed: {e}")


def print_next_steps():
    """Print next steps."""
    print(f"\n{C.BOLD}{C.CYAN}═══════════════════════════════════════════════════════{C.RESET}")
    print(f"{C.BOLD}{C.CYAN}  Setup Complete! Next Steps:{C.RESET}")
    print(f"{C.BOLD}{C.CYAN}═══════════════════════════════════════════════════════{C.RESET}")
    print()
    print("  To run AMOS-powered ClawSpring:")
    print(f"    {C.GREEN}python amos.py{C.RESET}")
    print()
    print("  To run AMOS Brain Launcher (menu):")
    print(f"    {C.GREEN}python amos_brain_launcher.py{C.RESET}")
    print()
    print("  To run AMOS Organism API server:")
    print(f"    {C.GREEN}cd AMOS_ORGANISM_OS && python run.py api{C.RESET}")
    print()
    print("  To run Organism CLI:")
    print(f"    {C.GREEN}cd AMOS_ORGANISM_OS && python run.py cli{C.RESET}")
    print()
    print("  To check brain status only:")
    print(
        f"    {C.GREEN}python -c 'from amos_brain import get_amos_integration; print(get_amos_integration().get_status())'{C.RESET}"
    )
    print()


def main():
    """Run all checks."""
    print(f"{C.BOLD}{C.CYAN}╔═══════════════════════════════════════════════════════╗{C.RESET}")
    print(f"{C.BOLD}{C.CYAN}║     AMOS Brain Setup Diagnostic & Fix Tool            ║{C.RESET}")
    print(f"{C.BOLD}{C.CYAN}╚═══════════════════════════════════════════════════════╝{C.RESET}")

    check_python_path()
    check_clawspring_path()
    check_amos_brain()
    check_clawspring()
    check_mcp_config()
    check_environment_vars()
    check_agent_definition()
    run_test_import()

    print_next_steps()

    return 0


if __name__ == "__main__":
    sys.exit(main())
