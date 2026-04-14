#!/usr/bin/env python3
"""
AMOS Organism CLI Commands

Command-line interface for organism control:
- status: Show organism health and state
- start: Initialize and run organism
- stop: Graceful shutdown
- restart: Stop then start
- config: Show/edit configuration
- logs: View organism logs
"""

import argparse
import asyncio
import json
import sys
import time
from pathlib import Path
from typing import Optional

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))

# Import organism components
try:
    from amos_organism_runner import (
        AMOSOrganismRunner,
        OrganismConfig
    )
    RUNNER_AVAILABLE = True
except ImportError:
    RUNNER_AVAILABLE = False

try:
    from amos_organism_integration import demo
    INTEGRATION_AVAILABLE = True
except ImportError:
    INTEGRATION_AVAILABLE = False


ORGANISM_ROOT = Path(__file__).parent
STATE_FILE = ORGANISM_ROOT / ".amos_organism_state.json"


def save_state(state: dict) -> None:
    """Save organism state to file."""
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)


def load_state() -> dict:
    """Load organism state from file."""
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            return json.load(f)
    return {"running": False, "pid": None, "start_time": None}


def cmd_status(args) -> int:
    """Show organism status."""
    print("AMOS Organism Status")
    print("=" * 50)
    
    state = load_state()
    print(f"Running: {'Yes' if state.get('running') else 'No'}")
    print(f"PID: {state.get('pid', 'N/A')}")
    print(f"Started: {state.get('start_time', 'N/A')}")
    
    if RUNNER_AVAILABLE:
        print("\nRunner: Available")
        # Could instantiate and check health here
    else:
        print("\nRunner: Not available")
    
    if INTEGRATION_AVAILABLE:
        print("Integration: Available")
    else:
        print("Integration: Not available")
    
    # Check for state files
    root = ORGANISM_ROOT
    health_file = root / "amos_health.json"
    if health_file.exists():
        try:
            with open(health_file) as f:
                health = json.load(f)
            print(f"\nLast Health Check:")
            print(f"  State: {health.get('state', 'unknown')}")
            print(f"  Coherence: {health.get('coherence_score', 0):.2f}")
            print(f"  Axioms: {health.get('axiom_compliance', 0):.2f}")
        except Exception:
            pass
    
    return 0


def cmd_start(args) -> int:
    """Start the organism."""
    state = load_state()
    if state.get("running"):
        print("Organism is already running!")
        return 1
    
    print("Starting AMOS Organism...")
    
    if not RUNNER_AVAILABLE:
        print("Error: Organism runner not available")
        return 1
    
    # Build config
    config = OrganismConfig(
        name=args.name or "AMOS-Organism",
        mode=args.mode,
        health_check_interval=args.health_interval
    )
    
    # Save state
    save_state({
        "running": True,
        "pid": None,  # Would set if daemonized
        "start_time": time.time(),
        "config": {
            "name": config.name,
            "mode": config.mode
        }
    })
    
    # Run (blocking for now)
    try:
        asyncio.run(_run_organism(config, args.duration))
    except KeyboardInterrupt:
        print("\nReceived interrupt, shutting down...")
    finally:
        save_state({"running": False, "pid": None, "start_time": None})
    
    return 0


async def _run_organism(config: OrganismConfig, duration: Optional[float]) -> None:
    """Run organism async."""
    runner = AMOSOrganismRunner(config)
    
    # Initialize
    print("  → Initializing...")
    if not await runner.initialize():
        print("✗ Initialization failed")
        return
    
    # Calibrate
    print("  → Calibrating...")
    report = await runner.calibrate()
    if not report.is_valid():
        print("⚠ Calibration has issues, continuing in degraded mode")
    
    # Print health
    print("\n" + runner.health_report())
    
    separator = "=" * 50
    print(separator)
    print("Organism running (Ctrl+C to stop)")
    print(f"{'=' * 50}\n")
    
    if duration:
        print(f"Will run for {duration} seconds...")
        await runner.run()
        await asyncio.sleep(duration)
        await runner.shutdown()
    else:
        await runner.run()


def cmd_stop(args) -> int:
    """Stop the organism."""
    state = load_state()
    if not state.get("running"):
        print("Organism is not running")
        return 0
    
    print("Stopping AMOS Organism...")
    
    # For now, just update state file
    # In daemon mode, would send signal to process
    save_state({"running": False, "pid": None, "start_time": None})
    
    print("Organism stopped")
    return 0


def cmd_restart(args) -> int:
    """Restart the organism."""
    print("Restarting AMOS Organism...")
    
    # Stop if running
    cmd_stop(args)
    
    # Small delay
    time.sleep(1)
    
    # Start
    return cmd_start(args)


def cmd_config(args) -> int:
    """Show or edit configuration."""
    config_file = ORGANISM_ROOT / "amos_organism_config.json"
    
    if args.set:
        # Set a config value
        key, value = args.set.split("=", 1)
        try:
            # Try to parse as JSON
            parsed = json.loads(value)
        except json.JSONDecodeError:
            parsed = value
        
        config = {}
        if config_file.exists():
            with open(config_file) as f:
                config = json.load(f)
        
        config[key] = parsed
        
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"Set {key} = {parsed}")
        return 0
    
    # Show config
    if config_file.exists():
        with open(config_file) as f:
            config = json.load(f)
        print("Current Configuration:")
        print(json.dumps(config, indent=2))
    else:
        print("No configuration file found")
        print("Using defaults:")
        default = OrganismConfig()
        print(json.dumps({
            "name": default.name,
            "mode": default.mode,
            "health_check_interval": default.health_check_interval,
            "max_memory_mb": default.max_memory_mb,
            "log_level": default.log_level
        }, indent=2))
    
    return 0


def cmd_health(args) -> int:
    """Show detailed health report."""
    health_file = ORGANISM_ROOT / "amos_health.json"
    
    if not health_file.exists():
        print("No health data available")
        print("Start the organism to generate health data")
        return 1
    
    try:
        with open(health_file) as f:
            health = json.load(f)
        
        print("AMOS Organism Health Report")
        print("=" * 50)
        print(json.dumps(health, indent=2))
        
    except Exception as e:
        print(f"Error reading health data: {e}")
        return 1
    
    return 0


def cmd_demo(args) -> int:
    """Run organism demo."""
    if not INTEGRATION_AVAILABLE:
        print("Integration module not available")
        return 1
    
    print("Running AMOS Organism Demo...")
    print("This will run for 10 seconds\n")
    
    from amos_organism_integration import demo
    
    try:
        return asyncio.run(demo())
    except KeyboardInterrupt:
        print("\nDemo interrupted")
        return 0


def main() -> int:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="AMOS Organism CLI",
        prog="amos-organism"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Status command
    status_parser = subparsers.add_parser(
        "status", help="Show organism status"
    )
    status_parser.set_defaults(func=cmd_status)
    
    # Start command
    start_parser = subparsers.add_parser(
        "start", help="Start the organism"
    )
    start_parser.add_argument(
        "--name", type=str, help="Organism name"
    )
    start_parser.add_argument(
        "--mode", default="development",
        choices=["development", "testing", "production"],
        help="Run mode"
    )
    start_parser.add_argument(
        "--duration", type=float, default=None,
        help="Run for N seconds (default: indefinite)"
    )
    start_parser.add_argument(
        "--health-interval", type=float, default=30.0,
        help="Health check interval in seconds"
    )
    start_parser.set_defaults(func=cmd_start)
    
    # Stop command
    stop_parser = subparsers.add_parser(
        "stop", help="Stop the organism"
    )
    stop_parser.set_defaults(func=cmd_stop)
    
    # Restart command
    restart_parser = subparsers.add_parser(
        "restart", help="Restart the organism"
    )
    restart_parser.add_argument(
        "--name", type=str, help="Organism name"
    )
    restart_parser.add_argument(
        "--mode", default="development",
        choices=["development", "testing", "production"]
    )
    restart_parser.set_defaults(func=cmd_restart)
    
    # Config command
    config_parser = subparsers.add_parser(
        "config", help="Show or edit configuration"
    )
    config_parser.add_argument(
        "--set", type=str,
        help="Set config value (key=value)"
    )
    config_parser.set_defaults(func=cmd_config)
    
    # Health command
    health_parser = subparsers.add_parser(
        "health", help="Show health report"
    )
    health_parser.set_defaults(func=cmd_health)
    
    # Demo command
    demo_parser = subparsers.add_parser(
        "demo", help="Run organism demo"
    )
    demo_parser.set_defaults(func=cmd_demo)
    
    # Parse args
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 0
    
    # Run command
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
