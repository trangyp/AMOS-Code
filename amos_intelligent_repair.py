#!/usr/bin/env python3
"""AMOS Intelligent Code Repair - Fixes bare except clauses with brain guidance."""

from __future__ import annotations

import logging
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from amos_brain_working import think
from amos_task_automation import TaskAutomation

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("amos_repair")


@dataclass
class RepairIssue:
    """Issue found that needs repair."""

    file_path: str
    line: int
    original: str
    issue_type: str
    context: str


@dataclass
class RepairResult:
    """Result of repair operation."""

    file_path: str
    line: int
    original: str
    replacement: str
    applied: bool
    error: Optional[str] = None


class IntelligentCodeRepair:
    """Intelligently repair code issues using brain guidance."""

    def __init__(self):
        self.task_auto = TaskAutomation()
        self.repairs: list[RepairResult] = []

    def find_bare_excepts(self, file_path: str) -> list[RepairIssue]:
        """Find all bare except clauses in a file."""
        path = Path(file_path)
        if not path.exists():
            return []

        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            return []

        issues = []
        lines = content.split("\n")

        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            # Match bare except:
            if stripped == "except:" or re.match(r"^except\s*:\s*$", stripped):
                # Get context (previous lines for context)
                context_start = max(0, i - 3)
                context = "\n".join(lines[context_start:i])
                issues.append(
                    RepairIssue(
                        file_path=str(path),
                        line=i,
                        original=line,
                        issue_type="bare_except",
                        context=context,
                    )
                )

        return issues

    def get_brain_recommendation(self, issue: RepairIssue) -> str:
        """Ask brain for best replacement strategy."""
        try:
            result = think(
                f"Code context:\n{issue.context}\n\n"
                f"Line {issue.line} has bare 'except:'. "
                f"What specific exception type should we catch? "
                f"Options: Exception, RuntimeError, ValueError. "
                f"Return just the exception type name.",
                {"context": "code_repair", "file": issue.file_path},
            )
            # Extract recommendation from brain response
            response = str(result.get("response", ""))
            if "Exception" in response:
                return "Exception"
            elif "RuntimeError" in response:
                return "RuntimeError"
            elif "ValueError" in response:
                return "ValueError"
            return "Exception"  # Default safe choice
        except Exception:
            return "Exception"

    def repair_bare_except(self, issue: RepairIssue) -> RepairResult:
        """Repair a bare except clause."""
        path = Path(issue.file_path)

        try:
            content = path.read_text(encoding="utf-8")
        except Exception as e:
            return RepairResult(
                file_path=issue.file_path,
                line=issue.line,
                original=issue.original,
                replacement="",
                applied=False,
                error=f"Cannot read file: {e}",
            )

        lines = content.split("\n")
        if issue.line < 1 or issue.line > len(lines):
            return RepairResult(
                file_path=issue.file_path,
                line=issue.line,
                original=issue.original,
                replacement="",
                applied=False,
                error="Line number out of range",
            )

        # Get brain recommendation
        exception_type = self.get_brain_recommendation(issue)

        # Create replacement
        original_line = lines[issue.line - 1]
        # Preserve indentation
        indent = original_line[: len(original_line) - len(original_line.lstrip())]
        replacement = f"{indent}except {exception_type}:"

        # Apply replacement
        lines[issue.line - 1] = replacement

        try:
            path.write_text("\n".join(lines), encoding="utf-8")
            return RepairResult(
                file_path=issue.file_path,
                line=issue.line,
                original=issue.original.strip(),
                replacement=replacement.strip(),
                applied=True,
            )
        except Exception as e:
            return RepairResult(
                file_path=issue.file_path,
                line=issue.line,
                original=issue.original.strip(),
                replacement=replacement.strip(),
                applied=False,
                error=f"Cannot write file: {e}",
            )

    def repair_file(self, file_path: str) -> list[RepairResult]:
        """Repair all issues in a file."""
        issues = self.find_bare_excepts(file_path)
        results = []

        for issue in issues:
            logger.info(f"Repairing {issue.file_path}:{issue.line}")
            result = self.repair_bare_except(issue)
            results.append(result)
            self.repairs.append(result)

        return results

    def generate_report(self) -> dict:
        """Generate repair report."""
        total = len(self.repairs)
        applied = len([r for r in self.repairs if r.applied])
        failed = total - applied

        return {
            "total_issues": total,
            "repairs_applied": applied,
            "repairs_failed": failed,
            "success_rate": f"{(applied / total * 100):.1f}%" if total > 0 else "N/A",
            "details": [
                {
                    "file": r.file_path,
                    "line": r.line,
                    "original": r.original,
                    "replacement": r.replacement,
                    "status": "fixed" if r.applied else f"failed: {r.error}",
                }
                for r in self.repairs
            ],
        }


def main() -> int:
    """Run intelligent code repair."""
    print("=" * 70)
    print("AMOS Intelligent Code Repair")
    print("=" * 70)

    repairer = IntelligentCodeRepair()

    # Repair critical files with bare excepts
    files_to_repair = [
        "server/amos_api_hub.py",
        "amos_brain/doctor.py",
        "amos_brain_healer.py",
        "AMOS_ORGANISM_OS/03_IMMUNE/agent_invariant_audit.py",
        "amos_equation_verify_hook.py",
        "amos_mcp_tools.py",
    ]

    for file_path in files_to_repair:
        path = Path(file_path)
        if path.exists():
            print(f"\nRepairing {file_path}...")
            results = repairer.repair_file(file_path)
            for r in results:
                status = "✓" if r.applied else "✗"
                print(f"  {status} Line {r.line}: {r.original} -> {r.replacement}")

    # Generate report
    report = repairer.generate_report()

    print("\n" + "=" * 70)
    print("REPAIR REPORT")
    print("=" * 70)
    print(f"Total issues found: {report['total_issues']}")
    print(f"Repairs applied: {report['repairs_applied']}")
    print(f"Repairs failed: {report['repairs_failed']}")
    print(f"Success rate: {report['success_rate']}")
    print("=" * 70)

    return 0 if report["repairs_failed"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
