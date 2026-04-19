"""AMOS Brain Architecture Bridge - Architectural Integrity Integration.

Connects Repo Doctor's architectural integrity engine to the AMOS brain,
enabling architecture-aware decision making and invariant validation.
"""

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, TYPE_CHECKING, Union

sys.path.insert(0, str(Path(__file__).parent.parent))


from repo_doctor.arch_invariants import ArchitectureInvariantEngine
from repo_doctor.architecture import build_architecture_graph
from repo_doctor.entanglement import EntanglementMatrix
from repo_doctor.repair_plan import RepairPlanner
from repo_doctor.state_vector import RepoStateVector, StateDimension

if TYPE_CHECKING:
    from repo_doctor.arch_invariants import ArchInvariantResult
    from repo_doctor.architecture import ArchitectureGraph
    from repo_doctor.repair_plan import RepairAction


@dataclass
class ArchitecturalContext:
    """Complete architectural context for brain decisions."""

    arch_score: float
    hidden_score: float
    total_score: float
    node_count: int
    edge_count: int
    boundary_violations: List[dict]
    authority_issues: List[dict]
    hidden_interfaces: List[dict]
    high_entanglement_pairs: List[tuple[str, str, float]]
    critical_modules: List[str]
    failed_invariants: List["ArchInvariantResult"]
    repair_actions: List["RepairAction"]
    trend: str = "stable"


@dataclass
class ArchitectureValidationResult:
    """Result of validating a decision against architecture."""

    approved: bool
    arch_impact_score: float
    invariant_violations: List[str]
    boundary_risks: List[str]
    authority_risks: List[str]
    coupling_impacts: List[str]
    suggested_constraints: List[str]
    alternative_actions: List[str]


class ArchitecturalCognitionBridge:
    """Bridge connecting Repo Doctor architectural analysis to AMOS Brain."""

    ARCH_SCORE_THRESHOLD = 0.7
    ENTANGLEMENT_THRESHOLD = 0.5

    def __init__(self, repo_path: Optional[Union[str, Path]] = None):
        self.repo_path = Path(repo_path) if repo_path else Path.cwd()
        self._arch_engine: Optional[ArchitectureInvariantEngine] = None
        self._arch_graph: Optional[ArchitectureGraph] = None
        self._entanglement: Optional[EntanglementMatrix] = None
        self._cached_context: Optional[ArchitecturalContext] = None

    @property
    def arch_engine(self):
        if self._arch_engine is None:
            self._arch_engine = ArchitectureInvariantEngine(self.repo_path)
        return self._arch_engine

    @property
    def arch_graph(self):
        if self._arch_graph is None:
            self._arch_graph = build_architecture_graph(self.repo_path)
        return self._arch_graph

    @property
    def entanglement(self) -> EntanglementMatrix:
        if self._entanglement is None:
            self._entanglement = EntanglementMatrix(self.repo_path)
        return self._entanglement

    def get_context(self, force_refresh: bool = False) -> ArchitecturalContext:
        """Gather complete architectural context for brain decisions."""
        if self._cached_context is not None and not force_refresh:
            return self._cached_context

        arch_score, hidden_score, results = self.arch_engine.get_architectural_state()

        state = RepoStateVector()
        state.set(StateDimension.ARCHITECTURE, arch_score)
        state.set(StateDimension.HIDDEN_STATE, hidden_score)

        boundary_violations = []
        authority_issues = []
        hidden_interfaces = []
        failed = [r for r in results if not r.passed]

        for r in failed:
            if r.invariant_name == "boundary_integrity":
                boundary_violations.extend(r.violations)
            elif r.invariant_name == "single_authority":
                authority_issues.extend(r.details)
            elif r.invariant_name == "hidden_interfaces":
                hidden_interfaces.extend(r.details)

        edges = self.entanglement.analyze()
        high_ent = [
            (e.module_a, e.module_b, e.total_weight)
            for e in edges
            if e.total_weight > self.ENTANGLEMENT_THRESHOLD
        ]

        module_scores = {}
        for e in edges:
            module_scores[e.module_a] = module_scores.get(e.module_a, 0) + e.total_weight
            module_scores[e.module_b] = module_scores.get(e.module_b, 0) + e.total_weight

        critical = sorted(module_scores.keys(), key=lambda m: module_scores[m], reverse=True)[:5]

        planner = RepairPlanner(self.repo_path)
        plan = planner.generate_architecture_plan(state, results)

        context = ArchitecturalContext(
            arch_score=arch_score,
            hidden_score=hidden_score,
            total_score=state.score(),
            node_count=len(self.arch_graph.nodes),
            edge_count=len(self.arch_graph.edges),
            boundary_violations=boundary_violations,
            authority_issues=authority_issues,
            hidden_interfaces=hidden_interfaces,
            high_entanglement_pairs=high_ent,
            critical_modules=critical,
            failed_invariants=failed,
            repair_actions=plan.actions,
        )

        self._cached_context = context
        return context

    def validate(self, action: str, target_files: List[str]) -> ArchitectureValidationResult:
        """Validate a proposed brain decision against architectural constraints."""
        context = self.get_context()

        violations = []
        boundary_risks = []
        authority_risks = []
        coupling_impacts = []
        constraints = []
        alternatives = []
        impact = 0.0

        for file in target_files:
            for mod_a, mod_b, _weight in context.high_entanglement_pairs:
                if file in mod_a or file in mod_b:
                    other = mod_b if file in mod_a else mod_a
                    coupling_impacts.append(f"{file} coupled to {other}")
                    constraints.append(f"Test both {mod_a} and {mod_b}")

        for bv in context.boundary_violations:
            vf = bv.get("enforcing_node", "") if isinstance(bv, dict) else ""
            for target in target_files:
                if target in vf or vf in target:
                    reason = bv.get("reason", "") if isinstance(bv, dict) else ""
                    boundary_risks.append(f"{target}: {reason}")

        for ai in context.authority_issues:
            if isinstance(ai, dict):
                af = ai.get("file", "")
                for target in target_files:
                    if target in af or af in target:
                        msg = ai.get("message", "")
                        authority_risks.append(f"{target}: {msg}")

        if context.arch_score < self.ARCH_SCORE_THRESHOLD:
            violations.append(f"Arch score ({context.arch_score:.2f}) below threshold")
            impact += 0.3

        if action == "delete":
            for file in target_files:
                if file in context.critical_modules:
                    violations.append(f"Deleting critical module: {file}")
                    alternatives.append(f"Deprecate {file} instead")
                    impact += 0.2

        impact = min(impact, 1.0)
        approved = len(violations) == 0 and impact < 0.5 and len(boundary_risks) < 3

        return ArchitectureValidationResult(
            approved=approved,
            arch_impact_score=impact,
            invariant_violations=violations,
            boundary_risks=boundary_risks,
            authority_risks=authority_risks,
            coupling_impacts=coupling_impacts,
            suggested_constraints=constraints,
            alternative_actions=alternatives,
        )


def get_architecture_bridge(repo_path: Optional[Union[str, Path]] = None) -> ArchitecturalCognitionBridge:
    """Factory function to get architecture bridge instance."""
    return ArchitecturalCognitionBridge(repo_path)
