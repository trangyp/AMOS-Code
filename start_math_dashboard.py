#!/usr/bin/env python3
"""Convenience launcher for the AMOS Mathematical Framework Dashboard.

This script starts the math dashboard server with proper configuration
and environment setup. It handles port configuration, virtual environment
activation, and provides helpful startup messages.

Usage:
    python start_math_dashboard.py
    python start_math_dashboard.py --port 8081
    python start_math_dashboard.py --host 0.0.0.0 --port 8081
"""

import argparse
import os
import sys
from pathlib import Path


def get_project_root() -> Path:
    """Get the project root directory."""
    return Path(__file__).parent.resolve()


def setup_python_path():
    """Add necessary paths to Python path."""
    root = get_project_root()
    sys.path.insert(0, str(root))
    sys.path.insert(0, str(root / "clawspring"))
    sys.path.insert(0, str(root / "clawspring" / "amos_brain"))


def check_dependencies() -> bool:
    """Check if required dependencies are installed."""
    try:
        import fastapi
        import uvicorn

        print("✓ FastAPI and Uvicorn available")
        return True
    except ImportError as e:
        print(f"✗ Missing dependency: {e}")
        print("  Install with: pip install fastapi uvicorn")
        return False


def check_dashboard_files() -> bool:
    """Check if dashboard files exist."""
    root = get_project_root()
    server_path = root / "clawspring" / "amos_brain" / "math_dashboard_server.py"
    html_path = root / "clawspring" / "amos_brain" / "math_dashboard.html"

    checks = []

    if server_path.exists():
        print(f"✓ Dashboard server: {server_path}")
        checks.append(True)
    else:
        print(f"✗ Dashboard server not found: {server_path}")
        checks.append(False)

    if html_path.exists():
        size = html_path.stat().st_size
        print(f"✓ Dashboard HTML: {html_path} ({size} bytes)")
        checks.append(True)
    else:
        print(f"✗ Dashboard HTML not found: {html_path}")
        checks.append(False)

    return all(checks)


def start_dashboard(host: str, port: int, reload: bool = False):
    """Start the math dashboard server."""
    root = get_project_root()
    server_path = root / "clawspring" / "amos_brain" / "math_dashboard_server.py"

    print("\n" + "=" * 60)
    print("AMOS Mathematical Framework Dashboard")
    print("=" * 60)
    print(f"Host: {host}")
    print(f"Port: {port}")
    print(f"URL: http://{host}:{port}/")
    print("=" * 60 + "\n")

    # Set environment variables
    os.environ["MATH_DASHBOARD_HOST"] = host
    os.environ["MATH_DASHBOARD_PORT"] = str(port)

    # Change to the server directory for proper relative imports
    server_dir = server_path.parent

    # Use uvicorn to run the FastAPI app
    try:
        import uvicorn

        # Add the directory to path for the import
        sys.path.insert(0, str(server_dir))
        sys.path.insert(0, str(server_dir.parent))

        # Import and run
        import importlib.util

        spec = importlib.util.spec_from_file_location("math_dashboard_server", server_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Get the app and run with uvicorn
        app = module.app

        print("Starting server... (Press Ctrl+C to stop)\n")
        uvicorn.run(app, host=host, port=port, reload=reload, log_level="info")

    except KeyboardInterrupt:
        print("\n\nServer stopped by user.")
        return 0
    except Exception as e:
        print(f"\n✗ Error starting server: {e}")
        import traceback

        traceback.print_exc()
        return 1


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Start the AMOS Mathematical Framework Dashboard")
    parser.add_argument(
        "--host",
        default=os.getenv("MATH_DASHBOARD_HOST", "0.0.0.0"),
        help="Host to bind to (default: 0.0.0.0)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.getenv("MATH_DASHBOARD_PORT", "8081")),
        help="Port to bind to (default: 8081)",
    )
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload for development")
    parser.add_argument(
        "--check", action="store_true", help="Only check dependencies and files, don't start"
    )

    args = parser.parse_args()

    # Setup paths
    setup_python_path()

    print("Checking AMOS Mathematical Framework Dashboard...\n")

    # Check dependencies
    deps_ok = check_dependencies()

    # Check files
    files_ok = check_dashboard_files()

    if args.check:
        if deps_ok and files_ok:
            print("\n✓ All checks passed. Dashboard ready to start.")
            return 0
        else:
            print("\n✗ Some checks failed. Please fix issues above.")
            return 1

    if not deps_ok:
        print("\n✗ Cannot start: missing dependencies")
        return 1

    if not files_ok:
        print("\n✗ Cannot start: missing dashboard files")
        return 1

    # Start the dashboard
    return start_dashboard(args.host, args.port, args.reload)


if __name__ == "__main__":
    sys.exit(main())
