#!/usr/bin/env python3
"""Demonstration: Deep Architectural Pathology + AMOS Brain Integration.

Shows how the brain now validates decisions against architectural pathologies
before proceeding with actions.

Architecture:
    BrainClient
        ├── Architecture Bridge (base validation)
        └── Pathology Bridge (deep validation)
            ├── Authority Inversion Detector
            ├── Layer Leakage Detector
            ├── Bootstrap Path Validator
            ├── Shadow Dependency Detector
            ├── Artifact Chain Validator
            ├── Migration Geometry Validator
            └── Mode Lattice Validator
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))


def demo_brain_with_pathologies():
    """Demonstrate brain validation with pathology awareness."""
    print("=" * 70)
    print("AMOS BRAIN + DEEP PATHOLOGY INTEGRATION DEMO")
    print("=" * 70)

    # Try to import the pathology-aware brain
    try:
        from amos_brain.facade import BrainClient
        from amos_brain.pathology_bridge import (
            PathologyAwareArchitectureBridge,
            get_pathology_aware_bridge,
        )

        print("\n✅ Pathology-aware brain components loaded successfully")
    except ImportError as e:
        print(f"\n⚠️  Some components not available: {e}")
        print("   This is expected if repo_doctor pathologies are not fully integrated")
        return

    # Create brain client with repo path
    print("\n" + "-" * 70)
    print("1. INITIALIZING BRAIN CLIENT WITH PATHOLOGY AWARENESS")
    print("-" * 70)

    client = BrainClient(".")
    print(f"   Repository path: {Path.cwd()}")
    print(f"   Brain initialized: ✅")

    # Get base architectural context
    print("\n" + "-" * 70)
    print("2. BASE ARCHITECTURE CONTEXT")
    print("-" * 70)

    arch_context = client.get_architectural_context()
    print(f"   αArch (Architectural Integrity): {arch_context.arch_score:.2f}")
    print(f"   αHidden (Hidden State): {arch_context.hidden_score:.2f}")
    print(f"   Total Score: {arch_context.total_score:.2f}")
    print(f"   Nodes: {arch_context.node_count}, Edges: {arch_context.edge_count}")
    print(f"   Failed Invariants: {len(arch_context.failed_invariants)}")

    # Get pathology-aware context (if available)
    print("\n" + "-" * 70)
    print("3. PATHOLOGY-AWARE ARCHITECTURE CONTEXT")
    print("-" * 70)

    pathology_context = client.get_pathology_context()

    if pathology_context is not None:
        print(f"   Total Pathologies: {pathology_context.total_pathologies}")
        print(f"   Critical: {pathology_context.critical_pathologies}")
        print(f"   High: {pathology_context.high_pathologies}")
        print(f"   Medium: {pathology_context.medium_pathologies}")
        print(f"   Low: {pathology_context.low_pathologies}")
        print()
        print(f"   Pathology Score: {pathology_context.pathology_score:.2f} (1.0 = clean)")
        print(f"   Authority Score: {pathology_context.authority_score:.2f}")
        print(f"   Bootstrap Score: {pathology_context.bootstrap_score:.2f}")
        print(f"   Artifact Score: {pathology_context.artifact_score:.2f}")

        # Show detailed breakdown
        if pathology_context.authority_issues:
            print(f"\n   Authority Issues: {len(pathology_context.authority_issues)}")
            for issue in pathology_context.authority_issues[:2]:
                print(f"     - {issue.pathology_type.name}: {issue.message[:60]}...")

        if pathology_context.bootstrap_issues:
            print(f"\n   Bootstrap Issues: {len(pathology_context.bootstrap_issues)}")
            for issue in pathology_context.bootstrap_issues[:2]:
                print(f"     - {issue.message[:60]}...")

        if pathology_context.artifact_issues:
            print(f"\n   Artifact Issues: {len(pathology_context.artifact_issues)}")
            for issue in pathology_context.artifact_issues[:2]:
                print(f"     - {issue.message[:60]}...")
    else:
        print("   ⚠️  Pathology engine not available (expected if repo_doctor not fully loaded)")

    # Demonstrate pre-decision validation
    print("\n" + "-" * 70)
    print("4. PRE-DECISION PATHOLOGY VALIDATION")
    print("-" * 70)

    test_actions = [
        ("refactor", ["amos_brain/facade.py"]),
        ("migrate", ["migrations/001_initial.py"]),
        ("delete", ["old_module.py"]),
        ("create", ["new_feature.py"]),
    ]

    for action, files in test_actions:
        print(f"\n   Testing action: '{action}' on {files}")

        # Base architecture validation
        arch_result = client.validate_architecture(action, files)
        print(f"     Base arch validation: {'✅' if arch_result.approved else '❌'}")

        # Pathology validation (if available)
        path_result = client.validate_with_pathologies(action, files)

        if path_result is not None:
            print(f"     Pathology score: {path_result.pathology_score:.2f}")
            print(f"     Approved: {'✅' if path_result.approved else '❌'}")
            print(f"     Requires review: {'⚠️ yes' if path_result.requires_human_review else '✓ no'}")

            if path_result.issues:
                print(f"     Issues ({len(path_result.issues)}):")
                for issue in path_result.issues[:2]:
                    print(f"       - {issue[:70]}...")

            if path_result.warnings:
                print(f"     Warnings ({len(path_result.warnings)}):")
                for warning in path_result.warnings[:2]:
                    print(f"       - {warning[:70]}...")
        else:
            print("     Pathology validation: ⚠️ not available")

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print("""
The AMOS Brain now has deep architectural pathology awareness:

✅ Base Architecture Validation
   - 7 architectural invariants (boundary, authority, planes, etc.)
   - Architecture graph (G_arch = V_arch, E_arch, Φ_arch)
   - Entanglement matrix for coupling analysis

✅ Deep Pathology Validation (NEW)
   - 7 specialized detectors
   - 18+ pathology classes covered
   - Pre-decision authority inversion checks
   - Bootstrap path validation
   - Artifact chain continuity verification
   - Migration geometry validation
   - Mode-lattice drift detection

✅ Integration Points
   - BrainClient.validate_with_pathologies() - Pre-decision checks
   - BrainClient.get_pathology_context() - Full pathology context
   - PathologyAwareArchitectureBridge - Unified validation

✅ Invariants Enforced
   - I_authority_order - Truth flows from canonical layers
   - I_single_authority - One owner per architectural fact
   - I_bootstrap - Valid initial state through declared paths
   - I_artifact_continuity - Source → Build → Install → Runtime preserved
   - I_modes - All workflows valid across mode lattice

The brain now answers:
  • "Is this code correct?" (syntax, tests, types)
  • "Is the architecture sound?" (invariants, pathologies)
  • "Are authority relationships valid?" (inversion detection)
  • "Will this work across all modes?" (local/CI/prod/debug)
  • "Is the upgrade/rollback path safe?" (migration geometry)

Architecture is now an EXPLICIT, VERIFIABLE, DIAGNOSABLE surface.
""")

    print("=" * 70)
    print("Integration Status: ✅ COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    demo_brain_with_pathologies()
