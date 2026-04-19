#!/usr/bin/env python3
"""Test Knowledge Sync Engine with enhanced reporting."""

from knowledge_sync_engine import KnowledgeSyncEngine


def main():
    engine = KnowledgeSyncEngine()

    # Scan both sources
    doc_eqs = engine.scan_documentation()
    code_eqs = engine.scan_implementations()

    print("=" * 60)
    print("Knowledge Synchronization Report")
    print("=" * 60)

    print(f"\nDocumentation equations found: {len(doc_eqs)}")
    for name in list(doc_eqs.keys())[:10]:
        print(f"  - {name}")

    print(f"\nCode equations found: {len(code_eqs)}")
    for name in list(code_eqs.keys())[:10]:
        print(f"  - {name}")

    # Generate report
    report = engine.generate_report()

    print("\n" + "=" * 60)
    print("Sync Status")
    print("=" * 60)
    print(f"  Total: {report['total']}")
    print(f"  Synced: {report['synced']}")
    print(f"  Doc only: {report['doc_only']}")
    print(f"  Code only: {report['code_only']}")
    print(f"  Coverage: {report['coverage']:.1f}%")

    print("\nRecommendations:")
    for rec in report["recommendations"]:
        print(f"  • {rec}")

    # List all code equations by phase pattern
    print("\n" + "=" * 60)
    print("Equations by Implementation Phase")
    print("=" * 60)

    phases = {}
    for name in code_eqs:
        if "stabilizer" in name or "surface_code" in name or "quantum_volume" in name:
            phase = "Phase 8: Quantum Computing"
        elif "black_hole" in name or "einstein" in name or "noether" in name:
            phase = "Phase 9: Fundamental Physics"
        elif "zne" in name or "cdr" in name or "pec" in name or "quasi_prob" in name:
            phase = "Phase 10: QEC/Mitigation"
        elif "vqe" in name or "qaoa" in name or "kernel" in name or "adaptive" in name:
            phase = "Phase 11: VQA/Modern AI"
        elif (
            "chern" in name
            or "anyon" in name
            or "wilson" in name
            or "scattering" in name
            or "qcd" in name
        ):
            phase = "Phase 12: Test-Time/QFT"
        elif (
            "plan" in name
            or "tool" in name
            or "thinking" in name
            or "verification" in name
            or "rollback" in name
        ):
            phase = "Phase 13: Agentic AI"
        else:
            phase = "Other"

        if phase not in phases:
            phases[phase] = []
        phases[phase].append(name)

    for phase in sorted(phases.keys()):
        print(f"\n{phase} ({len(phases[phase])} equations)")
        for name in phases[phase][:5]:
            print(f"  • {name}")
        if len(phases[phase]) > 5:
            print(f"  ... and {len(phases[phase]) - 5} more")

    print("\n" + "=" * 60)
    print("AMOS Knowledge Sync Engine - Operational")
    print("=" * 60)


if __name__ == "__main__":
    main()
