"""Entanglement Cognition Bridge.

Integrates Repo Doctor's entanglement analysis with the AMOS Brain
to enable coupling-aware decision making.

M_ij = alpha*import_link(i,j) + beta*test_coupling(i,j) + gamma*git_cochange(i,j)

High M_ij means:
- Changes in module i often destabilize module j
- They should be tested together
- They should be bisected together
- They may need contract isolation
"""

from __future__ import annotations


from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# Import entanglement matrix
try:
    from repo_doctor.entanglement import EntanglementEdge, EntanglementMatrix

    ENTANGLEMENT_AVAILABLE = True
except ImportError:
    ENTANGLEMENT_AVAILABLE = False


@dataclass
class EntanglementContext:
    """Complete entanglement context for a module or repository."""

    # Module info
    module_name: str
    total_modules: int = 0

    # Entanglement metrics
    avg_entanglement: float = 0.0
    max_entanglement: float = 0.0
    total_edges: int = 0
    high_entanglement_edges: int = 0

    # Coupling details
    strongly_coupled_modules: list[tuple[str, float]] = field(default_factory=list)
    import_coupled: list[str] = field(default_factory=list)
    test_coupled: list[str] = field(default_factory=list)
    git_coupled: list[str] = field(default_factory=list)

    # Risk assessment
    entanglement_risk_score: float = 0.0  # 0-1, higher = more risky
    change_impact_radius: int = 0  # Number of modules likely affected


@dataclass
class ChangeImpactPrediction:
    """Predicted impact of changing a module."""

    target_module: str
    predicted_affected_modules: list[str]
    risk_score: float
    test_recommendations: list[str]
    bisect_recommendations: list[str]
    isolation_suggestions: list[str]


@dataclass
class EntanglementAlert:
    """Alert about high entanglement issues."""

    severity: str  # critical, high, medium, low
    module_a: str
    module_b: str
    entanglement_score: float
    threshold: float
    message: str
    recommendation: str


class EntanglementCognitionBridge:
    """Bridge between entanglement analysis and AMOS Brain cognition.

    Provides:
    - Coupling-aware impact prediction
    - Module entanglement analysis
    - Change radius estimation
    - Test/bisect recommendations
    """

    def __init__(self, repo_path: str | Path):
        self.repo_path = Path(repo_path)
        self._matrix: EntanglementMatrix | None = None
        self._edges: list[EntanglementEdge] = []
        self._threshold_critical = 0.7
        self._threshold_high = 0.5
        self._threshold_medium = 0.3

    @property
    def matrix(self) -> EntanglementMatrix | None:
        """Lazy initialization of entanglement matrix."""
        if self._matrix is None and ENTANGLEMENT_AVAILABLE:
            self._matrix = EntanglementMatrix(self.repo_path)
            self._edges = self._matrix.analyze()
        return self._matrix

    def get_entanglement_context(self, module_name: str) -> EntanglementContext | None:
        """Get complete entanglement context for a module."""
        if not ENTANGLEMENT_AVAILABLE or self.matrix is None:
            return None

        # Find all edges involving this module
        module_edges = [
            e for e in self._edges if e.module_a == module_name or e.module_b == module_name
        ]

        if not module_edges:
            return EntanglementContext(
                module_name=module_name,
                total_modules=len(self.matrix.modules),
            )

        # Compute metrics
        weights = [e.total_weight for e in module_edges]
        avg_ent = sum(weights) / len(weights) if weights else 0.0
        max_ent = max(weights) if weights else 0.0

        # Find strongly coupled modules
        strong_threshold = 0.5
        strongly_coupled = []
        for edge in module_edges:
            other = edge.module_b if edge.module_a == module_name else edge.module_a
            strongly_coupled.append((other, edge.total_weight))
        strongly_coupled.sort(key=lambda x: -x[1])

        # Count high entanglement edges
        high_edges = sum(1 for w in weights if w > self._threshold_high)

        # Compute risk score
        risk_score = min(1.0, max_ent * 1.5)

        # Change impact radius
        impact_radius = len([w for w in weights if w > self._threshold_medium])

        return EntanglementContext(
            module_name=module_name,
            total_modules=len(self.matrix.modules),
            avg_entanglement=avg_ent,
            max_entanglement=max_ent,
            total_edges=len(module_edges),
            high_entanglement_edges=high_edges,
            strongly_coupled_modules=strongly_coupled[:10],
            entanglement_risk_score=risk_score,
            change_impact_radius=impact_radius,
        )

    def predict_change_impact(
        self,
        target_module: str,
        include_secondary: bool = True,
    ) -> ChangeImpactPrediction | None:
        """Predict impact of changing a module.

        Args:
            target_module: Module to be changed
            include_secondary: Whether to include secondary effects

        Returns:
            ChangeImpactPrediction with affected modules and recommendations
        """
        if not ENTANGLEMENT_AVAILABLE:
            return None

        context = self.get_entanglement_context(target_module)
        if context is None:
            return None

        # Primary affected modules (direct entanglement)
        primary_affected = [m for m, _ in context.strongly_coupled_modules]

        # Secondary affected modules (if requested)
        secondary_affected = []
        if include_secondary and primary_affected:
            for primary in primary_affected[:5]:
                primary_ctx = self.get_entanglement_context(primary)
                if primary_ctx:
                    for sec_module, weight in primary_ctx.strongly_coupled_modules:
                        if sec_module != target_module and sec_module not in primary_affected:
                            secondary_affected.append(sec_module)

        all_affected = list(dict.fromkeys(primary_affected + secondary_affected))

        # Generate recommendations
        test_recs = self._generate_test_recommendations(target_module, all_affected)
        bisect_recs = self._generate_bisect_recommendations(target_module, all_affected)
        isolation_recs = self._generate_isolation_suggestions(target_module, context)

        return ChangeImpactPrediction(
            target_module=target_module,
            predicted_affected_modules=all_affected,
            risk_score=context.entanglement_risk_score,
            test_recommendations=test_recs,
            bisect_recommendations=bisect_recs,
            isolation_suggestions=isolation_recs,
        )

    def check_entanglement_alerts(self) -> list[EntanglementAlert]:
        """Check for high entanglement issues across the repository."""
        alerts = []

        if not ENTANGLEMENT_AVAILABLE or self.matrix is None:
            return alerts

        for edge in self._edges:
            score = edge.total_weight

            if score >= self._threshold_critical:
                alerts.append(
                    EntanglementAlert(
                        severity="critical",
                        module_a=edge.module_a,
                        module_b=edge.module_b,
                        entanglement_score=score,
                        threshold=self._threshold_critical,
                        message=f"Critical entanglement: {edge.module_a} <-> {edge.module_b}",
                        recommendation="Immediate decoupling required. Consider contract interface.",
                    )
                )
            elif score >= self._threshold_high:
                alerts.append(
                    EntanglementAlert(
                        severity="high",
                        module_a=edge.module_a,
                        module_b=edge.module_b,
                        entanglement_score=score,
                        threshold=self._threshold_high,
                        message=f"High entanglement: {edge.module_a} <-> {edge.module_b}",
                        recommendation="Review coupling. Changes must be coordinated.",
                    )
                )
            elif score >= self._threshold_medium:
                alerts.append(
                    EntanglementAlert(
                        severity="medium",
                        module_a=edge.module_a,
                        module_b=edge.module_b,
                        entanglement_score=score,
                        threshold=self._threshold_medium,
                        message=f"Medium entanglement: {edge.module_a} <-> {edge.module_b}",
                        recommendation="Monitor for increasing coupling.",
                    )
                )

        return sorted(alerts, key=lambda x: -x.entanglement_score)

    def get_global_entanglement_summary(self) -> dict[str, Any]:
        """Get global entanglement summary for the repository."""
        if not ENTANGLEMENT_AVAILABLE or self.matrix is None:
            return {}

        if not self._edges:
            return {
                "total_modules": len(self.matrix.modules),
                "total_edges": 0,
                "avg_entanglement": 0.0,
                "max_entanglement": 0.0,
            }

        weights = [e.total_weight for e in self._edges]

        return {
            "total_modules": len(self.matrix.modules),
            "total_edges": len(self._edges),
            "avg_entanglement": sum(weights) / len(weights),
            "max_entanglement": max(weights),
            "critical_edges": sum(1 for w in weights if w >= self._threshold_critical),
            "high_edges": sum(1 for w in weights if w >= self._threshold_high),
            "medium_edges": sum(1 for w in weights if w >= self._threshold_medium),
        }

    def get_most_entangled_modules(self, n: int = 10) -> list[tuple[str, float]]:
        """Get the most entangled modules by average coupling."""
        if not ENTANGLEMENT_AVAILABLE or self.matrix is None:
            return []

        module_entanglement: dict[str, list[float]] = {}

        for edge in self._edges:
            for module in [edge.module_a, edge.module_b]:
                if module not in module_entanglement:
                    module_entanglement[module] = []
                module_entanglement[module].append(edge.total_weight)

        avg_entanglements = [
            (module, sum(weights) / len(weights)) for module, weights in module_entanglement.items()
        ]

        return sorted(avg_entanglements, key=lambda x: -x[1])[:n]

    def _generate_test_recommendations(
        self,
        target_module: str,
        affected_modules: list[str],
    ) -> list[str]:
        """Generate test recommendations based on entanglement."""
        recs = []

        if affected_modules:
            recs.append(f"Run tests for: {', '.join(affected_modules[:5])}")
            recs.append("Run integration tests covering entangled modules")

        if len(affected_modules) > 5:
            recs.append(
                f"Consider full regression test (high impact: {len(affected_modules)} modules)"
            )

        return recs

    def _generate_bisect_recommendations(
        self,
        target_module: str,
        affected_modules: list[str],
    ) -> list[str]:
        """Generate bisect recommendations based on entanglement."""
        recs = []

        if affected_modules:
            recs.append(f"Bisect must include: {', '.join(affected_modules[:3])}")

        return recs

    def _generate_isolation_suggestions(
        self,
        target_module: str,
        context: EntanglementContext,
    ) -> list[str]:
        """Generate contract isolation suggestions."""
        recs = []

        if context.max_entanglement > 0.7:
            recs.append(f"Consider formal contract for {target_module} interface")

        if context.high_entanglement_edges > 5:
            recs.append("High coupling detected - review module boundaries")

        return recs


def get_entanglement_bridge(repo_path: str | Path = None) -> EntanglementCognitionBridge:
    """Factory function to get entanglement bridge instance."""
    return EntanglementCognitionBridge(repo_path or ".")
