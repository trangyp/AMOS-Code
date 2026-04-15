#!/usr/bin/env python3
"""CI report parser for Repo Doctor GitHub Actions integration.

Parses JSON reports and outputs formatted summaries for GitHub Actions.
"""

import json
import sys
from pathlib import Path
from typing import Optional


def parse_invariant_failures(report_path: str) -> tuple[int, list[str]]:
    """Parse invariant failures from report.

    Returns:
        Tuple of (count, list_of_failures)
    """
    try:
        with open(report_path) as f:
            data = json.load(f)
        failures = data.get("hard_invariant_failures", [])
        return len(failures), failures
    except Exception:
        return 0, []


def parse_energy(report_path: str) -> Optional[float]:
    """Parse energy value from report."""
    try:
        with open(report_path) as f:
            data = json.load(f)
        energy = data.get("energy")
        return float(energy) if energy is not None else None
    except Exception:
        return None


def parse_bandit_results(report_path: str) -> dict[str, int]:
    """Parse Bandit security scan results.

    Returns:
        Dict with severity counts
    """
    try:
        with open(report_path) as f:
            data = json.load(f)

        results = data.get("results", [])
        counts = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}

        for result in results:
            severity = result.get("issue_severity")
            if severity in counts:
                counts[severity] += 1

        return counts
    except Exception:
        return {"HIGH": 0, "MEDIUM": 0, "LOW": 0}


def check_critical_failures(report_path: str) -> list[str]:
    """Check for critical invariant failures (Parse or Security).

    Returns:
        List of critical failure names
    """
    try:
        with open(report_path) as f:
            data = json.load(f)

        failures = data.get("hard_invariant_failures", [])
        critical = [f for f in failures if "parse" in f.lower() or "security" in f.lower()]
        return critical
    except Exception:
        return []


def print_step_summary(report_path: str, bandit_path: Optional[str] = None) -> None:
    """Print GitHub Actions step summary."""
    # Energy section
    print("## Repository Energy State\n")

    energy = parse_energy(report_path)
    if energy is not None:
        print(f"**Total Energy:** {energy:.2f}\n")

        if energy < 5.0:
            print("**Status:** 🟢 Healthy\n")
        elif energy < 10.0:
            print("**Status:** 🟡 Warning\n")
        else:
            print("**Status:** 🔴 Critical\n")
    else:
        print("**Total Energy:** N/A\n")

    # Invariant section
    print("## Hard Invariant Results\n")

    count, failures = parse_invariant_failures(report_path)
    if failures:
        print(f"❌ {count} invariants failed:\n")
        for f in failures:
            print(f"  - {f}")
    else:
        print("✅ All hard invariants passing\n")

    # Security section
    if bandit_path and Path(bandit_path).exists():
        print("\n## Security Analysis\n")

        counts = parse_bandit_results(bandit_path)
        print("| Severity | Count |")
        print("|----------|-------|")
        print(f"| 🔴 High | {counts['HIGH']} |")
        print(f"| 🟡 Medium | {counts['MEDIUM']} |")
        print(f"| 🟢 Low | {counts['LOW']} |")


def main() -> int:
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: ci_report_parser.py <command> [args...]", file=sys.stderr)
        print("Commands: summary, critical, energy, invariants", file=sys.stderr)
        return 1

    command = sys.argv[1]
    report_path = sys.argv[2] if len(sys.argv) > 2 else "repo_doctor_full_report.json"

    if command == "summary":
        bandit_path = sys.argv[3] if len(sys.argv) > 3 else None
        print_step_summary(report_path, bandit_path)
        return 0

    elif command == "critical":
        critical = check_critical_failures(report_path)
        if critical:
            print(f"Critical failures found: {len(critical)}")
            for c in critical:
                print(f"  - {c}")
            return 1
        print("No critical failures")
        return 0

    elif command == "energy":
        energy = parse_energy(report_path)
        print(energy if energy is not None else "N/A")
        return 0

    elif command == "invariants":
        count, failures = parse_invariant_failures(report_path)
        print(f"Failed: {count}")
        for f in failures:
            print(f"  - {f}")
        return 0 if count == 0 else 1

    else:
        print(f"Unknown command: {command}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
