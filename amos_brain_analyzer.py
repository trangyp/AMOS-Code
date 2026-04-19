#!/usr/bin/env python3
"""
AMOS Brain Analyzer - Uses brain to analyze and fix codebase
"""

from amos_brain_working import think


def analyze_repo_status():
    """Use brain to analyze repository status."""

    # Critical files to check
    critical_files = [
        "axiom_one_standalone.py",
        "axiom_one_brain_bridge.py",
        "amos_canon_integration.py",
        "amos_brain_working.py",
        "clawspring/amos_brain/amos_kernel_runtime.py",
    ]

    # Use brain to prioritize
    result = think(
        "Analyze AMOS codebase and identify production blockers",
        {
            "task": "codebase_analysis",
            "critical_components": ["brain", "canon", "standalone_server"],
            "files": critical_files,
            "goal": "production_readiness",
        },
    )

    return result


def fix_file_with_brain(filepath: str, issue: str) -> dict:
    """Use brain to help fix a specific file issue."""

    result = think(
        f"Fix {issue} in {filepath}", {"file": filepath, "issue": issue, "action": "code_fix"}
    )

    return result


if __name__ == "__main__":
    print("=" * 70)
    print("🧠 AMOS BRAIN ANALYZER")
    print("=" * 70)

    # Run analysis
    analysis = analyze_repo_status()

    print(f"\nStatus: {analysis.get('status')}")
    print(f"Legality: {analysis.get('legality')}")
    print(f"Mode: {analysis.get('mode')}")
    print(f"Brain Used: {analysis.get('brain_used')}")

    if "kernel_result" in analysis:
        print("\n--- Kernel Result ---")
        kr = analysis["kernel_result"]
        if isinstance(kr, dict):
            if "legality" in kr:
                legality = kr["legality"]
                if isinstance(legality, dict):
                    print(f"Legality Score: {legality.get('score')}")
                else:
                    print(f"Legality: {legality}")
            print(f"Operating Mode: {kr.get('operating_mode')}")

    print("\n" + "=" * 70)
