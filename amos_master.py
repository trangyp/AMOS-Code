#!/usr/bin/env python3
"""AMOS Master Orchestrator
Starts and coordinates all AMOS components.
"""

import subprocess
import sys
import time
import webbrowser
from pathlib import Path


def print_header(text):
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)


def start_api_server():
    """Start the AMOS API server."""
    print("\n[1] Starting AMOS API Server...")
    print("    Port: 8765")

    organism_dir = Path(__file__).parent / "AMOS_ORGANISM_OS"

    # Start server in background
    proc = subprocess.Popen(
        [sys.executable, "run.py", "api"],
        cwd=organism_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    # Wait for server to start
    time.sleep(3)

    # Check if running
    try:
        import urllib.request

        req = urllib.request.Request("http://localhost:8765/health")
        with urllib.request.urlopen(req, timeout=5) as resp:
            if resp.status == 200:
                print("    ✓ API Server running at http://localhost:8765")
                return proc
    except:
        pass

    print("    ⚠ Server starting (may take a moment)")
    return proc


def open_dashboard():
    """Open the web dashboard."""
    print("\n[2] Opening Dashboard...")
    dashboard_path = Path(__file__).parent / "AMOS_ORGANISM_OS" / "dashboard" / "index.html"

    if dashboard_path.exists():
        url = f"file://{dashboard_path.absolute()}"
        webbrowser.open(url)
        print(f"    ✓ Dashboard opened: {url}")
    else:
        print(f"    ✗ Dashboard not found at {dashboard_path}")


def show_endpoints():
    """Display available API endpoints."""
    print("\n[3] Available API Endpoints:")
    endpoints = [
        ("GET", "/health", "Health check"),
        ("GET", "/status", "System status"),
        ("POST", "/brain/think", "Cognitive processing"),
        ("POST", "/brain/plan", "Create plans"),
        ("POST", "/brain/analyze", "Systemic analysis"),
        ("GET", "/agents/list", "List agents"),
        ("POST", "/agents/execute", "Execute commands"),
    ]

    for method, path, desc in endpoints:
        print(f"    {method:6} http://localhost:8765{path:20} - {desc}")


def show_commands():
    """Display test commands."""
    print("\n[4] Quick Test Commands:")
    commands = [
        "curl http://localhost:8765/health",
        "curl http://localhost:8765/agents/list",
        'curl -X POST http://localhost:8765/brain/think -H "Content-Type: application/json" -d \'{"content":"Hello AMOS"}\'',
    ]

    for cmd in commands:
        print(f"    {cmd}")


def main():
    """Main orchestrator."""
    print_header("🧠 AMOS MASTER ORCHESTRATOR")

    # Start components
    server_proc = start_api_server()

    # Show info
    show_endpoints()
    show_commands()

    # Open dashboard
    open_dashboard()

    # Final message
    print("\n" + "=" * 60)
    print("  AMOS IS RUNNING")
    print("=" * 60)
    print("\n  API Server: http://localhost:8765")
    print("  Dashboard: file://.../dashboard/index.html")
    print("\n  Press Ctrl+C to stop")
    print("=" * 60)

    # Keep running
    try:
        if server_proc:
            server_proc.wait()
    except KeyboardInterrupt:
        print("\n\n  Shutting down AMOS...")
        if server_proc:
            server_proc.terminate()
        print("  ✓ Stopped")


if __name__ == "__main__":
    main()
