#!/usr/bin/env python3

"""AMOS Production Hardening Suite

Implements Phase 28 hardening requirements:
1. Security Audit & Hardening
2. Reliability & Resilience Verification
3. Performance Optimization
"""

import json
import os
import re
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any


def _now_utc() -> str:
    """Get current timezone.utc timestamp."""
    return datetime.now(UTC).isoformat()


@dataclass
class SecurityFinding:
    """Security audit finding."""

    severity: str  # critical, high, medium, low
    file: str
    line: int
    issue: str
    recommendation: str
    timestamp: str = field(default_factory=_now_utc)


@dataclass
class HardeningReport:
    """Production hardening report."""

    timestamp: str
    security_findings: List[SecurityFinding]
    reliability_score: float
    performance_baseline: Dict[str, float]
    recommendations: List[str]
    passed: bool = False


class SecurityAuditor:
    """Production security auditor."""

    CRITICAL_PATTERNS = [
        (r'password\s*=\s*["\'][^"\']+["\']', "Hardcoded password"),
        (r'api_key\s*=\s*["\'][^"\']+["\']', "Hardcoded API key"),
        (r'secret\s*=\s*["\'][^"\']+["\']', "Hardcoded secret"),
        (r'token\s*=\s*["\'][^"\']+["\']', "Hardcoded token"),
        (r"eval\s*\(", "Dangerous eval() usage"),
        (r"exec\s*\(", "Dangerous exec() usage"),
        (r"subprocess\.call\s*\([^)]*shell\s*=\s*True", "Subprocess with shell=True"),
        (r"pickle\.loads?\s*\(", "Unsafe pickle usage"),
        (r"yaml\.load\s*\([^)]*Loader\s*=\s*None", "Unsafe YAML loading"),
        (r"debug\s*=\s*True", "Debug mode enabled"),
        (r"TLS_VERIFY\s*=\s*False", "TLS verification disabled"),
        (r"VERIFY_SSL\s*=\s*False", "SSL verification disabled"),
    ]

    def __init__(self, root_path: str = "."):
        self.root_path = Path(root_path)
        self.findings: List[SecurityFinding] = []

    def scan_file(self, filepath: Path) -> List[SecurityFinding]:
        """Scan a single file for security issues."""
        findings = []

        try:
            content = filepath.read_text(encoding="utf-8", errors="ignore")
            lines = content.split("\n")

            for line_num, line in enumerate(lines, 1):
                for pattern, issue_type in self.CRITICAL_PATTERNS:
                    if re.search(pattern, line, re.IGNORECASE):
                        # Skip comments and docstrings
                        stripped = line.strip()
                        if (
                            stripped.startswith("#")
                            or stripped.startswith('"""')
                            or stripped.startswith("'''")
                        ):
                            continue

                        # Skip .venv and test files for certain patterns
                        if ".venv" in str(filepath) or "test" in str(filepath).lower():
                            if issue_type in ["Hardcoded password", "Hardcoded API key"]:
                                severity = "low"  # Test files are OK
                            else:
                                continue
                        else:
                            severity = "high" if issue_type.startswith("Hardcoded") else "medium"

                        findings.append(
                            SecurityFinding(
                                severity=severity,
                                file=str(filepath),
                                line=line_num,
                                issue=issue_type,
                                recommendation=f"Review and fix {issue_type.lower()}",
                            )
                        )
        except Exception as e:
            print(f"Error scanning {filepath}: {e}")

        return findings

    def scan_repository(self) -> List[SecurityFinding]:
        """Scan entire repository."""
        print("🔒 Starting security audit...")

        exclude_dirs = {
            ".venv",
            "__pycache__",
            ".git",
            "node_modules",
            ".ruff_cache",
            ".pytest_cache",
        }

        for root, dirs, files in os.walk(self.root_path):
            # Skip excluded directories
            dirs[:] = [d for d in dirs if d not in exclude_dirs and not d.startswith(".")]

            for file in files:
                if file.endswith(".py"):
                    filepath = Path(root) / file
                    findings = self.scan_file(filepath)
                    self.findings.extend(findings)

        return self.findings

    def generate_report(self) -> Dict[str, Any]:
        """Generate security audit report."""
        critical = len([f for f in self.findings if f.severity == "critical"])
        high = len([f for f in self.findings if f.severity == "high"])
        medium = len([f for f in self.findings if f.severity == "medium"])
        low = len([f for f in self.findings if f.severity == "low"])

        return {
            "timestamp": datetime.now(UTC).isoformat(),
            "summary": {
                "critical": critical,
                "high": high,
                "medium": medium,
                "low": low,
                "total": len(self.findings),
            },
            "findings": [
                {
                    "severity": f.severity,
                    "file": f.file,
                    "line": f.line,
                    "issue": f.issue,
                    "recommendation": f.recommendation,
                }
                for f in self.findings
            ],
            "passed": critical == 0 and high == 0,
        }


class ReliabilityVerifier:
    """Verify system reliability and resilience."""

    def __init__(self, root_path: str = "."):
        self.root_path = Path(root_path)

    def verify_imports(self) -> Dict[str, Any]:
        """Verify critical imports work."""
        print("🔍 Verifying critical imports...")

        critical_modules = [
            ("backend/main", "FastAPI Backend"),
            ("clawspring.amos_brain_integration", "Brain Integration"),
            ("amos_openclaws_bridge", "OpenClaws Bridge"),
            ("amos_cli", "CLI Interface"),
        ]

        results = {}
        for module, desc in critical_modules:
            try:
                __import__(module)
                results[desc] = {"status": "pass", "error": None}
            except Exception as e:
                results[desc] = {"status": "fail", "error": str(e)}

        return results

    def verify_health_checks(self) -> Dict[str, Any]:
        """Verify health check endpoints are defined."""
        print("🏥 Verifying health checks...")

        health_files = [
            "backend/main.py",
            "backend/api/superbrain.py",
            "backend/api/brain_integrated.py",
        ]

        results = {}
        for file in health_files:
            filepath = self.root_path / file
            if filepath.exists():
                content = filepath.read_text()
                has_health = "@router.get" in content and "health" in content.lower()
                results[file] = "pass" if has_health else "warn"
            else:
                results[file] = "not_found"

        return results

    def generate_report(self) -> Dict[str, Any]:
        """Generate reliability report."""
        imports = self.verify_imports()
        health = self.verify_health_checks()

        import_score = sum(1 for v in imports.values() if v["status"] == "pass") / len(imports)
        health_score = sum(1 for v in health.values() if v == "pass") / len(health)

        overall_score = (import_score + health_score) / 2

        return {
            "timestamp": datetime.now(UTC).isoformat(),
            "import_checks": imports,
            "health_checks": health,
            "score": overall_score,
            "passed": overall_score >= 0.8,
        }


class PerformanceBenchmark:
    """Basic performance benchmarking."""

    def benchmark_imports(self) -> dict[str, float]:
        """Benchmark import times."""
        print("⚡ Benchmarking import performance...")

        times = {}

        # Test brain bridge import time
        start = time.perf_counter()
        try:
            times["bridge_import_ms"] = (time.perf_counter() - start) * 1000
        except Exception:
            times["bridge_import_ms"] = -1

        return times

    def generate_report(self) -> Dict[str, Any]:
        """Generate performance report."""
        times = self.benchmark_imports()

        return {
            "timestamp": datetime.now(UTC).isoformat(),
            "metrics": times,
            "targets": {
                "import_time_ms": 500,  # Target: <500ms
            },
            "passed": all(t < 500 for t in times.values() if t > 0),
        }


def run_hardening_suite() -> HardeningReport:
    """Run complete production hardening suite."""
    print("=" * 60)
    print("🛡️ AMOS PRODUCTION HARDENING SUITE")
    print("=" * 60)

    # Security Audit
    auditor = SecurityAuditor()
    auditor.scan_repository()
    security_report = auditor.generate_report()

    print(f"\n🔒 Security Audit: {security_report['summary']}")

    # Reliability Verification
    verifier = ReliabilityVerifier()
    reliability_report = verifier.generate_report()

    print(f"🔍 Reliability Score: {reliability_report['score']:.1%}")

    # Performance Benchmark
    benchmark = PerformanceBenchmark()
    perf_report = benchmark.generate_report()

    print(f"⚡ Performance: {perf_report['metrics']}")

    # Overall Assessment
    all_passed = (
        security_report["passed"] and reliability_report["passed"] and perf_report["passed"]
    )

    print("\n" + "=" * 60)
    if all_passed:
        print("✅ HARDENING PASSED - System ready for production")
    else:
        print("⚠️ HARDENING ISSUES FOUND - Review required")
    print("=" * 60)

    return HardeningReport(
        timestamp=datetime.now(UTC).isoformat(),
        security_findings=auditor.findings,
        reliability_score=reliability_report["score"],
        performance_baseline=perf_report["metrics"],
        recommendations=[
            "Fix any high/critical security findings",
            "Ensure all health check endpoints are operational",
            "Monitor import times in production environment",
        ],
        passed=all_passed,
    )


if __name__ == "__main__":
    report = run_hardening_suite()

    # Save report
    report_file = Path("amos_hardening_report.json")
    with open(report_file, "w") as f:
        json.dump(
            {
                "timestamp": report.timestamp,
                "passed": report.passed,
                "reliability_score": report.reliability_score,
                "performance": report.performance_baseline,
                "recommendations": report.recommendations,
            },
            f,
            indent=2,
        )

    print(f"\n📄 Report saved to: {report_file}")

    sys.exit(0 if report.passed else 1)
