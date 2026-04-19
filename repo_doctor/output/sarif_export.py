"""
Repo Doctor Ω∞ - SARIF Export

Export diagnostics to SARIF format (Static Analysis Results Interchange Format).
This enables integration with:
- GitHub Security dashboard
- Azure DevOps
- VS Code problem panel
- Third-party security platforms

SARIF 2.1.0 specification compliant.
"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from ..state.basis import StateDimension


@dataclass
class SarifLocation:
    """SARIF physical location."""

    file_path: str
    line: int = 1
    column: int = 1

    def to_dict(self) -> Dict[str, Any]:
        return {
            "physicalLocation": {
                "artifactLocation": {"uri": self.file_path},
                "region": {
                    "startLine": self.line,
                    "startColumn": self.column,
                },
            }
        }


@dataclass
class SarifResult:
    """Single SARIF result (finding)."""

    rule_id: str
    message: str
    level: str  # error, warning, note
    locations: List[SarifLocation] = field(default_factory=list)
    properties: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ruleId": self.rule_id,
            "message": {"text": self.message},
            "level": self.level,
            "locations": [loc.to_dict() for loc in self.locations],
            "properties": self.properties,
        }


class SarifExporter:
    """
    Export Repo Doctor results to SARIF format.
    """

    # Map StateDimension to SARIF rule IDs
    RULE_MAP: dict[StateDimension, str] = {
        StateDimension.SYNTAX: "REPO001",
        StateDimension.IMPORTS: "REPO002",
        StateDimension.TYPES: "REPO003",
        StateDimension.API: "REPO004",
        StateDimension.ENTRYPOINTS: "REPO005",
        StateDimension.PACKAGING: "REPO006",
        StateDimension.RUNTIME: "REPO007",
        StateDimension.PERSISTENCE: "REPO008",
        StateDimension.STATUS: "REPO009",
        StateDimension.SECURITY: "REPO010",
        StateDimension.DOCS_TESTS_DEMOS: "REPO011",
        StateDimension.HISTORY: "REPO012",
    }

    # Rule metadata
    RULES: dict[str, dict[str, Any]] = {
        "REPO001": {
            "name": "SyntaxIntegrity",
            "shortDescription": {"text": "Source file syntax integrity"},
            "fullDescription": {"text": "All source files must parse without fatal errors"},
            "defaultConfiguration": {"level": "error"},
        },
        "REPO002": {
            "name": "ImportResolution",
            "shortDescription": {"text": "Import resolution integrity"},
            "fullDescription": {"text": "All imports must resolve to real symbols"},
            "defaultConfiguration": {"level": "error"},
        },
        "REPO004": {
            "name": "APIContract",
            "shortDescription": {"text": "API contract integrity"},
            "fullDescription": {"text": "Public API must match runtime reality"},
            "defaultConfiguration": {"level": "error"},
        },
        "REPO005": {
            "name": "EntrypointIntegrity",
            "shortDescription": {"text": "Entrypoint integrity"},
            "fullDescription": {"text": "All entrypoints must point to valid targets"},
            "defaultConfiguration": {"level": "error"},
        },
        "REPO010": {
            "name": "SecurityViolation",
            "shortDescription": {"text": "Security violation detected"},
            "fullDescription": {"text": "Security invariant must not be violated"},
            "defaultConfiguration": {"level": "error"},
        },
    }

    def __init__(self, tool_name: str = "RepoDoctorOmega"):
        self.tool_name = tool_name
        self.results: List[SarifResult] = []

    def add_finding(
        self,
        dimension: StateDimension,
        message: str,
        file_path: str = "",
        line: int = 1,
        level: str = "error",
        properties: Dict[str, Any] = None,
    ) -> None:
        """Add a SARIF finding."""
        rule_id = self.RULE_MAP.get(dimension, "REPO000")

        locations = []
        if file_path:
            locations.append(SarifLocation(file_path, line))

        result = SarifResult(
            rule_id=rule_id,
            message=message,
            level=level,
            locations=locations,
            properties=properties or {},
        )
        self.results.append(result)

    def export(self, output_path: Optional[Path] = None) -> Dict[str, Any]:
        """
        Generate SARIF report.
        """
        sarif_doc = {
            "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
            "version": "2.1.0",
            "runs": [
                {
                    "tool": {
                        "driver": {
                            "name": self.tool_name,
                            "informationUri": "https://github.com/trangyp/AMOS-code",
                            "version": "0.1.0",
                            "rules": [
                                {
                                    "id": rule_id,
                                    **rule_data,
                                }
                                for rule_id, rule_data in self.RULES.items()
                            ],
                        }
                    },
                    "results": [r.to_dict() for r in self.results],
                    "invocations": [
                        {
                            "executionSuccessful": True,
                            "startTimeUtc": datetime.now().isoformat(),
                        }
                    ],
                    "properties": {
                        "repoDoctor": {
                            "version": "0.1.0",
                            "quantumModel": True,
                            "hamiltonianEnabled": True,
                        }
                    },
                }
            ],
        }

        if output_path:
            with open(output_path, "w") as f:
                json.dump(sarif_doc, f, indent=2)

        return sarif_doc

    def from_diagnosis(self, diagnosis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert Repo Doctor diagnosis to SARIF.
        """
        # Add findings for failed invariants
        failed = diagnosis.get("invariants", {}).get("failed", [])
        for inv in failed:
            self.add_finding(
                dimension=StateDimension.API,  # Default to API
                message=f"Invariant failed: {inv}",
                level="error",
            )

        # Add findings for low amplitudes
        amplitudes = diagnosis.get("state_vector", {})
        for dim_name, amp in amplitudes.items():
            if amp < 0.5:
                # Find corresponding dimension
                for dim in StateDimension:
                    if dim.value == dim_name and amp < 0.8:
                        self.add_finding(
                            dimension=dim,
                            message=f"Subsystem degraded: {dim_name} = {amp:.2f}",
                            level="warning" if amp > 0.5 else "error",
                            properties={"amplitude": amp},
                        )

        return self.export()
