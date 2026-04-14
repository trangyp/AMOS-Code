#!/usr/bin/env python3
"""
Architectural Integrity Engine Demo

Demonstrates the new higher-order architectural analysis capabilities
including boundary detection, authority analysis, and hidden interface discovery.
"""

import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from repo_doctor.architecture import (
    ArchitectureGraph,
    ArchitectureBuilder,
    ArchNodeType,
    ArchEdgeType,
    PlaneType,
    build_architecture_graph,
)
from repo_doctor.arch_invariants import (
    ArchitectureInvariantEngine,
    BoundaryInvariant,
    AuthorityInvariant,
    HiddenInterfaceInvariant,
    FolkloreInvariant,
)
from repo_doctor.state_vector import RepoStateVector, StateDimension
from repo_doctor.repair_plan import RepairPlanner


def demo_architecture_graph(repo_path: str = ".") -> None:
    """Demonstrate building and analyzing an architecture graph."""
    print("=" * 70)
    print("ARCHITECTURAL INTEGRITY ENGINE DEMO")
    print("=" * 70)
    
    # Build architecture graph
    print("\n1. Building Architecture Graph...")
    graph = build_architecture_graph(repo_path)
    
    print(f"   - Nodes discovered: {len(graph.nodes)}")
    print(f"   - Edges discovered: {len(graph.edges)}")
    print(f"   - Authority claims: {len(graph.authority_claims)}")
    
    # Show node types
    node_types = {}
    for node in graph.nodes.values():
        node_types[node.node_type.name] = node_types.get(node.node_type.name, 0) + 1
    
    print("\n   Node types:")
    for node_type, count in sorted(node_types.items()):
        print(f"     - {node_type}: {count}")
    
    # Show plane distribution
    plane_dist = {}
    for node in graph.nodes.values():
        if node.plane:
            plane_dist[node.plane.name] = plane_dist.get(node.plane.name, 0) + 1
    
    print("\n   Plane distribution:")
    for plane, count in sorted(plane_dist.items()):
        print(f"     - {plane}: {count}")


def demo_architectural_invariants(repo_path: str = ".") -> None:
    """Demonstrate running architectural invariants."""
    print("\n2. Running Architectural Invariants...")
    
    engine = ArchitectureInvariantEngine(repo_path)
    results = engine.run_all()
    
    print(f"   - Invariants checked: {len(results)}")
    
    passed = sum(1 for r in results if r.passed)
    failed = len(results) - passed
    
    print(f"   - Passed: {passed}")
    print(f"   - Failed: {failed}")
    
    if failed > 0:
        print("\n   Failed invariants:")
        for result in results:
            if not result.passed:
                print(f"     ✗ {result.invariant_name}: {result.message}")
                if result.details:
                    for detail in result.details[:3]:  # Show first 3
                        print(f"       - {detail}")
    else:
        print("\n   ✓ All architectural invariants passed!")


def demo_architectural_state(repo_path: str = ".") -> None:
    """Demonstrate getting architectural state dimensions."""
    print("\n3. Computing Architectural State Dimensions...")
    
    engine = ArchitectureInvariantEngine(repo_path)
    arch_score, hidden_score, results = engine.get_architectural_state()
    
    print(f"   - αArch(t) (Architectural Integrity): {arch_score:.2f}")
    print(f"   - αHidden(t) (Hidden State): {hidden_score:.2f}")
    
    # Create a state vector with the new dimensions
    state = RepoStateVector()
    state.set(StateDimension.ARCHITECTURE, arch_score)
    state.set(StateDimension.HIDDEN_STATE, hidden_score)
    
    print(f"\n   Full state vector includes {len(state.values)} dimensions:")
    print("   - 10 local dimensions (syntax, imports, build, tests, etc.)")
    print("   - 2 architectural dimensions (αArch, αHidden)")


def demo_architecture_aware_repair(repo_path: str = ".") -> None:
    """Demonstrate architecture-aware repair planning."""
    print("\n4. Architecture-Aware Repair Planning...")
    
    engine = ArchitectureInvariantEngine(repo_path)
    arch_score, hidden_score, results = engine.get_architectural_state()
    
    planner = RepairPlanner(repo_path)
    
    # Create a mock state
    state = RepoStateVector()
    state.set(StateDimension.ARCHITECTURE, arch_score)
    state.set(StateDimension.HIDDEN_STATE, hidden_score)
    
    # Generate architecture plan
    plan = planner.generate_architecture_plan(state, results)
    
    print(f"   - Total actions: {len(plan.actions)}")
    print(f"   - Automated fixes: {len(plan.automated_fixes)}")
    print(f"   - Manual fixes: {len(plan.manual_fixes)}")
    print(f"   - Total risk: {plan.total_risk}")
    print(f"   - Estimated time: {plan.estimated_time}")
    
    if plan.actions:
        print("\n   Repair actions with architecture constraints:")
        for action in plan.actions[:3]:  # Show first 3
            print(f"     - {action.description}")
            print(f"       Priority: {action.priority}, Risk: {action.estimated_risk}")
            print(f"       Preserves boundary: {action.preserves_boundary_integrity}")
            print(f"       Reduces authority dup: {action.reduces_authority_duplication}")


def main() -> int:
    """Main demo entry point."""
    repo_path = "."
    if len(sys.argv) > 1:
        repo_path = sys.argv[1]
    
    try:
        demo_architecture_graph(repo_path)
        demo_architectural_invariants(repo_path)
        demo_architectural_state(repo_path)
        demo_architecture_aware_repair(repo_path)
        
        print("\n" + "=" * 70)
        print("DEMO COMPLETE")
        print("=" * 70)
        print("\nThe Repo Doctor now includes:")
        print("  • Architecture graph modeling (G_arch = V_arch, E_arch, Φ_arch)")
        print("  • 7 architectural invariants (boundary, authority, planes, hidden, etc.)")
        print("  • 2 new state dimensions (αArch, αHidden)")
        print("  • Architecture-aware repair planning")
        print()
        
        return 0
        
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
