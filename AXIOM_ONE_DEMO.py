#!/usr/bin/env python3
"""Axiom One Civilization Substrate - Working Demo.

Demonstrates the three new core capabilities:
1. Agent Fabric Kernel (Layer 10) - Bounded AI labor
2. Repo Autopsy Engine (Section 10) - Automatic debugging
3. Simulation Engine (Layer 12) - Pre-runtime prediction
"""

import asyncio
import json
from datetime import datetime, timezone
UTC = timezone.utc

UTC = UTC


def demo_agent_fabric() -> dict:
    """Demonstrate Agent Fabric Kernel."""
    print("\n" + "=" * 60)
    print("DEMO 1: Agent Fabric Kernel - Bounded AI Labor")
    print("=" * 60)

    from amos_brain.agent_fabric_kernel import (
        AgentTask,
        get_agent_fabric_kernel,
    )

    # Get the kernel
    kernel = get_agent_fabric_kernel()

    # Register an agent
    print("\n[1] Registering agent 'repo-debugger'...")
    agent = kernel.register_agent("repo-debugger", authorized_by="demo_user")
    print(f"   Agent ID: {agent.id}")
    print(f"   Class: {agent.class_id}")
    print(f"   Budget: ${agent.budget.max_usd} max")
    print(f"   Permissions: {agent.permissions.tools}")

    # Spawn a run
    print("\n[2] Spawning agent run...")
    task = AgentTask(
        objective="Analyze repository for missing imports",
        tools=["file_read", "grep_search"],
    )
    run = kernel.spawn_run(agent.id, task, context={"repo_path": "."})
    print(f"   Run ID: {run.id}")
    print(f"   Phase: {run.phase}")
    print(f"   Budget remaining: ${run.budget.remaining():.4f}")

    # Simulate execution
    print("\n[3] Simulating agent execution...")

    # Record some actions
    action1 = run.record_action("read_file", {"file": "test.py"}, cost_usd=0.001)
    print(f"   Action 1: {action1['type']} (cost: ${action1['cost_usd']})")

    action2 = run.record_action("grep_search", {"pattern": "import"}, cost_usd=0.002)
    print(f"   Action 2: {action2['type']} (cost: ${action2['cost_usd']})")

    print(f"   Total spent: ${run.budget.current_spend:.4f}")
    print(f"   Remaining: ${run.budget.remaining():.4f}")

    # Generate receipt
    print("\n[4] Generating immutable receipt...")
    receipt = run.generate_receipt()
    print(f"   Receipt ID: {receipt.receipt_id}")
    print(f"   Actions: {len(receipt.actions)}")
    print(f"   Total cost: ${receipt.total_cost_usd:.4f}")
    print(f"   Hash: {receipt.receipt_hash[:16]}...")

    # Verify receipt
    is_valid = receipt.verify()
    print(f"   Verification: {'PASS' if is_valid else 'FAIL'}")

    return {
        "agent_id": agent.id,
        "run_id": run.id,
        "receipt_id": receipt.receipt_id,
        "actions_count": len(receipt.actions),
        "total_cost": receipt.total_cost_usd,
        "verified": is_valid,
    }


def demo_repo_autopsy() -> dict:
    """Demonstrate Repo Autopsy Engine."""
    print("\n" + "=" * 60)
    print("DEMO 2: Repo Autopsy Engine - Automatic Debugging")
    print("=" * 60)

    from amos_brain.repo_autopsy_engine import (
        AutopsyRequest,
        AutopsyRequestType,
        get_repo_autopsy_engine,
    )

    # Create engine
    engine = get_repo_autopsy_engine()

    # Create request
    print("\n[1] Creating autopsy request...")
    request = AutopsyRequest(
        type=AutopsyRequestType.BUILD_FAILURE,
        repo_path=".",
        trigger_source="demo",
        priority="p1",
    )
    print(f"   Request ID: {request.id}")
    print(f"   Type: {request.type.value}")
    print(f"   Priority: {request.priority}")

    # Start autopsy (async)
    print("\n[2] Starting autopsy session...")
    session = asyncio.get_event_loop().run_until_complete(engine.start_autopsy(request))
    print(f"   Session ID: {session.request.id}")
    print(f"   Phase: {session.phase.value}")

    # Wait a bit for processing
    import time

    time.sleep(1)

    # Check results
    print("\n[3] Autopsy results...")
    print(f"   Evidence collected: {len(session.collected_evidence)}")
    print(f"   Patterns identified: {len(session.identified_patterns)}")
    print(f"   Fault locations: {len(session.fault_locations)}")

    if session.report:
        print("\n[4] Report generated!")
        report = session.report
        print(f"   Patterns found: {len(report.patterns_found)}")
        print(f"   Proposed fixes: {len(report.proposed_fixes)}")
        print(f"   Requires review: {report.requires_human_review}")
        print(f"   Est. repair time: {report.estimated_repair_time} min")

        # Show markdown summary
        print("\n[5] Report excerpt:")
        lines = report.to_markdown().split("\n")[:10]
        for line in lines:
            print(f"   {line}")
        print("   ...")

    return {
        "session_id": session.request.id,
        "evidence_count": len(session.collected_evidence),
        "patterns_count": len(session.identified_patterns),
        "fault_count": len(session.fault_locations),
        "report_generated": session.report is not None,
    }


def demo_simulation() -> dict:
    """Demonstrate Simulation Engine."""
    print("\n" + "=" * 60)
    print("DEMO 3: Simulation Engine - Pre-Runtime Prediction")
    print("=" * 60)

    from amos_brain.simulation_engine import (
        Scenario,
        SimulationRequest,
        SimulationType,
        get_simulation_engine,
    )

    # Create engine
    engine = get_simulation_engine()

    # Create scenarios
    print("\n[1] Creating simulation scenarios...")
    scenarios = [
        Scenario(name="normal_load", load_factor=1.0),
        Scenario(name="peak_load", load_factor=2.5),
        Scenario(name="stress_test", load_factor=5.0, failure_mode="cpu_stress"),
    ]
    for s in scenarios:
        print(f"   - {s.name}: {s.load_factor}x load")

    # Create request
    print("\n[2] Creating simulation request...")
    request = SimulationRequest(
        type=SimulationType.DEPLOYMENT_IMPACT,
        target="PR-123",
        repo_path=".",
        scenarios=scenarios,
        requested_by="demo_user",
    )
    print(f"   Simulation ID: {request.id}")
    print(f"   Target: {request.target}")
    print(f"   Scenarios: {len(request.scenarios)}")

    # Run simulation
    print("\n[3] Running simulation...")
    result = asyncio.get_event_loop().run_until_complete(engine.run_simulation(request))
    print(f"   Status: {result.status}")
    print(f"   Started: {result.started_at.isoformat()}")

    # Wait for completion
    import time

    time.sleep(1.5)

    # Get final result
    final = engine.get_result(request.id)
    if final and final.status == "completed":
        print("\n[4] Simulation completed!")
        print(f"   Confidence: {final.confidence_score:.0%}")
        print(f"   Scenario results: {len(final.scenario_results)}")

        # Impact summary
        impact = final.impact_analysis
        print("\n[5] Impact Analysis:")
        print(f"   Latency p95: {impact.performance.latency_p95.change_percent:+.1f}%")
        print(f"   Throughput: {impact.performance.throughput.change_percent:+.1f}%")
        print(f"   Error rate: {impact.performance.error_rate.change_percent:+.1f}%")
        print(f"   Daily cost: ${impact.costs.daily_cost:.2f}")
        print(f"   Cost change: {impact.costs.change_percent:+.1f}%")
        print(f"   Failure probability: {impact.risks.failure_probability:.1%}")
        print(f"   Rollback complexity: {impact.risks.rollback_complexity}")

        # Recommendations
        print("\n[6] Recommendations:")
        for rec in final.recommendations[:3]:
            print(f"   [{rec.priority.upper()}] {rec.description}")
            print(f"      Confidence: {rec.confidence:.0%}")

    return {
        "simulation_id": request.id,
        "status": result.status,
        "confidence": result.confidence_score if result else 0,
        "scenarios_run": len(result.scenario_results) if result else 0,
        "recommendations": len(final.recommendations) if final else 0,
    }


def demo_brain_client_integration() -> dict:
    """Demonstrate BrainClient facade integration."""
    print("\n" + "=" * 60)
    print("DEMO 4: BrainClient - Unified Axiom One Interface")
    print("=" * 60)

    from amos_brain.facade import BrainClient

    # Create client
    print("\n[1] Creating BrainClient...")
    client = BrainClient(repo_path=".")
    print("   Client initialized with Axiom One capabilities")

    # Spawn agent through facade
    print("\n[2] Spawning agent via BrainClient...")
    agent_result = client.spawn_agent(
        agent_class="repo-debugger",
        task_objective="Find all Python files with syntax errors",
    )
    print(f"   Agent ID: {agent_result['agent_id']}")
    print(f"   Run ID: {agent_result['run_id']}")
    print(f"   Budget: ${agent_result['budget_max_usd']}")
    print(f"   Permissions: {len(agent_result['permissions']['tools'])} tools")

    # Get agent status
    print("\n[3] Checking agent run status...")
    status = client.get_agent_run(agent_result["run_id"])
    if status:
        print(f"   Phase: {status['phase']}")
        print(f"   Actions: {status['actions_count']}")
        print(f"   Budget spent: ${status['budget_spent']:.4f}")

    # Simulate deployment
    print("\n[4] Running deployment simulation via BrainClient...")
    sim_result = client.simulate_deployment(
        target="feature/new-api",
        scenarios=[
            {"name": "normal", "load_factor": 1.0},
            {"name": "peak", "load_factor": 3.0},
        ],
    )
    print(f"   Simulation ID: {sim_result['simulation_id']}")
    print(f"   Status: {sim_result['status']}")
    print(f"   Confidence: {sim_result['confidence']:.0%}")

    # Note: Repo autopsy requires actual build failure context
    print("\n[5] Repo Autopsy available via client.autopsy_repo()")
    print("   (Skipped in demo - requires actual failure context)")

    return {
        "agent_spawned": True,
        "agent_id": agent_result["agent_id"],
        "run_id": agent_result["run_id"],
        "simulation_id": sim_result["simulation_id"],
        "simulation_confidence": sim_result["confidence"],
    }


def main():
    """Run all demos."""
    print("\n" + "=" * 70)
    print(" " * 15 + "AXIOM ONE CIVILIZATION SUBSTRATE")
    print(" " * 20 + "Working Demonstration")
    print("=" * 70)

    print("\nInitializing Axiom One capabilities...")
    print(f"Started at: {datetime.now(UTC).isoformat()}")

    results = {}

    # Run demos
    try:
        results["agent_fabric"] = demo_agent_fabric()
    except Exception as e:
        print(f"\nAgent Fabric Error: {e}")
        results["agent_fabric"] = {"error": str(e)}

    try:
        results["repo_autopsy"] = demo_repo_autopsy()
    except Exception as e:
        print(f"\nRepo Autopsy Error: {e}")
        results["repo_autopsy"] = {"error": str(e)}

    try:
        results["simulation"] = demo_simulation()
    except Exception as e:
        print(f"\nSimulation Error: {e}")
        results["simulation"] = {"error": str(e)}

    try:
        results["brain_client"] = demo_brain_client_integration()
    except Exception as e:
        print(f"\nBrain Client Error: {e}")
        results["brain_client"] = {"error": str(e)}

    # Summary
    print("\n" + "=" * 70)
    print("DEMO SUMMARY")
    print("=" * 70)

    for demo_name, demo_results in results.items():
        status = "✅ PASS" if "error" not in demo_results else "❌ FAIL"
        print(f"\n{demo_name.upper()}: {status}")
        for key, value in demo_results.items():
            if key != "error":
                print(f"  {key}: {value}")
            else:
                print(f"  Error: {value}")

    # Save results
    output_file = "axiom_one_demo_results.json"
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nResults saved to: {output_file}")

    print("\n" + "=" * 70)
    print("Axiom One demonstration complete!")
    print("=" * 70)

    return results


if __name__ == "__main__":
    main()
