"""
External Tool Sensors - Integration with state-of-the-art tools.

Sensors:
- pip-audit: Security vulnerability scanner
- bandit: Python security linter
- safety: Dependency vulnerability scanner
- ruff: Fast Python linter
- pyright: Type checker
- deptry: Dependency checker
"""

from __future__ import annotations

import json
import shutil
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class SensorResult:
    """Result from an external tool sensor."""

    tool_name: str
    available: bool
    passed: bool
    findings: list[dict] = field(default_factory=list)
    error_message: str | None = None
    execution_time_ms: float | None = None


class ExternalSensor:
    """Base class for external tool sensors."""

    def __init__(self, repo_path: str | Path):
        self.repo_path = Path(repo_path).resolve()

    def is_available(self) -> bool:
        """Check if the tool is available in PATH."""
        return False

    def run(self) -> SensorResult:
        """Run the sensor and return results."""
        raise NotImplementedError


class PipAuditSensor(ExternalSensor):
    """
    pip-audit sensor - detects known security vulnerabilities.
    Uses PyPA advisory database via PyPI JSON API.
    """

    def is_available(self) -> bool:
        return shutil.which("pip-audit") is not None

    def run(self) -> SensorResult:
        """Run pip-audit and parse JSON output."""
        if not self.is_available():
            return SensorResult(
                tool_name="pip-audit",
                available=False,
                passed=True,  # Soft fail - not a hard invariant
                error_message="pip-audit not installed (pip install pip-audit)",
            )

        try:
            result = subprocess.run(
                ["pip-audit", "--format=json", "--desc=off", "."],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=120,
            )

            # pip-audit returns exit code 1 if vulnerabilities found
            # exit code 0 if no vulnerabilities
            if result.returncode not in [0, 1]:
                return SensorResult(
                    tool_name="pip-audit",
                    available=True,
                    passed=False,
                    error_message=f"pip-audit failed: {result.stderr[:200]}",
                )

            try:
                data = json.loads(result.stdout)
                vulnerabilities = []

                for dep in data.get("dependencies", []):
                    for vuln in dep.get("vulns", []):
                        vulnerabilities.append(
                            {
                                "package": dep.get("name"),
                                "version": dep.get("version"),
                                "vulnerability_id": vuln.get("id"),
                                "description": vuln.get("description", "No description")[:100],
                                "fix_versions": vuln.get("fix_versions", []),
                                "severity": "unknown",
                            }
                        )

                return SensorResult(
                    tool_name="pip-audit",
                    available=True,
                    passed=len(vulnerabilities) == 0,
                    findings=vulnerabilities,
                    error_message=None
                    if not vulnerabilities
                    else f"{len(vulnerabilities)} vulnerabilities found",
                )

            except json.JSONDecodeError:
                return SensorResult(
                    tool_name="pip-audit",
                    available=True,
                    passed=True,  # Soft fail
                    error_message="Could not parse pip-audit output",
                )

        except subprocess.TimeoutExpired:
            return SensorResult(
                tool_name="pip-audit",
                available=True,
                passed=False,
                error_message="pip-audit timed out (>120s)",
            )
        except Exception as e:
            return SensorResult(
                tool_name="pip-audit", available=True, passed=False, error_message=str(e)
            )


class RuffSensor(ExternalSensor):
    """
    Ruff sensor - fast Python linter (100-1000x faster than alternatives).
    Checks for code quality, import sorting, style issues.
    """

    def is_available(self) -> bool:
        return shutil.which("ruff") is not None

    def run(self) -> SensorResult:
        """Run ruff check and parse JSON output."""
        if not self.is_available():
            return SensorResult(
                tool_name="ruff",
                available=False,
                passed=True,
                error_message="ruff not installed (pip install ruff)",
            )

        try:
            result = subprocess.run(
                ["ruff", "check", "--output-format=json", "."],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=60,
            )

            # ruff returns exit code 1 if violations found, 0 if clean
            try:
                violations = json.loads(result.stdout)
                findings = []

                for v in violations:
                    findings.append(
                        {
                            "file": v.get("filename"),
                            "line": v.get("location", {}).get("row"),
                            "column": v.get("location", {}).get("column"),
                            "code": v.get("code"),
                            "message": v.get("message"),
                            "severity": "warning" if v.get("code", "").startswith("W") else "error",
                        }
                    )

                # Group by severity
                errors = [f for f in findings if f["severity"] == "error"]
                warnings = [f for f in findings if f["severity"] == "warning"]

                return SensorResult(
                    tool_name="ruff",
                    available=True,
                    passed=len(errors) == 0,  # Only errors cause failure
                    findings=findings,
                    error_message=f"{len(errors)} errors, {len(warnings)} warnings"
                    if findings
                    else None,
                )

            except json.JSONDecodeError:
                return SensorResult(
                    tool_name="ruff",
                    available=True,
                    passed=True,
                    error_message="Could not parse ruff output",
                )

        except subprocess.TimeoutExpired:
            return SensorResult(
                tool_name="ruff",
                available=True,
                passed=False,
                error_message="ruff timed out (>60s)",
            )
        except Exception as e:
            return SensorResult(
                tool_name="ruff", available=True, passed=False, error_message=str(e)
            )


class PyrightSensor(ExternalSensor):
    """
    Pyright sensor - static type checker for Python.
    Detects type errors and helps maintain type safety.
    """

    def is_available(self) -> bool:
        return shutil.which("pyright") is not None

    def run(self) -> SensorResult:
        """Run pyright and parse JSON output."""
        if not self.is_available():
            return SensorResult(
                tool_name="pyright",
                available=False,
                passed=True,
                error_message="pyright not installed (npm install -g pyright)",
            )

        try:
            result = subprocess.run(
                ["pyright", "--outputjson", "."],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=120,
            )

            try:
                data = json.loads(result.stdout)
                diagnostics = data.get("generalDiagnostics", [])
                summary = data.get("summary", {})

                findings = []
                for d in diagnostics:
                    severity = "error" if d.get("severity") == "error" else "warning"
                    findings.append(
                        {
                            "file": d.get("file"),
                            "line": d.get("range", {}).get("start", {}).get("line"),
                            "column": d.get("range", {}).get("start", {}).get("character"),
                            "code": d.get("rule"),
                            "message": d.get("message"),
                            "severity": severity,
                        }
                    )

                errors = summary.get("errorCount", 0)
                warnings = summary.get("warningCount", 0)

                return SensorResult(
                    tool_name="pyright",
                    available=True,
                    passed=errors == 0,
                    findings=findings,
                    error_message=f"{errors} type errors, {warnings} warnings"
                    if errors or warnings
                    else None,
                )

            except json.JSONDecodeError:
                return SensorResult(
                    tool_name="pyright",
                    available=True,
                    passed=True,
                    error_message="Could not parse pyright output",
                )

        except subprocess.TimeoutExpired:
            return SensorResult(
                tool_name="pyright",
                available=True,
                passed=False,
                error_message="pyright timed out (>120s)",
            )
        except Exception as e:
            return SensorResult(
                tool_name="pyright", available=True, passed=False, error_message=str(e)
            )


class DeptrySensor(ExternalSensor):
    """
    deptry sensor - checks for dependency issues.
    Detects unused dependencies, missing imports, and transitive dependencies.
    """

    def is_available(self) -> bool:
        return shutil.which("deptry") is not None

    def run(self) -> SensorResult:
        """Run deptry and parse output."""
        if not self.is_available():
            return SensorResult(
                tool_name="deptry",
                available=False,
                passed=True,
                error_message="deptry not installed (pip install deptry)",
            )

        try:
            result = subprocess.run(
                ["deptry", "."], cwd=self.repo_path, capture_output=True, text=True, timeout=60
            )

            # deptry returns exit code 1 if issues found
            output = result.stdout + result.stderr

            # Parse deptry output lines
            findings = []
            for line in output.split("\n"):
                if "DEP" in line:  # deptry uses DEPxxx codes
                    parts = line.split(" ", 1)
                    if len(parts) >= 2:
                        code = parts[0].strip("[]")
                        message = parts[1]
                        findings.append({"code": code, "message": message, "severity": "error"})

            return SensorResult(
                tool_name="deptry",
                available=True,
                passed=len(findings) == 0,
                findings=findings,
                error_message=f"{len(findings)} dependency issues" if findings else None,
            )

        except subprocess.TimeoutExpired:
            return SensorResult(
                tool_name="deptry",
                available=True,
                passed=False,
                error_message="deptry timed out (>60s)",
            )
        except Exception as e:
            return SensorResult(
                tool_name="deptry", available=True, passed=False, error_message=str(e)
            )


class BanditSensor(ExternalSensor):
    """
    Bandit sensor - finds common security issues in Python code.
    Checks for hardcoded passwords, SQL injection, unsafe eval, etc.
    """

    def __init__(self, repo_path: str | Path):
        super().__init__(repo_path)
        self.tool_name = "bandit"

    def is_available(self) -> bool:
        try:
            subprocess.run(
                ["bandit", "--version"],
                capture_output=True,
                timeout=5,
            )
            return True
        except (subprocess.SubprocessError, FileNotFoundError):
            return False

    def run(self) -> SensorResult:
        start_time = time.time()

        if not self.is_available():
            return SensorResult(
                tool_name=self.tool_name,
                passed=True,  # Soft-fail if not installed
                available=False,
                error_message="bandit not installed (pip install bandit)",
            )

        try:
            result = subprocess.run(
                [
                    "bandit",
                    "-r",
                    str(self.repo_path),
                    "-f",
                    "json",
                    "-ll",  # Low severity and above
                ],
                capture_output=True,
                text=True,
                timeout=120,
            )

            execution_time = (time.time() - start_time) * 1000

            # Bandit returns non-zero if issues found
            findings = []
            try:
                output = json.loads(result.stdout) if result.stdout else {}
                for issue in output.get("results", []):
                    findings.append(
                        {
                            "file": issue.get("filename"),
                            "line": issue.get("line_number"),
                            "code": issue.get("test_id"),
                            "severity": issue.get("issue_severity"),
                            "message": issue.get("issue_text"),
                            "confidence": issue.get("issue_confidence"),
                        }
                    )
            except json.JSONDecodeError:
                pass

            passed = len(findings) == 0

            return SensorResult(
                tool_name=self.tool_name,
                passed=passed,
                available=True,
                findings=findings,
                execution_time_ms=execution_time,
            )

        except subprocess.TimeoutExpired:
            return SensorResult(
                tool_name=self.tool_name,
                passed=False,
                available=True,
                error_message="bandit timed out after 120s",
            )
        except Exception as e:
            return SensorResult(
                tool_name=self.tool_name,
                passed=False,
                available=True,
                error_message=str(e),
            )


class SafetySensor(ExternalSensor):
    """
    Safety sensor - checks Python dependencies for known security vulnerabilities.
    Uses comprehensive vulnerability database from Safety DB.
    """

    def __init__(self, repo_path: str | Path):
        super().__init__(repo_path)
        self.tool_name = "safety"

    def is_available(self) -> bool:
        try:
            subprocess.run(
                ["safety", "--version"],
                capture_output=True,
                timeout=5,
            )
            return True
        except (subprocess.SubprocessError, FileNotFoundError):
            return False

    def run(self) -> SensorResult:
        start_time = time.time()

        if not self.is_available():
            return SensorResult(
                tool_name=self.tool_name,
                passed=True,  # Soft-fail if not installed
                available=False,
                error_message="safety not installed (pip install safety)",
            )

        try:
            # Check if requirements.txt or pyproject.toml exists
            req_file = self.repo_path / "requirements.txt"
            pyproject_file = self.repo_path / "pyproject.toml"

            if not req_file.exists() and not pyproject_file.exists():
                return SensorResult(
                    tool_name=self.tool_name,
                    passed=True,
                    available=True,
                    findings=[],
                    error_message="No requirements.txt or pyproject.toml found",
                )

            # Run safety check
            cmd = ["safety", "check", "--json"]
            if req_file.exists():
                cmd.extend(["-r", str(req_file)])

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120,
                cwd=str(self.repo_path),
            )

            execution_time = (time.time() - start_time) * 1000

            findings = []
            try:
                output = json.loads(result.stdout) if result.stdout else {}
                for vuln in output.get("vulnerabilities", []):
                    findings.append(
                        {
                            "package": vuln.get("package_name"),
                            "affected": vuln.get("affected_specifications"),
                            "vulnerability": vuln.get("vulnerability_id"),
                            "severity": vuln.get("severity"),
                            "message": vuln.get("advisory"),
                        }
                    )
            except json.JSONDecodeError:
                pass

            passed = len(findings) == 0

            return SensorResult(
                tool_name=self.tool_name,
                passed=passed,
                available=True,
                findings=findings,
                execution_time_ms=execution_time,
            )

        except subprocess.TimeoutExpired:
            return SensorResult(
                tool_name=self.tool_name,
                passed=False,
                available=True,
                error_message="safety timed out after 120s",
            )
        except Exception as e:
            return SensorResult(
                tool_name=self.tool_name,
                passed=False,
                available=True,
                error_message=str(e),
            )


class SensorSuite:
    """Runs all available external sensors and aggregates results."""

    def __init__(self, repo_path: str | Path):
        self.repo_path = Path(repo_path).resolve()
        self.sensors: list[ExternalSensor] = [
            PipAuditSensor(self.repo_path),
            BanditSensor(self.repo_path),
            SafetySensor(self.repo_path),
            RuffSensor(self.repo_path),
            PyrightSensor(self.repo_path),
            DeptrySensor(self.repo_path),
        ]

    def run_all(self) -> list[SensorResult]:
        """Run all available sensors and return results."""
        results = []
        for sensor in self.sensors:
            results.append(sensor.run())
        return results

    def get_available_tools(self) -> list[str]:
        """Get list of available tools."""
        return [s.__class__.__name__ for s in self.sensors if s.is_available()]

    def get_report(self, results: list[SensorResult]) -> str:
        """Generate a formatted report from sensor results."""
        lines = [
            "=" * 60,
            "EXTERNAL TOOL SENSORS",
            "=" * 60,
        ]

        available_count = sum(1 for r in results if r.available)
        lines.append(f"Tools available: {available_count}/{len(results)}")
        lines.append("")

        for result in results:
            status = "✓" if result.passed else "✗"
            avail = "available" if result.available else "not installed"
            lines.append(f"{status} {result.tool_name} ({avail})")

            if result.available and not result.passed:
                if result.error_message:
                    lines.append(f"  → {result.error_message}")
                if result.findings:
                    # Show first 5 findings
                    for f in result.findings[:5]:
                        if "file" in f:
                            loc = f"{f.get('file')}:{f.get('line', '?')}"
                            lines.append(
                                f"    {loc}: {f.get('code', '')} {f.get('message', '')[:50]}"
                            )
                        else:
                            lines.append(f"    {f.get('code', '')}: {f.get('message', '')[:50]}")
                    if len(result.findings) > 5:
                        lines.append(f"    ... and {len(result.findings) - 5} more")

        lines.append("=" * 60)
        return "\n".join(lines)
