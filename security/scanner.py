"""AMOS Equation System - Security Scanner.

Comprehensive security scanning: SAST, dependencies, secrets, containers.
Integrates with CI/CD for automated security gates.

Usage:
    python security/scanner.py --all
    python security/scanner.py --sast --path ./app
    python security/scanner.py --dependencies
    python security/scanner.py --secrets

Author: AMOS Security Team
Version: 2.0.0
"""

import argparse
import json
import re
import subprocess
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List


@dataclass
class SecurityFinding:
    """Security scan finding."""

    severity: str  # critical, high, medium, low, info
    category: str  # sast, dependency, secret, container
    rule_id: str
    message: str
    file: str
    line: int
    remediation: str


@dataclass
class ScanReport:
    """Complete security scan report."""

    timestamp: str
    scan_types: List[str]
    findings: List[SecurityFinding]
    summary: Dict[str, int]
    passed: bool


class SecurityScanner:
    """Multi-layer security scanner."""

    # High-entropy secret patterns
    SECRET_PATTERNS = [  # nosec: B105 - These are detection patterns, not actual secrets
        (r"AWS_SECRET_ACCESS_KEY\s*=\s*['\"]([A-Za-z0-9/+=]{40})['\"]", "AWS Secret Key"),
        (r"PRIVATE_KEY.*BEGIN", "Private Key"),
        (r"password\s*=\s*['\"][^'\"]{8,}['\"]", "Hardcoded Password"),
        (r"api[_-]?key\s*=\s*['\"][A-Za-z0-9]{32,}['\"]", "API Key"),
        (r"token\s*=\s*['\"][A-Za-z0-9_-]{20,}['\"]", "Token"),
        (r"postgres://[^:]+:[^@]+@", "Database URL with Password"),
    ]  # nosec

    # Insecure code patterns
    INSECURE_PATTERNS = [
        (r"eval\s*\(", "eval() usage - dangerous"),
        (r"exec\s*\(", "exec() usage - dangerous"),
        (r"subprocess\.call.*shell\s*=\s*True", "Shell=True in subprocess"),
        (r"pickle\.loads?\s*\(", "Unsafe pickle deserialization"),
        (r"yaml\.load\s*\([^)]*\)", "Unsafe YAML load"),
        (r"md5\s*\(", "Weak hash algorithm MD5"),
        (r"sha1\s*\(", "Weak hash algorithm SHA1"),
        (r"random\.\w+\s*\(", "Insecure random for crypto"),
        (r"DEBUG\s*=\s*True", "Debug mode enabled"),
        (r"VERIFY_SSL\s*=\s*False", "SSL verification disabled"),
    ]

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.findings: List[SecurityFinding] = []

    # Files containing detection patterns that should be excluded from scanning
    SCANNER_FILES = {
        "security/scanner.py",
        "amos_deep_system_scanner.py",
        "amos_universal_system_scanner.py",
    }

    def scan_secrets(self) -> List[SecurityFinding]:
        """Scan for hardcoded secrets."""
        findings = []

        for file_path in self.project_root.rglob("*.py"):
            if ".venv" in str(file_path) or "__pycache__" in str(file_path):
                continue

            # Skip scanner files that contain detection patterns (not actual secrets)
            relative_path = str(file_path.relative_to(self.project_root))
            if any(scanner_file in relative_path for scanner_file in self.SCANNER_FILES):
                continue

            try:
                content = file_path.read_text()
                lines = content.split("\n")

                for line_num, line in enumerate(lines, 1):
                    for pattern, desc in self.SECRET_PATTERNS:
                        if re.search(pattern, line, re.IGNORECASE):
                            findings.append(
                                SecurityFinding(
                                    severity="critical",
                                    category="secret",
                                    rule_id="HARDCODED_SECRET",
                                    message=f"Potential {desc} detected",
                                    file=str(file_path.relative_to(self.project_root)),
                                    line=line_num,
                                    remediation="Use environment variables or secret management (AWS Secrets Manager, etc.)",
                                )
                            )
            except Exception:
                continue

        return findings

    def scan_sast(self) -> List[SecurityFinding]:
        """Static application security testing."""
        findings = []

        for file_path in self.project_root.rglob("*.py"):
            if ".venv" in str(file_path) or "__pycache__" in str(file_path):
                continue

            # Skip scanner files that contain detection patterns (not actual secrets)
            relative_path = str(file_path.relative_to(self.project_root))
            if any(scanner_file in relative_path for scanner_file in self.SCANNER_FILES):
                continue

            try:
                content = file_path.read_text()
                lines = content.split("\n")

                for line_num, line in enumerate(lines, 1):
                    for pattern, desc in self.INSECURE_PATTERNS:
                        if re.search(pattern, line):
                            severity = "high" if "dangerous" in desc else "medium"
                            findings.append(
                                SecurityFinding(
                                    severity=severity,
                                    category="sast",
                                    rule_id="INSECURE_PATTERN",
                                    message=desc,
                                    file=str(file_path.relative_to(self.project_root)),
                                    line=line_num,
                                    remediation="Review and replace with secure alternative",
                                )
                            )
            except Exception:
                continue

        return findings

    def scan_dependencies(self) -> List[SecurityFinding]:
        """Check for vulnerable dependencies."""
        findings = []

        # Run safety check if available
        try:
            result = subprocess.run(
                ["safety", "check", "--json"], capture_output=True, text=True, timeout=60
            )

            if result.returncode == 0:
                vulnerabilities = json.loads(result.stdout)
                for vuln in vulnerabilities.get("vulnerabilities", []):
                    findings.append(
                        SecurityFinding(
                            severity="high" if vuln.get("severity") == "critical" else "medium",
                            category="dependency",
                            rule_id=f"VULN-{vuln.get('vulnerability_id', 'UNKNOWN')}",
                            message=f"{vuln.get('package_name')} {vuln.get('vulnerable_spec')} - {vuln.get('advisory')}",
                            file="requirements.txt",
                            line=None,
                            remediation=f"Upgrade to {vuln.get('fixed_versions', 'latest')}",
                        )
                    )
        except (subprocess.TimeoutExpired, FileNotFoundError):
            # Fallback: basic checks
            findings.append(
                SecurityFinding(
                    severity="info",
                    category="dependency",
                    rule_id="MANUAL_CHECK",
                    message="Install 'safety' for comprehensive dependency scanning: pip install safety",
                    file=None,
                    line=None,
                    remediation="Run: safety check",
                )
            )

        # Check for outdated packages
        try:
            result = subprocess.run(
                ["pip", "list", "--outdated", "--format=json"],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0:
                outdated = json.loads(result.stdout)
                for pkg in outdated[:5]:  # Limit to top 5
                    findings.append(
                        SecurityFinding(
                            severity="low",
                            category="dependency",
                            rule_id="OUTDATED_PACKAGE",
                            message=f"{pkg['name']} {pkg['version']} -> {pkg['latest_version']}",
                            file="requirements.txt",
                            line=None,
                            remediation=f"Update to {pkg['latest_version']}",
                        )
                    )
        except Exception:
            pass

        return findings

    def scan_containers(self) -> List[SecurityFinding]:
        """Container image security scan."""
        findings = []

        dockerfile = self.project_root / "Dockerfile"
        if not dockerfile.exists():
            return findings

        content = dockerfile.read_text()
        lines = content.split("\n")

        # Check for security best practices
        checks = [
            (r"^FROM\s+.*:latest", "Using 'latest' tag - not reproducible", "medium"),
            (r"USER\s+root", "Running as root user", "high"),
            (r"apt-get\s+update.*&&.*apt-get\s+install", "Package update without cleanup", "low"),
            (r"pip\s+install.*--no-cache-dir", "Missing --no-cache-dir", "info"),
            (r"curl.*\|.*sh", "Piping curl to shell - dangerous", "critical"),
            (r"wget.*\|.*sh", "Piping wget to shell - dangerous", "critical"),
        ]

        for line_num, line in enumerate(lines, 1):
            for pattern, message, severity in checks:
                if re.search(pattern, line, re.IGNORECASE):
                    findings.append(
                        SecurityFinding(
                            severity=severity,
                            category="container",
                            rule_id="CONTAINER_SECURITY",
                            message=message,
                            file="Dockerfile",
                            line=line_num,
                            remediation="Review Dockerfile security best practices",
                        )
                    )

        # Check if USER directive exists
        if "USER" not in content:
            findings.append(
                SecurityFinding(
                    severity="high",
                    category="container",
                    rule_id="NO_USER_DIRECTIVE",
                    message="No USER directive - container runs as root",
                    file="Dockerfile",
                    line=None,
                    remediation="Add 'USER nonroot' directive",
                )
            )

        return findings

    def generate_report(self, scan_types: List[str]) -> ScanReport:
        """Generate comprehensive scan report."""
        all_findings = []

        if "secrets" in scan_types:
            all_findings.extend(self.scan_secrets())

        if "sast" in scan_types:
            all_findings.extend(self.scan_sast())

        if "dependencies" in scan_types:
            all_findings.extend(self.scan_dependencies())

        if "containers" in scan_types:
            all_findings.extend(self.scan_containers())

        # Calculate summary
        summary = {"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0}
        for finding in all_findings:
            summary[finding.severity] = summary.get(finding.severity, 0) + 1

        # Pass if no critical/high findings
        passed = summary["critical"] == 0 and summary["high"] == 0

        return ScanReport(
            timestamp=datetime.now().isoformat(),
            scan_types=scan_types,
            findings=all_findings,
            summary=summary,
            passed=passed,
        )


def print_report(report: ScanReport):
    """Print security report."""
    print("\n" + "=" * 70)
    print("AMOS SECURITY SCAN REPORT")
    print("=" * 70)
    print(f"Timestamp: {report.timestamp}")
    print(f"Scan Types: {', '.join(report.scan_types)}")
    print(f"Status: {'PASS' if report.passed else 'FAIL'}")

    print("\nSummary:")
    for severity, count in report.summary.items():
        if count > 0:
            icon = {"critical": "", "high": "", "medium": "", "low": "", "info": ""}.get(
                severity, ""
            )
            print(f"  {icon} {severity.upper():10} {count:3} findings")

    if report.findings:
        print("\nDetailed Findings:")
        print("-" * 70)

        # Sort by severity
        severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}
        sorted_findings = sorted(report.findings, key=lambda f: severity_order.get(f.severity, 5))

        for finding in sorted_findings:
            location = f"{finding.file}:{finding.line}" if finding.line else finding.file
            print(f"\n[{finding.severity.upper()}] {finding.rule_id}")
            print(f"  Category: {finding.category}")
            print(f"  Message: {finding.message}")
            if location:
                print(f"  Location: {location}")
            print(f"  Fix: {finding.remediation}")

    print("\n" + "=" * 70)


def main():
    parser = argparse.ArgumentParser(description="AMOS Security Scanner")
    parser.add_argument("--all", action="store_true", help="Run all scans")
    parser.add_argument("--sast", action="store_true", help="Static code analysis")
    parser.add_argument("--secrets", action="store_true", help="Secret detection")
    parser.add_argument("--dependencies", action="store_true", help="Dependency check")
    parser.add_argument("--containers", action="store_true", help="Container scan")
    parser.add_argument("--path", default=".", help="Project root path")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument(
        "--fail-on",
        choices=["critical", "high", "medium"],
        default="high",
        help="Exit with error if findings at this level",
    )

    args = parser.parse_args()

    # Determine scan types
    if args.all:
        scan_types = ["secrets", "sast", "dependencies", "containers"]
    else:
        scan_types = []
        if args.secrets:
            scan_types.append("secrets")
        if args.sast:
            scan_types.append("sast")
        if args.dependencies:
            scan_types.append("dependencies")
        if args.containers:
            scan_types.append("containers")

    if not scan_types:
        scan_types = ["secrets", "sast"]  # Default

    # Run scan
    scanner = SecurityScanner(args.path)
    report = scanner.generate_report(scan_types)

    # Output
    if args.json:
        print(json.dumps(asdict(report), indent=2))
    else:
        print_report(report)

    # Exit code based on severity
    severity_levels = {"critical": 0, "high": 0, "medium": 0}
    for finding in report.findings:
        severity_levels[finding.severity] = severity_levels.get(finding.severity, 0) + 1

    if args.fail_on == "critical" and severity_levels["critical"] > 0:
        exit(1)
    elif args.fail_on == "high" and (
        severity_levels["critical"] > 0 or severity_levels["high"] > 0
    ):
        exit(1)
    elif args.fail_on == "medium" and any(c > 0 for c in severity_levels.values()):
        exit(1)

    exit(0 if report.passed else 1)


if __name__ == "__main__":
    main()
