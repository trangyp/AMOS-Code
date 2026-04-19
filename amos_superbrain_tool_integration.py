#!/usr/bin/env python3
"""
AMOS SuperBrain Equation Tool Integration
Connects the 41-domain equation system to AMOS tool ecosystem.

Provides:
- Tool interface for equation execution via AMOS tools
- Audit trail integration for equation executions
- Dashboard data export for visualization
- Cross-domain pattern analysis as a service

Architecture:
- Integrates with amos_tools.py tool registry
- Exports to audit_exporter.py for governance
- Feeds unified_dashboard.html with equation metrics

Version: 8.1.0-PHASE15
Author: AMOS SuperBrain
"""


import json
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

# SuperBrain integration
try:
    from amos_brain import get_super_brain
    SUPERBRAIN_AVAILABLE = True
except ImportError:
    SUPERBRAIN_AVAILABLE = False

# Equation bridge integration
try:
    from amos_superbrain_equation_bridge import (
        AMOSSuperBrainBridge,
        Domain,
        MathematicalPattern,
        ExecutionResult
    )
    BRIDGE_AVAILABLE = True
except ImportError:
    BRIDGE_AVAILABLE = False
    Domain = None  # type: ignore
    AMOSSuperBrainBridge = None  # type: ignore
    MathematicalPattern = None  # type: ignore
    ExecutionResult = None  # type: ignore

# Audit integration
try:
    from clawspring.amos_brain.audit_exporter import AuditExporter
    AUDIT_AVAILABLE = True
except ImportError:
    AUDIT_AVAILABLE = False

# Mathematical Framework Integration
try:
    from clawspring.amos_brain.mathematical_framework_engine import (
        get_framework_engine,
        MathematicalFrameworkEngine,
    )
    MATH_FRAMEWORK_AVAILABLE = True
except ImportError:
    MATH_FRAMEWORK_AVAILABLE = False

try:
    from clawspring.amos_brain.math_audit_logger import get_math_audit_logger
    AUDIT_LOGGER_AVAILABLE = True
except ImportError:
    AUDIT_LOGGER_AVAILABLE = False


@dataclass
class EquationToolResult:
    """Result from SuperBrain equation tool execution."""
    equation_name: str
    domain: str
    pattern: str
    inputs: Dict[str, Any]
    outputs: Dict[str, Any]
    invariants_valid: bool
    invariant_violations: List[str]
    execution_time_ms: float
    cross_domain_links: List[str]
    timestamp: str
    execution_id: str


class AMOSSuperBrainEquationTool:
    """
    AMOS Tool for executing SuperBrain equations.

    Integrates 41 technology domains (180+ equations) into AMOS tool ecosystem.
    Includes Phase 15: AGI Pathways & Future Intelligence (2026-2030).
    Provides governance, audit trails, and cross-domain pattern detection.
    """

    def __init__(self):
        self._bridge: Optional[AMOSSuperBrainBridge] = None
        self._audit: Optional[Any] = None
        self._superbrain: Optional[Any] = None
        self._execution_count = 0
        self._init_integrations()

    def _init_integrations(self):
        """Initialize all AMOS ecosystem integrations."""
        if BRIDGE_AVAILABLE:
            self._bridge = AMOSSuperBrainBridge()

        if SUPERBRAIN_AVAILABLE:
            try:
                self._superbrain = get_super_brain()
            except Exception:
                pass

        if AUDIT_AVAILABLE:
            try:
                self._audit = AuditExporter()
            except Exception:
                pass

    def _validate_via_superbrain(
        self,
        equation_name: str,
        inputs: Dict[str, Any]
    ) -> Tuple[bool, str]:
        """
        Validate equation execution via SuperBrain ActionGate.

        Returns:
            (authorized, reason)
        """
        if not SUPERBRAIN_AVAILABLE or not self._superbrain:
            return True, "SuperBrain not available - fail open"

        try:
            if hasattr(self._superbrain, 'action_gate'):
                action_result = self._superbrain.action_gate.validate_action(
                    agent_id="amos_superbrain_equations",
                    action=f"execute_equation_{equation_name}",
                    details={
                        "equation": equation_name,
                        "input_keys": list(inputs.keys()),
                        "input_types": [type(v).__name__ for v in inputs.values()]
                    }
                )
                return action_result.authorized, getattr(
                    action_result, 'reason', 'No reason provided'
                )
        except Exception as e:
            return True, f"Validation error: {str(e)}"

        return True, "No ActionGate available"

    def _record_in_audit(self, result: EquationToolResult):
        """Record equation execution in AMOS audit trail."""
        if not self._audit:
            return

        try:
            audit_entry = {
                "timestamp": result.timestamp,
                "execution_id": result.execution_id,
                "equation": result.equation_name,
                "domain": result.domain,
                "pattern": result.pattern,
                "invariants_valid": result.invariants_valid,
                "violations": result.invariant_violations,
                "execution_time_ms": result.execution_time_ms,
                "cross_domain_links": len(result.cross_domain_links)
            }

            # Use audit exporter if available
            if hasattr(self._audit, 'export_audit_entry'):
                self._audit.export_audit_entry(audit_entry)
        except Exception:
            pass

    def execute_equation(
        self,
        equation_name: str,
        inputs: Dict[str, Any]
    ) -> EquationToolResult:
        """
        Execute a SuperBrain equation with full AMOS governance.

        Args:
            equation_name: Name of equation to execute
            inputs: Equation inputs as dictionary

        Returns:
            EquationToolResult with execution details
        """
        self._execution_count += 1
        execution_id = f"eq_exec_{self._execution_count}_{datetime.now().strftime('%Y%m%d%H%M%S')}"

        # Validate via SuperBrain governance
        authorized, reason = self._validate_via_superbrain(equation_name, inputs)
        if not authorized:
            return EquationToolResult(
                equation_name=equation_name,
                domain="unknown",
                pattern="blocked",
                inputs=inputs,
                outputs={},
                invariants_valid=False,
                invariant_violations=[f"Blocked by SuperBrain: {reason}"],
                execution_time_ms=0.0,
                cross_domain_links=[],
                timestamp=datetime.now().isoformat(),
                execution_id=execution_id
            )

        # Execute via bridge
        if not BRIDGE_AVAILABLE or not self._bridge:
            return EquationToolResult(
                equation_name=equation_name,
                domain="unknown",
                pattern="error",
                inputs=inputs,
                outputs={},
                invariants_valid=False,
                invariant_violations=["Equation bridge not available"],
                execution_time_ms=0.0,
                cross_domain_links=[],
                timestamp=datetime.now().isoformat(),
                execution_id=execution_id
            )

        try:
            exec_result = self._bridge.compute(equation_name, inputs)

            result = EquationToolResult(
                equation_name=equation_name,
                domain=exec_result.pattern_detected.value if exec_result.pattern_detected else "unknown",
                pattern=exec_result.pattern_detected.value if exec_result.pattern_detected else "unknown",
                inputs=inputs,
                outputs=exec_result.outputs,
                invariants_valid=exec_result.invariants_valid,
                invariant_violations=exec_result.invariant_violations,
                execution_time_ms=exec_result.execution_time_ms,
                cross_domain_links=exec_result.cross_domain_links,
                timestamp=datetime.now().isoformat(),
                execution_id=execution_id
            )

            # Record in audit trail
            self._record_in_audit(result)

            return result

        except Exception as e:
            return EquationToolResult(
                equation_name=equation_name,
                domain="error",
                pattern="error",
                inputs=inputs,
                outputs={},
                invariants_valid=False,
                invariant_violations=[str(e)],
                execution_time_ms=0.0,
                cross_domain_links=[],
                timestamp=datetime.now().isoformat(),
                execution_id=execution_id
            )

    def list_available_equations(self, domain: str  = None) -> List[dict[str, Any]]:
        """
        List all available equations, optionally filtered by domain.

        Args:
            domain: Optional domain filter (e.g., 'federated_learning')

        Returns:
            List of equation metadata dictionaries
        """
        if not BRIDGE_AVAILABLE or not self._bridge:
            return []

        equations = []
        for name, meta in self._bridge.registry.metadata.items():
            if domain is None or meta.domain.value == domain:
                equations.append({
                    "name": name,
                    "domain": meta.domain.value,
                    "pattern": meta.pattern.value,
                    "formula": meta.formula,
                    "description": meta.description,
                    "invariants": meta.invariants,
                    "phase": meta.phase
                })

        return equations

    def get_pattern_analysis(self) -> Dict[str, Any]:
        """Get cross-domain pattern analysis from equation executions."""
        if not BRIDGE_AVAILABLE or not self._bridge:
            return {"error": "Bridge not available"}

        return self._bridge.get_pattern_analysis()

    def batch_execute(
        self,
        computations: List[tuple[str, dict[str, Any]]]
    ) -> List[EquationToolResult]:
        """
        Execute multiple equations in batch.

        Args:
            computations: List of (equation_name, inputs) tuples

        Returns:
            List of EquationToolResult
        """
        results = []
        for eq_name, inputs in computations:
            result = self.execute_equation(eq_name, inputs)
            results.append(result)
        return results

    def export_to_dashboard(self) -> Dict[str, Any]:
        """
        Export equation system metrics for dashboard visualization.

        Returns:
            Dashboard data dictionary
        """
        if not BRIDGE_AVAILABLE or not self._bridge:
            return {
                "error": "Equation bridge not available",
                "version": "8.1.0-PHASE15",
                "domains": 0,
                "equations": 0
            }

        pattern_analysis = self._bridge.get_pattern_analysis()

        return {
            "version": "8.1.0-PHASE15",
            "domains": pattern_analysis.get("domains_covered", 0),
            "total_equations": pattern_analysis.get("total_equations", 0),
            "pattern_distribution": pattern_analysis.get("pattern_distribution", {}),
            "cross_domain_isomorphisms": pattern_analysis.get("cross_domain_isomorphisms", []),
            "execution_count": self._execution_count,
            "last_updated": datetime.now().isoformat(),
            "available_domains": list(set(
                meta.domain.value
                for meta in self._bridge.registry.metadata.values()
            )),
            "equation_sample": [
                {
                    "name": name,
                    "domain": meta.domain.value,
                    "formula": meta.formula
                }
                for name, meta in list(self._bridge.registry.metadata.items())[:5]
            ]
        }

    def analyze_with_math_framework(
        self,
        equation_name: str
    ) -> Dict[str, Any]:
        """Analyze SuperBrain equation using mathematical framework.

        Cross-references the equation with the AMOS Mathematical Framework
        Engine for enhanced domain analysis and invariant validation.

        Args:
            equation_name: Name of the equation to analyze

        Returns:
            Analysis result with math framework insights
        """
        if not MATH_FRAMEWORK_AVAILABLE:
            return {
                "error": "Mathematical Framework Engine not available",
                "equation": equation_name,
                "math_framework_enabled": False
            }

        if not BRIDGE_AVAILABLE or not self._bridge:
            return {
                "error": "SuperBrain bridge not available",
                "equation": equation_name
            }

        try:
            # Get equation metadata from bridge
            if equation_name not in self._bridge.registry.metadata:
                return {
                    "error": f"Equation '{equation_name}' not found in registry",
                    "analysis_status": "failed"
                }

            meta = self._bridge.registry.metadata[equation_name]

            # Get mathematical framework engine
            math_engine = get_framework_engine()

            # Map SuperBrain domain to math framework domain
            domain_map = {
                "machine_learning": "AI_ML",
                "deep_learning": "AI_ML",
                "reinforcement_learning": "AI_ML",
                "distributed_systems": "DISTRIBUTED_SYSTEMS",
                "security": "SECURITY",
                "quantum_computing": "PHYSICS"
            }

            math_domain = domain_map.get(
                meta.domain.value,
                "GENERAL"
            )

            # Query math framework for related equations
            related_equations = []
            if hasattr(math_engine, '_equations'):
                for fw_eq in math_engine._equations.values():
                    # Match by keywords
                    if any(kw in equation_name.lower()
                           for kw in fw_eq.name.lower().split('_')):
                        related_equations.append({
                            "name": fw_eq.name,
                            "formula": fw_eq.formula,
                            "domain": fw_eq.domain
                        })

            # Log analysis to audit
            if AUDIT_LOGGER_AVAILABLE:
                try:
                    audit_logger = get_math_audit_logger()
                    audit_logger.log_architecture_analysis(
                        f"superbrain_equation_{equation_name}",
                        [meta.domain.value, math_domain],
                        ["SuperBrainBridge", "MathematicalFrameworkEngine"]
                    )
                except Exception:
                    pass

            return {
                "equation": equation_name,
                "superbrain_domain": meta.domain.value,
                "math_framework_domain": math_domain,
                "pattern": meta.pattern.value,
                "related_math_equations": related_equations[:5],
                "math_framework_enabled": True,
                "analysis_status": "success"
            }

        except Exception as e:
            return {
                "error": f"Analysis failed: {str(e)}",
                "equation": equation_name,
                "analysis_status": "failed"
            }

    def get_domain_coverage_report(self) -> Dict[str, Any]:
        """Generate comprehensive domain coverage report."""
        if not BRIDGE_AVAILABLE or not self._bridge:
            return {"error": "Bridge not available"}

        coverage = {}
        for domain in Domain:
            equations = self._bridge.registry.get_by_domain(domain)
            coverage[domain.value] = {
                "equation_count": len(equations),
                "equations": equations[:10]  # First 10
            }

        return {
            "total_domains": len(Domain),
            "domains_with_equations": sum(1 for v in coverage.values() if v["equation_count"] > 0),
            "coverage": coverage,
            "fully_covered_domains": [
                d for d, v in coverage.items() if v["equation_count"] > 0
            ]
        }


# Tool function for amos_tools.py integration
def _amos_superbrain_equations(
    params: Dict[str, Any],
    config: Dict[str, Any]
) -> str:
    """
    Execute SuperBrain mathematical equations from 36 technology domains.

    Tool function for AMOS tool registry.
    """
    action = params.get("action", "execute")
    tool = AMOSSuperBrainEquationTool()

    if action == "execute":
        equation = params.get("equation", "")
        inputs = params.get("inputs", {})

        if not equation:
            return "Error: 'equation' parameter required"

        result = tool.execute_equation(equation, inputs)

        lines = [
            f"# SuperBrain Equation Execution: {result.equation_name}",
            f"Execution ID: {result.execution_id}",
            f"Domain: {result.domain}",
            f"Pattern: {result.pattern}",
            "",
            "## Inputs",
            json.dumps(result.inputs, indent=2, default=str),
            "",
            "## Outputs",
            json.dumps(result.outputs, indent=2, default=str),
            "",
            f"## Invariants Valid: {result.invariants_valid}",
        ]

        if result.invariant_violations:
            lines.extend([
                "### Violations:",
                "\n".join(f"- {v}" for v in result.invariant_violations)
            ])

        if result.cross_domain_links:
            lines.extend([
                "",
                "## Cross-Domain Links",
                "\n".join(f"- {link}" for link in result.cross_domain_links)
            ])

        lines.extend([
            "",
            f"Execution Time: {result.execution_time_ms:.2f}ms",
            f"Timestamp: {result.timestamp}"
        ])

        return "\n".join(lines)

    elif action == "list":
        domain = params.get("domain")
        equations = tool.list_available_equations(domain)

        lines = [
            f"# Available SuperBrain Equations ({len(equations)} total)",
            ""
        ]

        for eq in equations:
            lines.append(f"## {eq['name']}")
            lines.append(f"Domain: {eq['domain']}")
            lines.append(f"Pattern: {eq['pattern']}")
            lines.append(f"Formula: {eq['formula']}")
            lines.append(f"Phase: {eq['phase']}")
            lines.append("")

        return "\n".join(lines)

    elif action == "patterns":
        analysis = tool.get_pattern_analysis()

        return json.dumps(analysis, indent=2)

    elif action == "dashboard":
        data = tool.export_to_dashboard()

        return json.dumps(data, indent=2)

    elif action == "coverage":
        report = tool.get_domain_coverage_report()

        lines = [
            f"# SuperBrain Domain Coverage Report",
            f"Total Domains: {report['total_domains']}",
            f"Domains with Equations: {report['domains_with_equations']}",
            ""
        ]

        for domain_name, info in report['coverage'].items():
            if info['equation_count'] > 0:
                lines.append(f"## {domain_name}: {info['equation_count']} equations")
                for eq_name in info['equations'][:5]:
                    lines.append(f"  - {eq_name}")

        return "\n".join(lines)

    else:
        return f"Unknown action: {action}. Use: execute, list, patterns, dashboard, coverage"


# Export for tool registry
AMOS_SUPERBRAIN_EQUATION_TOOL = {
    "name": "AMOSSuperBrainEquations",
    "description": (
        "Execute mathematical equations from 36 technology domains (160+ equations). "
        "Includes: Federated Learning, CRDTs, Neural Verification, TPU/XLA, and more. "
        "Provides invariant checking and cross-domain pattern detection."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "enum": ["execute", "list", "patterns", "dashboard", "coverage"],
                "description": "Action to perform"
            },
            "equation": {
                "type": "string",
                "description": "Equation name for execute action"
            },
            "inputs": {
                "type": "object",
                "description": "Equation inputs for execute action"
            },
            "domain": {
                "type": "string",
                "description": "Optional domain filter for list action"
            }
        },
        "required": ["action"]
    },
    "handler": _amos_superbrain_equations
}


if __name__ == "__main__":
    # Demo the tool
    tool = AMOSSuperBrainEquationTool()

    print("=" * 70)
    print("AMOS SuperBrain Equation Tool - Demo")
    print("=" * 70)

    # Execute an equation
    result = tool.execute_equation(
        "privacy_budget",
        {"epsilons": [0.1, 0.2, 0.3]}
    )

    print(f"\nExecuted: {result.equation_name}")
    print(f"Domain: {result.domain}")
    print(f"Outputs: {result.outputs}")
    print(f"Invariants Valid: {result.invariants_valid}")
    print(f"Cross-Domain Links: {len(result.cross_domain_links)}")

    # Get dashboard data
    dashboard = tool.export_to_dashboard()
    print(f"\nDashboard Data:")
    print(f"  Total Equations: {dashboard['total_equations']}")
    print(f"  Domains: {dashboard['domains']}")
    print(f"  Pattern Distribution: {dashboard['pattern_distribution']}")

    print("\n" + "=" * 70)
    print("Tool integration complete!")
    print("=" * 70)
