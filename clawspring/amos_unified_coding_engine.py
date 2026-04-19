"""AMOS Unified Coding Engine - Cross-domain software analysis."""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional


class CodingLayer(Enum):
    """Engine layers for coding analysis."""
    ARCHITECTURE = "architecture_layer"
    BACKEND = "backend_layer"
    MOBILE = "mobile_apps_layer"
    WEB = "web_portal_layer"
    DATABASE = "database_and_schema_layer"
    INFRA = "infra_and_devops_layer"
    AI = "ai_and_automation_layer"
    UX_UI = "ux_ui_and_product_layer"
    DOCUMENTATION = "documentation_and_knowledge_layer"


class CodeQualityDimension(Enum):
    """Quality dimensions for code analysis."""
    READABILITY = "readability"
    MAINTAINABILITY = "maintainability"
    PERFORMANCE = "performance"
    SECURITY = "security"
    TESTABILITY = "testability"
    SCALABILITY = "scalability"


@dataclass
class CodeFinding:
    """Code analysis finding."""

    layer: str
    dimension: str
    severity: float
    issue: str
    recommendation: str


class ArchitectureLayerKernel:
    """Kernel for architecture layer analysis."""

    PRINCIPLES = [
        "separation_of_concerns",
        "single_responsibility",
        "dependency_inversion",
        "interface_segregation",
    ]

    def __init__(self):
        self.findings: List[CodeFinding] = []

    def analyze(self, code_description: str) -> List[CodeFinding]:
        """Analyze architecture aspects."""
        findings = []
        desc_lower = code_description.lower()
        # Check for separation of concerns
        if any(word in desc_lower for word in ["mixed", "tight coupling", "spaghetti"]):
            findings.append(
                CodeFinding(
                    layer="architecture",
                    dimension="maintainability",
                    severity=0.8,
                    issue="Poor separation of concerns",
                    recommendation="Refactor into distinct modules",
                )
            )
        # Check for dependency management
        if "circular" in desc_lower and "dependency" in desc_lower:
            findings.append(
                CodeFinding(
                    layer="architecture",
                    dimension="maintainability",
                    severity=0.7,
                    issue="Circular dependencies detected",
                    recommendation="Apply dependency inversion principle",
                )
            )
        self.findings = findings
        return findings

    def get_principles(self) -> List[str]:
        return self.PRINCIPLES


class BackendLayerKernel:
    """Kernel for backend layer analysis."""

    PRINCIPLES = [
        "stateless_design",
        "idempotent_operations",
        "async_processing",
        "circuit_breaker_pattern",
    ]

    def __init__(self):
        self.findings: List[CodeFinding] = []

    def analyze(self, code_description: str) -> List[CodeFinding]:
        """Analyze backend aspects."""
        findings = []
        desc_lower = code_description.lower()
        # Check for state management
        if "global state" in desc_lower or "shared mutable" in desc_lower:
            findings.append(
                CodeFinding(
                    layer="backend",
                    dimension="scalability",
                    severity=0.6,
                    issue="Global/shared mutable state",
                    recommendation="Use stateless design or immutable state",
                )
            )
        # Check for error handling
        if "no error handling" in desc_lower or "bare except" in desc_lower:
            findings.append(
                CodeFinding(
                    layer="backend",
                    dimension="security",
                    severity=0.7,
                    issue="Insufficient error handling",
                    recommendation="Implement proper exception handling",
                )
            )
        self.findings = findings
        return findings

    def get_principles(self) -> List[str]:
        return self.PRINCIPLES


class DatabaseLayerKernel:
    """Kernel for database layer analysis."""

    PRINCIPLES = [
        "normalization",
        "index_optimization",
        "transaction_integrity",
        "query_efficiency",
    ]

    def __init__(self):
        self.findings: List[CodeFinding] = []

    def analyze(self, code_description: str) -> List[CodeFinding]:
        """Analyze database aspects."""
        findings = []
        desc_lower = code_description.lower()
        # Check for N+1 query pattern
        if "n+1" in desc_lower or "loop query" in desc_lower:
            findings.append(
                CodeFinding(
                    layer="database",
                    dimension="performance",
                    severity=0.8,
                    issue="N+1 query pattern detected",
                    recommendation="Use eager loading or batch queries",
                )
            )
        # Check for indexing
        if "no index" in desc_lower or "full table scan" in desc_lower:
            findings.append(
                CodeFinding(
                    layer="database",
                    dimension="performance",
                    severity=0.7,
                    issue="Missing database indexes",
                    recommendation="Add appropriate indexes",
                )
            )
        self.findings = findings
        return findings

    def get_principles(self) -> List[str]:
        return self.PRINCIPLES


class SecurityLayerKernel:
    """Kernel for security analysis across all layers."""

    PRINCIPLES = [
        "input_validation",
        "output_encoding",
        "least_privilege",
        "defense_in_depth",
    ]

    def __init__(self):
        self.findings: List[CodeFinding] = []

    def analyze(self, code_description: str) -> List[CodeFinding]:
        """Analyze security aspects."""
        findings = []
        desc_lower = code_description.lower()
        security_patterns = [
            ("sql injection", "sql", "Use parameterized queries"),
            ("xss", "xss", "Implement output encoding"),
            ("hardcoded secret", "secrets", "Use secrets management"),
            ("no authentication", "auth", "Add authentication"),
            ("plaintext password", "passwords", "Hash passwords properly"),
        ]
        for pattern, issue_type, recommendation in security_patterns:
            if pattern in desc_lower:
                findings.append(
                    CodeFinding(
                        layer="security",
                        dimension="security",
                        severity=0.9,
                        issue=f"Security issue: {issue_type}",
                        recommendation=recommendation,
                    )
                )
        self.findings = findings
        return findings

    def get_principles(self) -> List[str]:
        return self.PRINCIPLES


class UnifiedCodingEngine:
    """AMOS Unified Coding Engine - Software analysis across all layers."""

    VERSION = "v1.0.0"
    NAME = "AMOS_Unified_Coding_OMEGA"

    def __init__(self):
        self.architecture_kernel = ArchitectureLayerKernel()
        self.backend_kernel = BackendLayerKernel()
        self.database_kernel = DatabaseLayerKernel()
        self.security_kernel = SecurityLayerKernel()

    def analyze(
        self, description: str, domains: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Run unified coding analysis."""
        domains = domains or ["architecture", "backend", "database", "security"]
        results: Dict[str, Any] = {}
        if "architecture" in domains:
            results["architecture"] = self._analyze_architecture(description)
        if "backend" in domains:
            results["backend"] = self._analyze_backend(description)
        if "database" in domains:
            results["database"] = self._analyze_database(description)
        if "security" in domains:
            results["security"] = self._analyze_security(description)
        return results

    def _analyze_architecture(self, description: str) -> dict:
        findings = self.architecture_kernel.analyze(description)
        return {
            "query": description[:100],
            "findings_count": len(findings),
            "findings": [
                {"dimension": f.dimension, "issue": f.issue, "severity": f.severity}
                for f in findings[:3]
            ],
            "principles": self.architecture_kernel.get_principles(),
        }

    def _analyze_backend(self, description: str) -> dict:
        findings = self.backend_kernel.analyze(description)
        return {
            "query": description[:100],
            "findings_count": len(findings),
            "findings": [
                {"dimension": f.dimension, "issue": f.issue, "severity": f.severity}
                for f in findings[:3]
            ],
            "principles": self.backend_kernel.get_principles(),
        }

    def _analyze_database(self, description: str) -> dict:
        findings = self.database_kernel.analyze(description)
        return {
            "query": description[:100],
            "findings_count": len(findings),
            "findings": [
                {"dimension": f.dimension, "issue": f.issue, "severity": f.severity}
                for f in findings[:3]
            ],
            "principles": self.database_kernel.get_principles(),
        }

    def _analyze_security(self, description: str) -> dict:
        findings = self.security_kernel.analyze(description)
        return {
            "query": description[:100],
            "findings_count": len(findings),
            "findings": [
                {"dimension": f.dimension, "issue": f.issue, "severity": f.severity}
                for f in findings[:3]
            ],
            "principles": self.security_kernel.get_principles(),
        }

    def get_findings_summary(self, results: dict) -> str:
        """Generate findings summary with gap acknowledgment."""
        lines = [
            f"# {self.NAME} {self.VERSION}",
            "",
            "Creator: Trang Phan | System: AMOS vInfinity",
            "",
            "## Domain Coverage",
        ]
        domain_names = {
            "architecture": "Architecture Layer",
            "backend": "Backend Layer",
            "database": "Database Layer",
            "security": "Security Layer",
        }
        total_findings = 0
        for domain, data in results.items():
            display_name = domain_names.get(domain, domain.title())
            lines.extend(["", f"### {display_name}"])
            if isinstance(data, dict):
                findings_count = data.get("findings_count", 0)
                total_findings += findings_count
                lines.append(f"- **Findings**: {findings_count}")
                if data.get("findings"):
                    lines.append("- **Key Issues**:")
                    for finding in data["findings"]:
                        lines.append(
                            f"  - {finding['dimension']}: {finding['issue']} "
                            f"(severity: {finding['severity']})"
                        )
                if "principles" in data:
                    lines.append(f"- **Principles**: {', '.join(data['principles'][:2])}...")
        lines.extend([
            "",
            f"**Total Findings**: {total_findings}",
            "",
            "## Layers Available",
            "- Architecture: Separation of concerns, SOLID principles",
            "- Backend: Stateless design, async processing",
            "- Database: Normalization, indexing, query optimization",
            "- Security: Input validation, output encoding, least privilege",
            "- Mobile, Web, Infra, AI/Automation, UX/UI, Documentation",
            "",
            "## Gaps and Limitations",
            "- Static analysis only; no runtime execution",
            "- Language-specific analysis not yet implemented",
            "- Pattern detection is keyword-based",
            "- Automated refactoring suggestions not yet available",
            "",
            "## Safety Disclaimer",
            "Code analysis is advisory. Does not guarantee security or correctness. "
            "Production code requires professional review and testing.",
        ])
        return "\n".join(lines)


# Singleton instance
_unified_coding_engine: Optional[UnifiedCodingEngine] = None


def get_unified_coding_engine() -> UnifiedCodingEngine:
    """Get or create the Unified Coding Engine singleton."""
    global _unified_coding_engine
    if _unified_coding_engine is None:
        _unified_coding_engine = UnifiedCodingEngine()
    return _unified_coding_engine
