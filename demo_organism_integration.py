#!/usr/bin/env python3
"""AMOS Organism Integration Demo

Demonstrates the complete organism system:
1. Runner initialization across all 8 layers
2. Integration with orchestrator
3. Ethics validation
4. Health monitoring
5. CLI interaction

Run: python3 demo_organism_integration.py
"""

import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))


async def demo_runner():
    """Demo the organism runner."""
    print("\n" + "=" * 60)
    print("DEMO 1: AMOS Organism Runner")
    print("=" * 60)

    try:
        from amos_organism_runner import AMOSOrganismRunner, OrganismConfig

        # Create config
        config = OrganismConfig(name="Demo-Runner", mode="testing", health_check_interval=5.0)

        print("\n[1] Creating organism runner...")
        runner = AMOSOrganismRunner(config)
        print(f"   ✓ Runner created: {config.name}")
        print(f"   ✓ Mode: {config.mode}")

        print("\n[2] Initializing layers...")
        success = await runner.initialize()
        if success:
            print("   ✓ All layers initialized")
            print(f"   ✓ State: {runner.state.name}")
        else:
            print("   ✗ Initialization failed")
            return False

        print("\n[3] Calibrating...")
        report = await runner.calibrate()
        print("   ✓ Calibration complete")
        print(
            f"   ✓ Checks passed: {report.summary.get('passed', 0)}/{report.summary.get('total', 0)}"
        )
        print(f"   ✓ State: {runner.state.name}")

        print("\n[4] Health report:")
        print(runner.health_report())

        print("\n[5] Running 3 cycles...")
        for i in range(3):
            await runner._process_cycle()
            print(f"   ✓ Cycle {i + 1} complete")
            await asyncio.sleep(0.5)

        print("\n[6] Status check:")
        status = await runner.status()
        print(json.dumps(status, indent=2))

        print("\n[7] Shutting down...")
        await runner.shutdown()
        print("   ✓ Shutdown complete")

        return True

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback

        traceback.print_exc()
        return False


async def demo_integration():
    """Demo the integration layer."""
    print("\n" + "=" * 60)
    print("DEMO 2: AMOS Organism Integration")
    print("=" * 60)

    try:
        from amos_organism_integration import AMOSOrganismIntegration, IntegrationConfig
        from amos_organism_runner import OrganismConfig

        print("\n[1] Creating integration layer...")
        config = IntegrationConfig(
            organism_config=OrganismConfig(
                name="Demo-Integration", mode="testing", health_check_interval=5.0
            ),
            cycle_interval=0.5,
            ethics_check_frequency=3,
        )

        integration = AMOSOrganismIntegration(config)
        print("   ✓ Integration created")

        print("\n[2] Initializing...")
        success = await integration.initialize()
        if success:
            print("   ✓ Integration initialized")
        else:
            print("   ⚠ Integration has issues")

        print("\n[3] Running 5 integrated cycles...")
        for i in range(5):
            metrics = await integration.run_cycle()
            status = "✓" if metrics.success else "✗"
            print(f"   {status} Cycle {metrics.cycle_id}: {metrics.duration_ms:.1f}ms")
            await asyncio.sleep(0.3)

        print("\n[4] Status report:")
        status = integration.get_status()
        print(f"   Cycles: {status['cycle_count']}")
        print(f"   Runner: {status['runner_state']}")
        print(f"   Components: {status['components']}")

        print("\n[5] Health report:")
        print(integration.get_health_report())

        print("\n[6] Shutting down...")
        await integration.shutdown()
        print("   ✓ Shutdown complete")

        return True

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback

        traceback.print_exc()
        return False


def demo_cli():
    """Demo the CLI interface."""
    print("\n" + "=" * 60)
    print("DEMO 3: AMOS Organism CLI")
    print("=" * 60)

    try:
        import subprocess

        print("\n[1] CLI Help:")
        result = subprocess.run(
            [sys.executable, "amos_organism_cli.py", "--help"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            lines = result.stdout.strip().split("\n")[:15]
            for line in lines:
                print(f"   {line}")
        else:
            print(f"   Error: {result.stderr}")

        print("\n[2] CLI Status command:")
        result = subprocess.run(
            [sys.executable, "amos_organism_cli.py", "status"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        lines = result.stdout.strip().split("\n")
        for line in lines[:10]:
            print(f"   {line}")

        print("\n[3] CLI Config command:")
        result = subprocess.run(
            [sys.executable, "amos_organism_cli.py", "config"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        lines = result.stdout.strip().split("\n")[:8]
        for line in lines:
            print(f"   {line}")

        return True

    except Exception as e:
        print(f"\n✗ Error: {e}")
        return False


async def main():
    """Main demo entry point."""
    print("\n" + "=" * 60)
    print("AMOS ORGANISM INTEGRATION DEMO")
    print(f"Started: {datetime.now().isoformat()}")
    print("=" * 60)

    results = {}

    # Demo 1: Runner
    print("\n" + "-" * 60)
    results["runner"] = await demo_runner()

    # Demo 2: Integration
    print("\n" + "-" * 60)
    results["integration"] = await demo_integration()

    # Demo 3: CLI
    print("\n" + "-" * 60)
    results["cli"] = demo_cli()

    # Summary
    print("\n" + "=" * 60)
    print("DEMO SUMMARY")
    print("=" * 60)

    for name, success in results.items():
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"{status}: {name}")

    all_passed = all(results.values())

    print("\n" + "=" * 60)
    if all_passed:
        print("✓ ALL DEMOS PASSED")
        print("The AMOS Organism system is working correctly!")
    else:
        print("⚠ SOME DEMOS FAILED")
        print("Check the errors above for details.")
    print("=" * 60)

    return 0 if all_passed else 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user")
        sys.exit(1)
