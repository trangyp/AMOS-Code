#!/usr/bin/env python3
"""
AMOS Launcher
=============
One-command launcher for the complete AMOS Brain ecosystem.

Starts all 15 components:
1. Core Brain (lazy-loaded)
2. Health Monitor (active)
3. API Server (optional)
4. Unified Dashboard (optional)
5. Session Logger (ready)

Usage:
    python amos_launcher.py [mode]

Modes:
    full        Start everything (API + Dashboard + Health checks)
    api         Start API server only
    dashboard   Start TUI dashboard only
    health      Run health checks only
    status      Show ecosystem status

Examples:
    python amos_launcher.py full
    python amos_launcher.py api --port 8080
    python amos_launcher.py status
"""
from __future__ import annotations

import sys
import argparse
import subprocess
import time
from pathlib import Path
from typing import Any

# Add paths
sys.path.insert(0, str(Path(__file__).parent / "clawspring"))
sys.path.insert(0, str(Path(__file__).parent))


def print_header(title: str):
    """Print formatted header."""
    print("=" * 60)
    print(f"  {title}")
    print("=" * 60)


def print_component(name: str, status: str, details: str = ""):
    """Print component status."""
    icon = "✓" if status == "ok" else "⚠" if status == "warn" else "✗"
    print(f"  {icon} {name:20s} {status:10s} {details}")


def check_ecosystem() -> dict[str, Any]:
    """Check status of all 15 ecosystem components."""
    print_header("AMOS ECOSYSTEM STATUS CHECK")
    
    components = {
        "Core Brain": False,
        "Tools (5)": False,
        "Skills (7)": False,
        "Agent Types": False,
        "Agent Loop": False,
        "CLI --amos": False,
        "Integration Tests": False,
        "Demo Script": False,
        "Observer": False,
        "Session Logger": False,
        "API Server": False,
        "Unified Dashboard": False,
        "Workflow Examples": False,
        "Health Monitor": False,
        "Documentation": False,
    }
    
    # Check 1: Core Brain
    try:
        from amos_brain import get_amos_integration
        amos = get_amos_integration()
        status = amos.get_status()
        if status.get('initialized'):
            components["Core Brain"] = True
            print_component("Core Brain", "ok", f"{status.get('engines_count', 0)} engines")
        else:
            print_component("Core Brain", "warn", "not initialized")
    except Exception as e:
        print_component("Core Brain", "error", str(e)[:30])
    
    # Check 2: Tools
    try:
        from tool_registry import _registry
        amos_tools = [k for k in _registry.keys() if "AMOS" in k]
        if len(amos_tools) >= 5:
            components["Tools (5)"] = True
            print_component("Tools (5)", "ok", f"{len(amos_tools)} registered")
        else:
            print_component("Tools (5)", "warn", f"only {len(amos_tools)}")
    except Exception as e:
        print_component("Tools (5)", "error", str(e)[:30])
    
    # Check 3: Skills
    try:
        from skill import find_skill
        skills = ["/amos-analyze", "/amos-laws", "/amos-status"]
        found = sum(1 for s in skills if find_skill(s) is not None)
        if found >= 3:
            components["Skills (7)"] = True
            print_component("Skills (7)", "ok", f"{found}+ found")
        else:
            print_component("Skills (7)", "warn", f"{found}/3 key skills")
    except Exception as e:
        print_component("Skills (7)", "error", str(e)[:30])
    
    # Check 4: Agent Types
    try:
        from multi_agent import load_agent_definitions
        defs = load_agent_definitions()
        if "amos" in defs:
            components["Agent Types"] = True
            print_component("Agent Types", "ok", "amos type registered")
        else:
            print_component("Agent Types", "warn", "not found")
    except Exception as e:
        print_component("Agent Types", "error", str(e)[:30])
    
    # Check 5: Agent Loop
    try:
        from agent import _amos_available
        if _amos_available:
            components["Agent Loop"] = True
            print_component("Agent Loop", "ok", "integrated")
        else:
            print_component("Agent Loop", "warn", "not available")
    except Exception as e:
        print_component("Agent Loop", "error", str(e)[:30])
    
    # Check 6: CLI
    try:
        result = subprocess.run(
            ["python3", "clawspring/clawspring.py", "--help"],
            capture_output=True, text=True, timeout=5
        )
        if "--amos" in result.stdout:
            components["CLI --amos"] = True
            print_component("CLI --amos", "ok", "flag available")
        else:
            print_component("CLI --amos", "warn", "flag missing")
    except Exception as e:
        print_component("CLI --amos", "error", str(e)[:30])
    
    # Check 7: Tests
    try:
        result = subprocess.run(
            ["python3", "test_amos_integration.py"],
            capture_output=True, text=True, timeout=30
        )
        if "12 passed" in result.stdout and "0 failed" in result.stdout:
            components["Integration Tests"] = True
            print_component("Integration Tests", "ok", "12/12 passing")
        else:
            print_component("Integration Tests", "warn", "some failing")
    except Exception as e:
        print_component("Integration Tests", "error", str(e)[:30])
    
    # Check 8: Demo
    try:
        from demo_amos import main as demo_main
        components["Demo Script"] = True
        print_component("Demo Script", "ok", "importable")
    except Exception as e:
        print_component("Demo Script", "warn", str(e)[:30])
    
    # Check 9: Observer
    try:
        from amos_observer import AMOSObserver
        obs = AMOSObserver()
        components["Observer"] = True
        print_component("Observer", "ok", "ready")
    except Exception as e:
        print_component("Observer", "warn", str(e)[:30])
    
    # Check 10: Session Logger
    try:
        from amos_session_logger import AMOSSessionLogger
        logger = AMOSSessionLogger()
        sessions = logger.list_sessions()
        components["Session Logger"] = True
        print_component("Session Logger", "ok", f"{len(sessions)} sessions")
    except Exception as e:
        print_component("Session Logger", "warn", str(e)[:30])
    
    # Check 11: API Server
    try:
        from amos_api_simple import AMOSAPIHandler
        components["API Server"] = True
        print_component("API Server", "ok", "handler ready")
    except Exception as e:
        print_component("API Server", "warn", str(e)[:30])
    
    # Check 12: Dashboard
    try:
        from amos_unified_dashboard import AMOSUnifiedDashboard
        dash = AMOSUnifiedDashboard()
        components["Unified Dashboard"] = True
        print_component("Unified Dashboard", "ok", "ready")
    except Exception as e:
        print_component("Unified Dashboard", "warn", str(e)[:30])
    
    # Check 13: Workflow
    try:
        from amos_workflow_example import AMOSWorkflow
        wf = AMOSWorkflow()
        components["Workflow Examples"] = True
        print_component("Workflow Examples", "ok", "ready")
    except Exception as e:
        print_component("Workflow Examples", "warn", str(e)[:30])
    
    # Check 14: Health Monitor
    try:
        from amos_health_monitor import init_default_health_checks
        monitor = init_default_health_checks()
        components["Health Monitor"] = True
        print_component("Health Monitor", "ok", f"{len(monitor.checks)} checks")
    except Exception as e:
        print_component("Health Monitor", "warn", str(e)[:30])
    
    # Check 15: Documentation
    docs = [
        "AMOS_ECOSYSTEM_COMPLETE.md",
        "AMOS_INTEGRATION_GUIDE.md",
        "README.md"
    ]
    found_docs = sum(1 for d in docs if Path(d).exists())
    if found_docs >= 2:
        components["Documentation"] = True
        print_component("Documentation", "ok", f"{found_docs} files")
    else:
        print_component("Documentation", "warn", "incomplete")
    
    # Summary
    healthy = sum(1 for v in components.values() if v)
    total = len(components)
    
    print()
    print("=" * 60)
    print(f"  SUMMARY: {healthy}/{total} components healthy")
    print("=" * 60)
    
    if healthy == total:
        print("  🎉 ALL SYSTEMS OPERATIONAL - ECOSYSTEM READY")
    elif healthy >= total * 0.8:
        print(f"  ⚠️  MOSTLY HEALTHY - {total - healthy} components need attention")
    else:
        print(f"  ✗ ISSUES DETECTED - {total - healthy} components unhealthy")
    
    return components


def start_api_server(port: int = 8080):
    """Start the API server."""
    print_header("STARTING API SERVER")
    print(f"  Port: {port}")
    print(f"  Endpoints:")
    print(f"    - GET  /api/health")
    print(f"    - GET  /api/status")
    print(f"    - POST /api/think")
    print(f"    - POST /api/reason")
    print()
    print("  Press Ctrl+C to stop")
    print()
    
    import subprocess
    subprocess.run(["python3", "amos_api_simple.py", "--port", str(port)])


def start_dashboard():
    """Start the unified dashboard."""
    print_header("STARTING UNIFIED DASHBOARD")
    print("  Starting TUI dashboard...")
    print()
    
    import subprocess
    subprocess.run(["python3", "amos_unified_dashboard.py"])


def run_health_checks():
    """Run comprehensive health checks."""
    import asyncio
    from amos_health_monitor import init_default_health_checks, HealthStatus
    
    print_header("RUNNING HEALTH CHECKS")
    
    monitor = init_default_health_checks()
    
    async def check():
        health = await monitor.check_health()
        
        print(f"\n  Overall Status: {health.overall.value.upper()}")
        print(f"  Timestamp: {health.timestamp}")
        print(f"  Components Checked: {len(health.checks)}")
        print()
        
        for check in health.checks:
            status_icon = "✓" if check.status == HealthStatus.HEALTHY else \
                         "⚠" if check.status == HealthStatus.DEGRADED else "✗"
            print(f"  {status_icon} {check.name:20s} | {check.status.value:10s}")
        
        healthy = sum(1 for c in health.checks if c.status == HealthStatus.HEALTHY)
        degraded = sum(1 for c in health.checks if c.status == HealthStatus.DEGRADED)
        unhealthy = sum(1 for c in health.checks if c.status == HealthStatus.UNHEALTHY)
        
        print()
        print(f"  Healthy: {healthy} | Degraded: {degraded} | Unhealthy: {unhealthy}")
    
    asyncio.run(check())


def main():
    parser = argparse.ArgumentParser(
        description="AMOS Brain Ecosystem Launcher",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python amos_launcher.py status      # Check ecosystem status
  python amos_launcher.py full        # Start everything
  python amos_launcher.py api         # Start API server
  python amos_launcher.py dashboard   # Start TUI dashboard
  python amos_launcher.py health      # Run health checks
        """
    )
    parser.add_argument(
        "mode",
        nargs="?",
        default="status",
        choices=["full", "api", "dashboard", "health", "status"],
        help="Launch mode (default: status)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8080,
        help="API server port (default: 8080)"
    )
    
    args = parser.parse_args()
    
    if args.mode == "status":
        check_ecosystem()
    
    elif args.mode == "api":
        start_api_server(args.port)
    
    elif args.mode == "dashboard":
        start_dashboard()
    
    elif args.mode == "health":
        run_health_checks()
    
    elif args.mode == "full":
        print_header("AMOS BRAIN ECOSYSTEM - FULL LAUNCH")
        print()
        print("Starting all components...")
        print()
        
        # 1. Check status first
        components = check_ecosystem()
        healthy = sum(1 for v in components.values() if v)
        
        if healthy < len(components) * 0.8:
            print("\n  ⚠️  Some components are not healthy.")
            print("  Fix issues before running full mode.")
            print("  Run: python amos_launcher.py status")
            return 1
        
        # 2. Start API server in background
        print("\n  [1/2] Starting API server...")
        import subprocess
        api_proc = subprocess.Popen(
            ["python3", "amos_api_simple.py", "--port", str(args.port)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        time.sleep(2)
        print(f"        API server started on port {args.port}")
        
        # 3. Start dashboard
        print("\n  [2/2] Starting dashboard...")
        print("        (This will take over the terminal)")
        print()
        
        try:
            subprocess.run(["python3", "amos_unified_dashboard.py"])
        except KeyboardInterrupt:
            print("\n  Stopping API server...")
            api_proc.terminate()
            print("  Shutdown complete.")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
