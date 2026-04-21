#!/usr/bin/env python3
"""AMOS Main Entry Point - Unified interface to all AMOS capabilities.

Usage:
    python amos_main.py status          # Show system status
    python amos_main.py bootstrap       # Initialize system
    python amos_main.py test             # Run tests
    python amos_main.py repair           # Fix codebase issues
    python amos_main.py serve            # Start API server
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path


async def cmd_status() -> int:
    """Show AMOS system status."""
    print("AMOS System Status")
    print("=" * 60)
    
    # Check core components
    components = [
        ("amos_kernel", "Kernel"),
        ("amos_brain", "Brain"),
        ("amos_circuit_breaker", "Circuit Breaker"),
        ("amos_workflow_engine_v2", "Workflow Engine"),
        ("amos_async_task_processor", "Task Processor"),
        ("amos_api_health_router", "Health Router"),
        ("amos_master_integration", "Master Integration"),
    ]
    
    available = 0
    for module, name in components:
        try:
            __import__(module)
            print(f"  ✓ {name}")
            available += 1
        except ImportError as e:
            print(f"  ✗ {name}: {e}")
    
    print("=" * 60)
    print(f"Components: {available}/{len(components)} available")
    return 0 if available > 0 else 1


async def cmd_bootstrap() -> int:
    """Initialize AMOS system."""
    try:
        from amos_system_bootstrap import AMOSSystemBootstrap, BootstrapConfig
        
        config = BootstrapConfig(root_path=Path.cwd())
        bootstrap = AMOSSystemBootstrap(config)
        result = await bootstrap.bootstrap()
        
        return 0 if result["status"] in ["healthy", "degraded"] else 1
    except ImportError as e:
        print(f"Bootstrap not available: {e}")
        return 1


async def cmd_test() -> int:
    """Run comprehensive tests."""
    try:
        from amos_comprehensive_test import AMOSComprehensiveTest
        
        test = AMOSComprehensiveTest()
        report = await test.run_all_tests()
        return 0 if report["overall"] == "PASS" else 1
    except ImportError as e:
        print(f"Test suite not available: {e}")
        return 1


async def cmd_repair() -> int:
    """Fix codebase issues."""
    try:
        from amos_auto_repair import AMOSAutoRepair
        
        repair = AMOSAutoRepair()
        results = repair.repair_all()
        
        print(f"Fixed {len(results['files_modified'])} files")
        return 0
    except ImportError as e:
        print(f"Auto repair not available: {e}")
        return 1


async def cmd_serve() -> int:
    """Start API server."""
    try:
        import uvicorn
        from amos_api_server import app
        
        print("Starting AMOS API server...")
        uvicorn.run(app, host="0.0.0.0", port=8000)
        return 0
    except ImportError as e:
        print(f"API server not available: {e}")
        print("Run: pip install fastapi uvicorn")
        return 1


async def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="AMOS Main")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Status command
    subparsers.add_parser("status", help="Show system status")
    
    # Bootstrap command
    subparsers.add_parser("bootstrap", help="Initialize system")
    
    # Test command
    subparsers.add_parser("test", help="Run tests")
    
    # Repair command
    subparsers.add_parser("repair", help="Fix codebase issues")
    
    # Serve command
    subparsers.add_parser("serve", help="Start API server")
    
    args = parser.parse_args()
    
    if args.command == "status":
        return await cmd_status()
    elif args.command == "bootstrap":
        return await cmd_bootstrap()
    elif args.command == "test":
        return await cmd_test()
    elif args.command == "repair":
        return await cmd_repair()
    elif args.command == "serve":
        return await cmd_serve()
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
