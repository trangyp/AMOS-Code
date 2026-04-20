"""
Repo Doctor Security Scanner - Deterministic Verification Envelope

Security-first pipeline that all AI patches must pass before being trusted.
Integrates open-source security tools: Semgrep, Trivy, Gitleaks, OSV-Scanner.

Equation:
    Ψ_security(t) = [semgrep(t), trivy(t), gitleaks(t), osv(t), ruff(t), pyright(t)]

Invariant:
    ∀ patch ∈ AI_Patches : verify(patch) → {passed, blocked, needs_review}
"""

from __future__ import annotations

import asyncio
import json
import logging
import subprocess
from dataclasses import dataclass, field
from datetime import datetime, timezone

UTC = timezone.utc
from enum import Enum
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class Severity(Enum):
    """Security finding severity levels."""

    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class SecurityFinding:
    """Single security finding from any scanner."""

    tool: str
    rule_id: str
    severity: Severity
    message: str
    file_path: str = None
    line_number: int = None
    column: int = None
    snippet: str = None
    fix: str = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ScanResult:
    """Result from a single security scanner."""

    tool: str
    passed: bool
    findings: list[SecurityFinding] = field(default_factory=list)
    execution_time_ms: float = 0.0
    error_message: str = None
    raw_output: str = None


@dataclass
class VerificationReceipt:
    """Receipt for a complete security verification run."""

    receipt_id: str
    timestamp: str
    repository_path: str
    commit_hash: str
    scan_results: list[ScanResult]
    overall_passed: bool
    critical_count: int = 0
    high_count: int = 0
    medium_count: int = 0
    low_count: int = 0
    blocking_findings: list[SecurityFinding] = field(default_factory=list)


class SemgrepScanner:
    """Semgrep CE static code analysis."""

    def __init__(self, config_path: str = None):
        self.config_path = config_path
        self.rules = [
            "p/security-audit",
            "p/secrets",
            "p/owasp-top-ten",
            "p/cwe-top-25",
            "p/python",
        ]

    async def scan(self, repo_path: Path, targets: list[str] = None) -> ScanResult:
        """Run Semgrep scan on repository."""
        start = datetime.now(timezone.utc)
        cmd = [
            "semgrep",
            "--json",
            "--quiet",
            "--config",
            self.config_path or "auto",
        ]
        for rule in self.rules:
            cmd.extend(["--config", rule])

        scan_targets = targets or ["."]
        cmd.extend(scan_targets)

        try:
            result = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=repo_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            stdout, stderr = await result.communicate()
            execution_time = (datetime.now(timezone.utc) - start).total_seconds() * 1000

            if result.returncode not in (0, 1):  # 1 = findings found
                return ScanResult(
                    tool="semgrep",
                    passed=False,
                    error_message=f"Semgrep failed: {stderr.decode()}",
                    execution_time_ms=execution_time,
                )

            data = json.loads(stdout.decode())
            findings = []
            for result in data.get("results", []):
                finding = SecurityFinding(
                    tool="semgrep",
                    rule_id=result.get("check_id", "unknown"),
                    severity=self._map_severity(result.get("extra", {}).get("severity", "WARNING")),
                    message=result.get("extra", {}).get("message", ""),
                    file_path=result.get("path"),
                    line_number=result.get("start", {}).get("line"),
                    column=result.get("start", {}).get("col"),
                    snippet=result.get("extra", {}).get("lines"),
                    fix=result.get("extra", {}).get("fix"),
                )
                findings.append(finding)

            passed = not any(f.severity in (Severity.HIGH, Severity.CRITICAL) for f in findings)
            return ScanResult(
                tool="semgrep",
                passed=passed,
                findings=findings,
                execution_time_ms=execution_time,
                raw_output=stdout.decode(),
            )
        except FileNotFoundError:
            return ScanResult(
                tool="semgrep",
                passed=False,
                error_message="Semgrep not installed. Install with: pip install semgrep",
            )
        except Exception as e:
            return ScanResult(tool="semgrep", passed=False, error_message=str(e))

    def _map_severity(self, semgrep_severity: str) -> Severity:
        mapping = {
            "ERROR": Severity.CRITICAL,
            "WARNING": Severity.HIGH,
            "INFO": Severity.MEDIUM,
        }
        return mapping.get(semgrep_severity.upper(), Severity.LOW)


class TrivyScanner:
    """Trivy filesystem, misconfiguration, and vulnerability scanner."""

    async def scan(self, repo_path: Path) -> ScanResult:
        """Run Trivy fs scan on repository."""
        start = datetime.now(timezone.utc)
        cmd = [
            "trivy",
            "fs",
            "--format",
            "json",
            "--scanners",
            "vuln,config,secret",
            str(repo_path),
        ]

        try:
            result = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            stdout, stderr = await result.communicate()
            execution_time = (datetime.now(timezone.utc) - start).total_seconds() * 1000

            if result.returncode != 0:
                return ScanResult(
                    tool="trivy",
                    passed=False,
                    error_message=f"Trivy failed: {stderr.decode()}",
                    execution_time_ms=execution_time,
                )

            data = json.loads(stdout.decode())
            findings = []

            # Parse vulnerability results
            for result in data.get("Results", []):
                for vuln in result.get("Vulnerabilities", []):
                    finding = SecurityFinding(
                        tool="trivy",
                        rule_id=vuln.get("VulnerabilityID", "unknown"),
                        severity=self._map_severity(vuln.get("Severity", "UNKNOWN")),
                        message=f"{vuln.get('Title', '')}: {vuln.get('Description', '')}",
                        file_path=result.get("Target"),
                        metadata={
                            "pkg_name": vuln.get("PkgName"),
                            "installed_version": vuln.get("InstalledVersion"),
                            "fixed_version": vuln.get("FixedVersion"),
                        },
                    )
                    findings.append(finding)

                # Parse secret results
                for secret in result.get("Secrets", []):
                    finding = SecurityFinding(
                        tool="trivy",
                        rule_id=secret.get("RuleID", "secret"),
                        severity=self._map_severity(secret.get("Severity", "HIGH")),
                        message=f"Secret detected: {secret.get('Title', '')}",
                        file_path=result.get("Target"),
                        line_number=secret.get("StartLine"),
                        snippet=secret.get("Match"),
                    )
                    findings.append(finding)

            passed = not any(f.severity in (Severity.CRITICAL,) for f in findings)
            return ScanResult(
                tool="trivy",
                passed=passed,
                findings=findings,
                execution_time_ms=execution_time,
                raw_output=stdout.decode(),
            )
        except FileNotFoundError:
            return ScanResult(
                tool="trivy",
                passed=False,
                error_message="Trivy not installed. See: https://aquasecurity.github.io/trivy/",
            )
        except Exception as e:
            return ScanResult(tool="trivy", passed=False, error_message=str(e))

    def _map_severity(self, trivy_severity: str) -> Severity:
        mapping = {
            "CRITICAL": Severity.CRITICAL,
            "HIGH": Severity.HIGH,
            "MEDIUM": Severity.MEDIUM,
            "LOW": Severity.LOW,
            "UNKNOWN": Severity.INFO,
        }
        return mapping.get(trivy_severity.upper(), Severity.INFO)


class GitleaksScanner:
    """Gitleaks secrets scanner for repos and history."""

    async def scan(self, repo_path: Path, scan_history: bool = False) -> ScanResult:
        """Run Gitleaks on repository."""
        start = datetime.now(timezone.utc)
        cmd = [
            "gitleaks",
            "detect",
            "--source",
            str(repo_path),
            "--report-format",
            "json",
            "--report-path",
            "/dev/stdout",
            "--verbose",
        ]
        if scan_history:
            cmd.append("--log-opts=--all")  # Scan entire history
        else:
            cmd.append("--staged")  # Only staged changes

        try:
            result = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            stdout, stderr = await result.communicate()
            execution_time = (datetime.now(timezone.utc) - start).total_seconds() * 1000

            # Gitleaks exits 1 if leaks found
            findings = []
            if stdout:
                try:
                    data = json.loads(stdout.decode())
                    for leak in data if isinstance(data, list) else []:
                        finding = SecurityFinding(
                            tool="gitleaks",
                            rule_id=leak.get("RuleID", "secret"),
                            severity=Severity.HIGH,
                            message=f"Secret: {leak.get('Description', 'Detected')}",
                            file_path=leak.get("File"),
                            line_number=leak.get("StartLine"),
                            snippet=leak.get("Match"),
                            metadata={
                                "commit": leak.get("Commit"),
                                "author": leak.get("Author"),
                                "date": leak.get("Date"),
                            },
                        )
                        findings.append(finding)
                except json.JSONDecodeError:
                    pass

            passed = len(findings) == 0
            return ScanResult(
                tool="gitleaks",
                passed=passed,
                findings=findings,
                execution_time_ms=execution_time,
                raw_output=stdout.decode() if stdout else None,
            )
        except FileNotFoundError:
            return ScanResult(
                tool="gitleaks",
                passed=False,
                error_message="Gitleaks not installed. See: https://github.com/gitleaks/gitleaks",
            )
        except Exception as e:
            return ScanResult(tool="gitleaks", passed=False, error_message=str(e))


class OSVScanner:
    """OSV-Scanner for dependency vulnerability checks."""

    async def scan(self, repo_path: Path) -> ScanResult:
        """Run OSV-Scanner on repository."""
        start = datetime.now(timezone.utc)
        cmd = [
            "osv-scanner",
            "scan",
            "--format",
            "json",
            str(repo_path),
        ]

        try:
            result = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            stdout, stderr = await result.communicate()
            execution_time = (datetime.now(timezone.utc) - start).total_seconds() * 1000

            # OSV exits 1 if vulnerabilities found
            findings = []
            if stdout:
                try:
                    data = json.loads(stdout.decode())
                    for result_item in data.get("results", []):
                        for pkg in result_item.get("packages", []):
                            for vuln in pkg.get("vulnerabilities", []):
                                finding = SecurityFinding(
                                    tool="osv-scanner",
                                    rule_id=vuln.get("id", "unknown"),
                                    severity=self._map_severity(
                                        vuln.get("database_specific", {}).get(
                                            "severity", "MODERATE"
                                        )
                                    ),
                                    message=vuln.get("summary", "Vulnerability detected"),
                                    file_path=result_item.get("source", {}).get("path"),
                                    metadata={
                                        "package": pkg.get("package", {}).get("name"),
                                        "version": pkg.get("package", {}).get("version"),
                                        "ecosystem": pkg.get("package", {}).get("ecosystem"),
                                    },
                                )
                                findings.append(finding)
                except json.JSONDecodeError:
                    pass

            passed = not any(f.severity in (Severity.CRITICAL, Severity.HIGH) for f in findings)
            return ScanResult(
                tool="osv-scanner",
                passed=passed,
                findings=findings,
                execution_time_ms=execution_time,
                raw_output=stdout.decode() if stdout else None,
            )
        except FileNotFoundError:
            return ScanResult(
                tool="osv-scanner",
                passed=False,
                error_message="OSV-Scanner not installed. See: https://google.github.io/osv-scanner/",
            )
        except Exception as e:
            return ScanResult(tool="osv-scanner", passed=False, error_message=str(e))

    def _map_severity(self, osv_severity: str) -> Severity:
        mapping = {
            "CRITICAL": Severity.CRITICAL,
            "HIGH": Severity.HIGH,
            "MODERATE": Severity.MEDIUM,
            "LOW": Severity.LOW,
        }
        return mapping.get(osv_severity.upper(), Severity.INFO)


class RuffScanner:
    """Ruff Python linter and formatter."""

    async def scan(self, repo_path: Path) -> ScanResult:
        """Run Ruff check on repository."""
        start = datetime.now(timezone.utc)
        cmd = [
            "ruff",
            "check",
            "--output-format",
            "json",
            str(repo_path),
        ]

        try:
            result = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            stdout, stderr = await result.communicate()
            execution_time = (datetime.now(timezone.utc) - start).total_seconds() * 1000

            findings = []
            if stdout:
                try:
                    data = json.loads(stdout.decode())
                    for item in data:
                        finding = SecurityFinding(
                            tool="ruff",
                            rule_id=item.get("code", "E000"),
                            severity=Severity.LOW,
                            message=item.get("message", ""),
                            file_path=item.get("filename"),
                            line_number=item.get("location", {}).get("row"),
                            column=item.get("location", {}).get("column"),
                            fix=item.get("fix", {}).get("message") if item.get("fix") else None,
                        )
                        findings.append(finding)
                except json.JSONDecodeError:
                    pass

            passed = len(findings) == 0
            return ScanResult(
                tool="ruff",
                passed=passed,
                findings=findings,
                execution_time_ms=execution_time,
            )
        except FileNotFoundError:
            return ScanResult(
                tool="ruff",
                passed=False,
                error_message="Ruff not installed. Install with: pip install ruff",
            )
        except Exception as e:
            return ScanResult(tool="ruff", passed=False, error_message=str(e))


class PyrightScanner:
    """Pyright Python type checker."""

    async def scan(self, repo_path: Path) -> ScanResult:
        """Run Pyright type check on repository."""
        start = datetime.now(timezone.utc)
        cmd = [
            "pyright",
            "--outputjson",
            str(repo_path),
        ]

        try:
            result = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            stdout, stderr = await result.communicate()
            execution_time = (datetime.now(timezone.utc) - start).total_seconds() * 1000

            findings = []
            if stdout:
                try:
                    data = json.loads(stdout.decode())
                    for diagnostic in data.get("generalDiagnostics", []):
                        finding = SecurityFinding(
                            tool="pyright",
                            rule_id=diagnostic.get("rule", "type-error"),
                            severity=Severity.MEDIUM
                            if diagnostic.get("severity") == "error"
                            else Severity.LOW,
                            message=diagnostic.get("message", ""),
                            file_path=diagnostic.get("file"),
                            line_number=diagnostic.get("range", {}).get("start", {}).get("line"),
                            column=diagnostic.get("range", {}).get("start", {}).get("character"),
                        )
                        findings.append(finding)
                except json.JSONDecodeError:
                    pass

            passed = not any(f.severity == Severity.MEDIUM for f in findings)
            return ScanResult(
                tool="pyright",
                passed=passed,
                findings=findings,
                execution_time_ms=execution_time,
            )
        except FileNotFoundError:
            return ScanResult(
                tool="pyright",
                passed=False,
                error_message="Pyright not installed. Install with: pip install pyright",
            )
        except Exception as e:
            return ScanResult(tool="pyright", passed=False, error_message=str(e))


class SecurityVerificationEngine:
    """
    Unified security verification engine.

    Runs all security scanners and produces a deterministic receipt.
    This is the gate that all AI patches must pass through.
    """

    def __init__(
        self,
        enable_semgrep: bool = True,
        enable_trivy: bool = True,
        enable_gitleaks: bool = True,
        enable_osv: bool = True,
        enable_ruff: bool = True,
        enable_pyright: bool = False,  # Optional, slower
    ):
        self.scanners = []
        if enable_semgrep:
            self.scanners.append(SemgrepScanner())
        if enable_trivy:
            self.scanners.append(TrivyScanner())
        if enable_gitleaks:
            self.scanners.append(GitleaksScanner())
        if enable_osv:
            self.scanners.append(OSVScanner())
        if enable_ruff:
            self.scanners.append(RuffScanner())
        if enable_pyright:
            self.scanners.append(PyrightScanner())

    async def verify(
        self,
        repo_path: Path,
        commit_hash: str = None,
        receipt_id: str = None,
    ) -> VerificationReceipt:
        """
        Run full security verification pipeline.

        Args:
            repo_path: Path to repository to scan
            commit_hash: Optional commit hash for receipt
            receipt_id: Optional custom receipt ID

        Returns:
            VerificationReceipt with all findings and overall status

        """
        import uuid

        receipt_id = receipt_id or f"sec-{uuid.uuid4().hex[:12]}"
        start_time = datetime.now(timezone.utc)

        # Run all scanners concurrently
        tasks = [scanner.scan(repo_path) for scanner in self.scanners]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        scan_results = []
        for result in results:
            if isinstance(result, Exception):
                scan_results.append(
                    ScanResult(tool="unknown", passed=False, error_message=str(result))
                )
            else:
                scan_results.append(result)

        # Aggregate statistics
        critical_count = sum(
            1 for r in scan_results for f in r.findings if f.severity == Severity.CRITICAL
        )
        high_count = sum(1 for r in scan_results for f in r.findings if f.severity == Severity.HIGH)
        medium_count = sum(
            1 for r in scan_results for f in r.findings if f.severity == Severity.MEDIUM
        )
        low_count = sum(1 for r in scan_results for f in r.findings if f.severity == Severity.LOW)

        # Determine blocking findings
        blocking_findings = [
            f
            for r in scan_results
            for f in r.findings
            if f.severity in (Severity.CRITICAL, Severity.HIGH)
        ]

        # Overall pass: no critical findings, all scanners ran
        overall_passed = critical_count == 0 and all(
            r.passed or not r.error_message for r in scan_results
        )

        return VerificationReceipt(
            receipt_id=receipt_id,
            timestamp=start_time.isoformat(),
            repository_path=str(repo_path.absolute()),
            commit_hash=commit_hash,
            scan_results=scan_results,
            overall_passed=overall_passed,
            critical_count=critical_count,
            high_count=high_count,
            medium_count=medium_count,
            low_count=low_count,
            blocking_findings=blocking_findings,
        )

    def format_receipt(self, receipt: VerificationReceipt) -> str:
        """Format verification receipt as human-readable report."""
        lines = [
            "╔══════════════════════════════════════════════════════════════╗",
            "║           SECURITY VERIFICATION RECEIPT                      ║",
            "╠══════════════════════════════════════════════════════════════╣",
            f"║ Receipt ID: {receipt.receipt_id:<46} ║",
            f"║ Timestamp:  {receipt.timestamp[:19]:<46} ║",
            f"║ Repository: {receipt.repository_path[-46:]:<46} ║",
            "╠══════════════════════════════════════════════════════════════╣",
            f"║ STATUS: {'PASS ✅' if receipt.overall_passed else 'FAIL ❌':<52} ║",
            "╠══════════════════════════════════════════════════════════════╣",
            "║ Findings Summary:                                            ║",
            f"║   Critical: {receipt.critical_count:<3} │ High: {receipt.high_count:<3} │ Medium: {receipt.medium_count:<3} │ Low: {receipt.low_count:<3}     ║",
            "╠══════════════════════════════════════════════════════════════╣",
        ]

        for result in receipt.scan_results:
            status = "✅" if result.passed else "❌"
            if result.error_message:
                status = "⚠️"
            lines.append(
                f"║ {status} {result.tool:<12} ({len(result.findings):>3} findings, "
                f"{result.execution_time_ms:>5.0f}ms)"
            )

        lines.extend(
            [
                "╠══════════════════════════════════════════════════════════════╣",
                f"║ Blocking Findings: {len(receipt.blocking_findings):<39} ║",
                "╚══════════════════════════════════════════════════════════════╝",
            ]
        )

        return "\n".join(lines)


# Global singleton
_security_engine: SecurityVerificationEngine = None


def get_security_engine() -> SecurityVerificationEngine:
    """Get or create global security verification engine."""
    global _security_engine
    if _security_engine is None:
        _security_engine = SecurityVerificationEngine()
    return _security_engine
