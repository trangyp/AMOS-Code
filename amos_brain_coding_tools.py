#!/usr/bin/env python3
from typing import Any

"""AMOS Brain - Unified Coding Tools Interface

Integrates the strongest coding tools with the AMOS brain
cognitive engine for intelligent code analysis.
"""

import json
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


@dataclass
class ToolResult:
    """Result from a coding tool execution."""

    tool: str
    status: str
    issues: list[dict[str, Any]]
    summary: str
    timestamp: str


class AMOSBrainCodingTools:
    """Unified interface to the strongest coding tools."""

    def __init__(self, repo_path: str = ".") -> None:
        self.repo_path = Path(repo_path).resolve()
        self.brain_id = self._generate_brain_id()
        self.results: List[ToolResult] = []

    def _generate_brain_id(self) -> str:
        """Generate unique brain session ID."""
        return f"amos-brain-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}"

    def run_ruff(self, fix: bool = False) -> ToolResult:
        """Run Ruff linter - ultra-fast Python linter."""
        cmd = ["ruff", "check", str(self.repo_path)]
        if fix:
            cmd.extend(["--fix", "--exit-non-zero-on-fix"])

        result = subprocess.run(cmd, capture_output=True, text=True)

        issues = []
        for line in result.stdout.split("\n"):
            if ":" in line and any(
                sev in line for sev in ["E", "F", "W", "I", "N", "D", "B", "C4", "UP", "SIM", "S"]
            ):
                parts = line.split(":")
                if len(parts) >= 3:
                    issues.append(
                        {
                            "file": parts[0],
                            "line": parts[1] if len(parts) > 1 else "0",
                            "message": ":".join(parts[2:]),
                            "severity": "error" if "E" in line or "F" in line else "warning",
                        }
                    )

        return ToolResult(
            tool="ruff",
            status="passed" if result.returncode == 0 else "failed",
            issues=issues[:20],
            summary=f"Found {len(issues)} issues" if issues else "No issues found",
            timestamp=datetime.now(timezone.utc).isoformat(),
        )

    def run_mypy(self) -> ToolResult:
        """Run MyPy - static type checker."""
        cmd = ["mypy", str(self.repo_path), "--ignore-missing-imports", "--show-error-codes"]
        result = subprocess.run(cmd, capture_output=True, text=True)

        issues = []
        for line in result.stdout.split("\n"):
            if ": error:" in line or ": note:" in line:
                parts = line.split(":", 2)
                if len(parts) >= 3:
                    issues.append(
                        {
                            "file": parts[0],
                            "line": parts[1],
                            "message": parts[2],
                            "severity": "error" if "error" in line else "note",
                        }
                    )

        return ToolResult(
            tool="mypy",
            status="passed" if result.returncode == 0 else "failed",
            issues=issues[:20],
            summary=f"Found {len(issues)} type issues" if issues else "Type checking passed",
            timestamp=datetime.now(timezone.utc).isoformat(),
        )

    def run_bandit(self) -> ToolResult:
        """Run Bandit - security vulnerability scanner."""
        cmd = ["bandit", "-r", str(self.repo_path), "-f", "json", "-q"]
        result = subprocess.run(cmd, capture_output=True, text=True)

        issues = []
        try:
            data = json.loads(result.stdout) if result.stdout else {"results": []}
            for item in data.get("results", []):
                issues.append(
                    {
                        "file": item.get("filename", ""),
                        "line": str(item.get("line_number", 0)),
                        "message": item.get("issue_text", ""),
                        "severity": item.get("issue_severity", "unknown").lower(),
                    }
                )
        except json.JSONDecodeError:
            pass

        return ToolResult(
            tool="bandit",
            status="passed" if not issues else "failed",
            issues=issues[:20],
            summary=f"Found {len(issues)} security issues" if issues else "No security issues",
            timestamp=datetime.now(timezone.utc).isoformat(),
        )

    def run_vulture(self) -> ToolResult:
        """Run Vulture - dead code detector."""
        cmd = ["vulture", str(self.repo_path), "--min-confidence", "80"]
        result = subprocess.run(cmd, capture_output=True, text=True)

        issues = []
        for line in result.stdout.split("\n"):
            if ":" in line:
                parts = line.split(":")
                if len(parts) >= 3:
                    issues.append(
                        {
                            "file": parts[0],
                            "line": parts[1],
                            "message": ":".join(parts[2:]),
                            "severity": "warning",
                        }
                    )

        return ToolResult(
            tool="vulture",
            status="passed" if not issues else "warning",
            issues=issues[:20],
            summary=f"Found {len(issues)} dead code items" if issues else "No dead code detected",
            timestamp=datetime.now(timezone.utc).isoformat(),
        )

    def run_pyupgrade(self, py_version: str = "3.12") -> ToolResult:
        """Run pyupgrade - Python upgrade checker."""
        cmd = [
            "pyupgrade",
            f"--py{py_version.replace('.', '')}",
            "--diff",
            "--recursive",
            str(self.repo_path),
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)

        return ToolResult(
            tool="pyupgrade",
            status="passed" if not result.stdout else "warning",
            issues=[{"message": result.stdout}] if result.stdout else [],
            summary="Code is modern" if not result.stdout else "Upgrade opportunities found",
            timestamp=datetime.now(timezone.utc).isoformat(),
        )

    def run_all(self) -> dict[str, ToolResult]:
        """Run all strongest coding tools."""
        print("=" * 60)
        print("AMOS BRAIN: Running Strongest Coding Tools")
        print(f"Brain ID: {self.brain_id}")
        print(f"Repository: {self.repo_path}")
        print(f"Timestamp: {datetime.now(timezone.utc).isoformat()}")
        print("=" * 60)

        tools = [
            ("ruff", self.run_ruff),
            ("mypy", self.run_mypy),
            ("bandit", self.run_bandit),
            ("vulture", self.run_vulture),
            ("pyupgrade", self.run_pyupgrade),
        ]

        results = {}
        for name, runner in tools:
            print(f"\n🔍 Running {name}...")
            try:
                result = runner()
                results[name] = result
                icon = (
                    "✅"
                    if result.status == "passed"
                    else "⚠️"
                    if result.status == "warning"
                    else "❌"
                )
                print(f"   {icon} {result.summary}")
            except Exception as e:
                print(f"   ❌ {name} failed: {e}")
                results[name] = ToolResult(
                    tool=name,
                    status="error",
                    issues=[{"message": str(e)}],
                    summary=f"Execution failed: {e}",
                    timestamp=datetime.now(timezone.utc).isoformat(),
                )

        print("\n" + "=" * 60)
        print("Analysis Complete")
        print("=" * 60)

        return results

    def generate_report(self, results: Dict[str, ToolResult]) -> str:
        """Generate comprehensive analysis report."""
        lines = [
            "# AMOS Brain Coding Analysis Report",
            "",
            f"**Brain ID:** {self.brain_id}",
            f"**Repository:** {self.repo_path}",
            f"**Timestamp:** {datetime.now(timezone.utc).isoformat()}",
            "",
            "## Summary",
            "",
        ]

        total_issues = sum(len(r.issues) for r in results.values())
        passed = sum(1 for r in results.values() if r.status == "passed")

        lines.append(f"- **Tools Run:** {len(results)}")
        lines.append(f"- **Passed:** {passed}/{len(results)}")
        lines.append(f"- **Total Issues:** {total_issues}")
        lines.append("")

        for name, result in results.items():
            icon = (
                "✅" if result.status == "passed" else "⚠️" if result.status == "warning" else "❌"
            )
            lines.append(f"### {icon} {name.upper()}")
            lines.append(f"**Status:** {result.status}")
            lines.append(f"**Summary:** {result.summary}")
            if result.issues:
                lines.append("**Issues:**")
                for issue in result.issues[:10]:
                    msg = issue.get("message", "Unknown")
                    lines.append(f"- {msg}")
            lines.append("")

        return "\n".join(lines)


def main() -> None:
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="AMOS Brain Coding Tools")
    parser.add_argument("--path", "-p", default=".", help="Repository path")
    parser.add_argument("--report", "-r", help="Save report to file")
    args = parser.parse_args()

    tools = AMOSBrainCodingTools(args.path)
    results = tools.run_all()

    report = tools.generate_report(results)
    print("\n" + report)

    if args.report:
        Path(args.report).write_text(report)
        print(f"\n📄 Report saved to: {args.report}")


if __name__ == "__main__":
    main()
