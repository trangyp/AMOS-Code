#!/usr/bin/env python3
"""AMOS Unified Server Starter
============================

Architectural Decision: Start all AMOS services with proper orchestration.
Uses process management for concurrent server startup with health monitoring.

Owner: Trang
Version: 1.0.0
"""

import atexit
import signal
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

# Process registry
processes = []


def print_header(text):
    """Print formatted header."""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)


def check_service_health(url, timeout=2):
    """Check if a service is healthy."""
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status == 200
    except Exception:
        return False


def start_api_server():
    """Start the AMOS Enhanced API server."""
    print("\n[1] Starting AMOS Enhanced API Server...")
    print("    Port: 5000")

    proc = subprocess.Popen(
        [sys.executable, "amos_api_enhanced.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=str(Path(__file__).parent),
    )
    processes.append(("API Server", proc, "http://localhost:5000/health"))

    # Wait for server to start
    for i in range(10):
        time.sleep(1)
        if check_service_health("http://localhost:5000/health"):
            print("    ✓ API Server running at http://localhost:5000")
            return True
        print(f"    ⏳ Waiting... ({i + 1}/10)")

    print("    ⚠️ API Server may still be starting")
    return True


def start_websocket_server():
    """Start the WebSocket server."""
    print("\n[2] Starting WebSocket Server...")
    print("    Port: 8766")

    proc = subprocess.Popen(
        [sys.executable, "websocket_server.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=str(Path(__file__).parent),
    )
    processes.append(("WebSocket", proc, None))

    time.sleep(2)
    print("    ✓ WebSocket Server started")
    return True


def show_status():
    """Show current status of all services."""
    print("\n[STATUS] Service Health Check")
    print("-" * 50)

    for name, proc, health_url in processes:
        is_running = proc.poll() is None
        status = "🟢 Running" if is_running else "🔴 Stopped"

        if health_url and is_running:
            healthy = check_service_health(health_url)
            health_status = "✅ Healthy" if healthy else "⚠️ Not Responding"
        else:
            health_status = "N/A"

        print(f"  {name:20} {status:15} {health_status}")

    print("-" * 50)


def shutdown_all():
    """Gracefully shutdown all processes."""
    print("\n\n🛑 Shutting down AMOS servers...")

    for name, proc, _ in processes:
        if proc.poll() is None:
            print(f"  Stopping {name}...")
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()

    print("  ✓ All servers stopped")
    print("=" * 70)


def main():
    """Main entry point."""
    print_header("🧠 AMOS UNIFIED SERVER STARTER")

    # Register cleanup
    atexit.register(shutdown_all)
    signal.signal(signal.SIGINT, lambda s, f: sys.exit(0))
    signal.signal(signal.SIGTERM, lambda s, f: sys.exit(0))

    # Start services
    start_api_server()
    start_websocket_server()

    # Show endpoints
    print("\n[3] Available Endpoints:")
    print("    API Health:     http://localhost:5000/health")
    print("    API Ready:      http://localhost:5000/ready")
    print("    API Status:     http://localhost:5000/status")
    print(f"    Dashboard:      file://{Path(__file__).parent}/amos_dashboard.html")
    print("    WebSocket:      ws://localhost:8766")

    # Show status
    time.sleep(2)
    show_status()

    # Keep running
    print("\n" + "=" * 70)
    print("  ✨ AMOS IS RUNNING")
    print("=" * 70)
    print("\n  Press Ctrl+C to stop all servers")
    print("=" * 70 + "\n")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
