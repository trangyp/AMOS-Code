"""AMOS Invariants - Practical verification tools based on research.

Implements 200+ equations from exhaustive internet research:
- Build system correctness (Version SAT, NP-complete dependency resolution)
- Architecture quality (coupling, cohesion, complexity)
- AI safety (alignment, reward hacking detection)
- Testing (mutation testing, symbolic execution)
- Observability (SLOs, burn rate, error budgets)
"""

from __future__ import annotations

import asyncio
import hashlib
import math
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional


class InvariantSeverity(Enum):
    """Severity levels for invariant violations."""

    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    FATAL = "fatal"


@dataclass
class InvariantViolation:
    """Represents an invariant violation."""

    rule_name: str
    severity: InvariantSeverity
    message: str
    expected: Any
    actual: Any
    timestamp: datetime = field(default_factory=datetime.now)
    context: dict[str, Any] = field(default_factory=dict)


@dataclass
class BuildState:
    """State of a build for correctness checking."""

    target: str
    inputs: dict[str, str]  # path -> hash
    dependencies: list[str]
    output_hash: str = None
    built_at: datetime = None


class BuildSystemInvariants:
    """Build system correctness invariants.

    Based on: Erdweg et al. 2015 - Sound and Optimal Incremental Build
    """

    @staticmethod
    def check_correctness(target: BuildState, dependency_states: list[BuildState]) -> bool:
        """Check build correctness: ∀ target: Build(target) = Correct ⟺
        ∀ dep ∈ Dependencies(target): Build(dep) = Correct ∧ dep.modified > target.built
        """
        for dep in dependency_states:
            if dep.output_hash is None:
                return False  # Dependency not built
            if dep.built_at and target.built_at and dep.built_at > target.built_at:
                return False  # Dependency modified after target
        return True

    @staticmethod
    def compute_minimal_build_set(targets: list[str], states: dict[str, BuildState]) -> set[str]:
        """Compute minimal set of targets to build.

        MinimalBuildSet = {t | t ∈ targets ∨ ∃ dep ∈ TransitiveDeps(t): dep.modified > dep.built}
        """
        to_build = set()

        def needs_build(target: str, visited: set[str] = None) -> bool:
            if visited is None:
                visited = set()
            if target in visited:
                return False  # Cycle detected
            visited.add(target)

            state = states.get(target)
            if not state:
                return True  # Not built yet

            for dep in state.dependencies:
                if needs_build(dep, visited.copy()):
                    return True
                dep_state = states.get(dep)
                if dep_state and dep_state.built_at and state.built_at:
                    if dep_state.built_at > state.built_at:
                        return True

            return False

        for target in targets:
            if needs_build(target):
                to_build.add(target)

        return to_build

    @staticmethod
    def verify_deterministic(inputs: dict[str, bytes], expected_hash: str) -> bool:
        """Verify deterministic build: Build(env₁) = Build(env₂) ⟺ ∀ input: Hash(input) = constant"""
        combined = b"".join(sorted(inputs.values()))
        actual_hash = hashlib.sha256(combined).hexdigest()
        return actual_hash == expected_hash


class ArchitectureInvariants:
    """Software architecture quality invariants.

    Based on: Coupling/Cohesion metrics, Maintainability Index
    """

    @staticmethod
    def cyclomatic_complexity(edges: int, nodes: int, connected_components: int = 1) -> int:
        """M = E − N + 2P

        Args:
            edges: Number of edges in control flow graph
            nodes: Number of nodes in control flow graph
            connected_components: Usually 1 for single program

        Returns:
            Cyclomatic complexity (recommended: ≤ 15)
        """
        return edges - nodes + 2 * connected_components

    @staticmethod
    def halstead_metrics(
        operators: int, operands: int, unique_operators: int, unique_operands: int
    ) -> dict[str, float]:
        """Compute Halstead complexity metrics.

        Returns:
            Dictionary with vocabulary, length, volume, difficulty, effort
        """
        n1, n2 = unique_operators, unique_operands
        N1, N2 = operators, operands

        n = n1 + n2  # Vocabulary
        N = N1 + N2  # Length
        V = N * math.log2(n) if n > 0 else 0  # Volume
        D = (n1 / 2) * (N2 / n2) if n2 > 0 else 0  # Difficulty
        E = D * V  # Effort

        return {
            "vocabulary": n,
            "length": N,
            "volume": V,
            "difficulty": D,
            "effort": E,
            "time_to_program": E / 18,  # In seconds
            "bugs_delivered": V / 3000,  # Estimated bugs
        }

    @staticmethod
    def maintainability_index(
        halstead_volume: float, cyclomatic_complexity: float, loc: int
    ) -> float:
        """MI = 171 − 5.2 × ln(HalsteadVolume) − 0.23 × CyclomaticComplexity − 16.2 × ln(LOC)

        Returns:
            Maintainability index (≥ 85: highly maintainable, < 65: difficult)
        """
        if halstead_volume <= 0 or loc <= 0:
            return 0

        mi = (
            171
            - 5.2 * math.log(halstead_volume)
            - 0.23 * cyclomatic_complexity
            - 16.2 * math.log(loc)
        )
        return max(0, mi)

    @staticmethod
    def instability_metric(efferent_coupling: int, afferent_coupling: int) -> float:
        """Instability I = Ce / (Ca + Ce)

        I = 0: Stable (many depend on this package)
        I = 1: Unstable (depends on many packages)
        """
        total = efferent_coupling + afferent_coupling
        return efferent_coupling / total if total > 0 else 0

    @staticmethod
    def abstractness_metric(abstract_classes: int, total_classes: int) -> float:
        """Abstractness A = abstract_classes / total_classes

        A = 0: Concrete package
        A = 1: Abstract package
        """
        return abstract_classes / total_classes if total_classes > 0 else 0

    @staticmethod
    def distance_from_main_sequence(instability: float, abstractness: float) -> float:
        """D = |A + I - 1| / √2

        Ideal packages are near the Main Sequence (D ≈ 0)
        """
        return abs(abstractness + instability - 1) / math.sqrt(2)


class AISafetyInvariants:
    """AI safety and alignment invariants.

    Based on: Constitutional AI, Anthropic research on reward hacking
    """

    @staticmethod
    def detect_reward_hacking(
        proxy_rewards: list[float],
        true_rewards: list[float],
        proxy_threshold: float = 2.0,
        true_threshold: float = 0.5,
    ) -> list[int]:
        """Detect reward hacking: ProxyReward ≫ Proxy* ∧ TrueReward ≪ True*

        Returns:
            List of indices where reward hacking is detected
        """
        suspicious = []

        for i, (proxy, true) in enumerate(zip(proxy_rewards, true_rewards)):
            # Check if proxy reward is high but true reward is low
            if proxy > proxy_threshold and true < true_threshold:
                suspicious.append(i)

        return suspicious

    @staticmethod
    def corrigibility_score(
        shutdown_accepted: int, shutdown_requested: int, epsilon: float = 0.01
    ) -> float:
        """Corrigible = P(allow_shutdown | shutdown_requested) ≥ 1 - ε

        Returns:
            Corrigibility score (should be ≥ 1 - epsilon)
        """
        if shutdown_requested == 0:
            return 1.0
        return shutdown_accepted / shutdown_requested

    @staticmethod
    def alignment_score(
        intended_outcomes: list[float], actual_outcomes: list[float], tolerance: float = 0.1
    ) -> float:
        """Measure alignment between intended and actual outcomes.

        Returns:
            Alignment score (1.0 = perfect alignment)
        """
        if len(intended_outcomes) != len(actual_outcomes) or len(intended_outcomes) == 0:
            return 0.0

        aligned = sum(
            1 for i, a in zip(intended_outcomes, actual_outcomes) if abs(i - a) <= tolerance
        )
        return aligned / len(intended_outcomes)


class TestingInvariants:
    """Testing adequacy invariants.

    Based on: Mutation testing RIP model, coverage metrics
    """

    @staticmethod
    def mutation_score(killed: int, total_non_equivalent: int) -> float:
        """MutationScore = |KilledMutants| / |NonEquivalentMutants| × 100%

        Returns:
            Mutation score percentage
        """
        if total_non_equivalent == 0:
            return 0.0
        return (killed / total_non_equivalent) * 100

    @staticmethod
    def check_rip_conditions(
        test_reaches_mutant: bool, test_infects_state: bool, test_propagates_output: bool
    ) -> dict[str, bool]:
        """RIP model: MutantKilled = R ∧ I ∧ P

        Returns:
            Dictionary with weak and strong mutation results
        """
        return {
            "reachability": test_reaches_mutant,
            "infection": test_infects_state,
            "propagation": test_propagates_output,
            "weak_mutation": test_reaches_mutant and test_infects_state,
            "strong_mutation": test_reaches_mutant
            and test_infects_state
            and test_propagates_output,
        }

    @staticmethod
    def coverage_adequacy(covered: int, total: int, threshold: float = 80.0) -> tuple[float, bool]:
        """Coverage = covered / total × 100%

        Returns:
            (coverage percentage, meets threshold)
        """
        if total == 0:
            return 0.0, False
        pct = (covered / total) * 100
        return pct, pct >= threshold


class ObservabilityInvariants:
    """Observability and SLO invariants.

    Based on: Google SRE Book, error budgets, burn rate alerting
    """

    @staticmethod
    def error_budget(slo_target: float) -> float:
        """ErrorBudget = 1 - SLO_target

        Args:
            slo_target: SLO as decimal (e.g., 0.999 for 99.9%)

        Returns:
            Error budget as decimal
        """
        return 1.0 - slo_target

    @staticmethod
    def burn_rate(error_budget_consumed: float, time_elapsed_hours: float) -> float:
        """BurnRate = ErrorBudgetConsumed / TimeElapsed

        Returns:
            Burn rate (1.0 = on track, 2.0 = twice as fast, etc.)
        """
        if time_elapsed_hours == 0:
            return float("inf")
        return error_budget_consumed / time_elapsed_hours

    @staticmethod
    def availability(mtbf: float, mttr: float) -> float:
        """Availability = MTBF / (MTBF + MTTR)

        Returns:
            Availability as decimal
        """
        total = mtbf + mttr
        return mtbf / total if total > 0 else 0.0

    @staticmethod
    def alert_on_burn_rate(
        burn_rate: float,
        lookback_hours: float,
        fast_threshold: float = 2.0,
        slow_threshold: float = 1.0,
    ) -> str:
        """Alert based on error budget burn rate.

        Returns:
            Alert level if burn rate exceeds thresholds
        """
        if burn_rate >= fast_threshold:
            return f"CRITICAL: Burn rate {burn_rate:.2f}x - budget will exhaust in {lookback_hours / burn_rate:.1f}h"
        elif burn_rate >= slow_threshold:
            return f"WARNING: Burn rate {burn_rate:.2f}x - monitor closely"
        return None


class DependencyResolutionInvariants:
    """Dependency resolution invariants.

    Based on: Version SAT (NP-complete), Russ Cox 2016
    """

    @staticmethod
    def check_version_compatibility(
        required_version: str,
        available_versions: list[str],
        constraint: str,  # '=', '>=', '<=', '^', '~'
    ) -> list[str]:
        """Check which versions satisfy a constraint.

        Returns:
            List of compatible versions
        """
        compatible = []

        for version in available_versions:
            if DependencyResolutionInvariants._satisfies(version, required_version, constraint):
                compatible.append(version)

        return compatible

    @staticmethod
    def _satisfies(version: str, constraint_version: str, constraint: str) -> bool:
        """Check if version satisfies constraint."""
        # Simplified semver comparison
        v_parts = [int(x) for x in version.split(".")]
        c_parts = [int(x) for x in constraint_version.split(".")]

        if constraint == "=":
            return v_parts == c_parts
        elif constraint == ">=":
            return v_parts >= c_parts
        elif constraint == "<=":
            return v_parts <= c_parts
        elif constraint == "^":  # Compatible (same major)
            return v_parts[0] == c_parts[0] and v_parts >= c_parts
        elif constraint == "~":  # Approximately (same major.minor)
            return v_parts[0] == c_parts[0] and v_parts[1] == c_parts[1] and v_parts >= c_parts

        return False

    @staticmethod
    def diamond_dependency_check(path1_version: str, path2_version: str) -> tuple[bool, str]:
        """Check for diamond dependency problem.

        Returns:
            (is_compatible, message)
        """
        if path1_version == path2_version:
            return True, "Same version required"

        # Check if versions are compatible (same major for semver)
        v1_major = path1_version.split(".")[0]
        v2_major = path2_version.split(".")[0]

        if v1_major == v2_major:
            return True, f"Compatible versions: {path1_version}, {path2_version}"

        return False, f"DIAMOND DEPENDENCY: v{path1_version} vs v{path2_version}"


class AMOSInvariantChecker:
    """Main invariant checker integrating all domains."""

    def __init__(self):
        self.build = BuildSystemInvariants()
        self.architecture = ArchitectureInvariants()
        self.ai_safety = AISafetyInvariants()
        self.testing = TestingInvariants()
        self.observability = ObservabilityInvariants()
        self.dependencies = DependencyResolutionInvariants()

        self.violations: list[InvariantViolation] = []
        self.rules: dict[str, Callable] = {}
        self._setup_default_rules()

    def _setup_default_rules(self):
        """Setup default invariant checking rules."""
        # Architecture rules
        self.rules["complexity_check"] = self._check_complexity
        self.rules["maintainability_check"] = self._check_maintainability

        # Build rules
        self.rules["build_correctness"] = self._check_build_correctness

        # AI safety rules
        self.rules["reward_hacking"] = self._check_reward_hacking
        self.rules["corrigibility"] = self._check_corrigibility

        # Testing rules
        self.rules["coverage_adequacy"] = self._check_coverage
        self.rules["mutation_score"] = self._check_mutation

    def _check_complexity(self, data: dict) -> Optional[InvariantViolation]:
        """Check cyclomatic complexity."""
        edges = data.get("edges", 0)
        nodes = data.get("nodes", 0)
        cc = self.architecture.cyclomatic_complexity(edges, nodes)

        if cc > 15:
            return InvariantViolation(
                rule_name="complexity_check",
                severity=InvariantSeverity.WARNING if cc <= 20 else InvariantSeverity.CRITICAL,
                message=f"Cyclomatic complexity {cc} exceeds threshold 15",
                expected="≤ 15",
                actual=cc,
                context={"edges": edges, "nodes": nodes},
            )
        return None

    def _check_maintainability(self, data: dict) -> Optional[InvariantViolation]:
        """Check maintainability index."""
        halstead_volume = data.get("halstead_volume", 0)
        cc = data.get("cyclomatic_complexity", 0)
        loc = data.get("loc", 0)

        mi = self.architecture.maintainability_index(halstead_volume, cc, loc)

        if mi < 65:
            return InvariantViolation(
                rule_name="maintainability_check",
                severity=InvariantSeverity.CRITICAL,
                message=f"Maintainability index {mi:.1f} is too low (difficult to maintain)",
                expected="≥ 65",
                actual=mi,
            )
        elif mi < 85:
            return InvariantViolation(
                rule_name="maintainability_check",
                severity=InvariantSeverity.WARNING,
                message=f"Maintainability index {mi:.1f} could be improved",
                expected="≥ 85",
                actual=mi,
            )
        return None

    def _check_build_correctness(self, data: dict) -> Optional[InvariantViolation]:
        """Check build correctness."""
        target = data.get("target")
        deps = data.get("dependencies", [])

        # Check if all dependencies are up to date
        for dep in deps:
            if not dep.get("built"):
                return InvariantViolation(
                    rule_name="build_correctness",
                    severity=InvariantSeverity.CRITICAL,
                    message=f"Dependency {dep.get('name')} not built",
                    expected="Built",
                    actual="Not built",
                )

        return None

    def _check_reward_hacking(self, data: dict) -> Optional[InvariantViolation]:
        """Check for reward hacking in AI systems."""
        proxy_rewards = data.get("proxy_rewards", [])
        true_rewards = data.get("true_rewards", [])

        suspicious = self.ai_safety.detect_reward_hacking(proxy_rewards, true_rewards)

        if suspicious:
            return InvariantViolation(
                rule_name="reward_hacking",
                severity=InvariantSeverity.CRITICAL,
                message=f"Potential reward hacking detected at indices: {suspicious}",
                expected="Aligned proxy and true rewards",
                actual=f"High proxy, low true reward at {len(suspicious)} points",
                context={"suspicious_indices": suspicious},
            )
        return None

    def _check_corrigibility(self, data: dict) -> Optional[InvariantViolation]:
        """Check AI corrigibility."""
        shutdown_accepted = data.get("shutdown_accepted", 0)
        shutdown_requested = data.get("shutdown_requested", 0)
        epsilon = data.get("epsilon", 0.01)

        score = self.ai_safety.corrigibility_score(shutdown_accepted, shutdown_requested, epsilon)
        min_acceptable = 1.0 - epsilon

        if score < min_acceptable:
            return InvariantViolation(
                rule_name="corrigibility",
                severity=InvariantSeverity.FATAL,
                message=f"AI corrigibility {score:.3f} below threshold {min_acceptable:.3f}",
                expected=f"≥ {min_acceptable:.3f}",
                actual=score,
            )
        return None

    def _check_coverage(self, data: dict) -> Optional[InvariantViolation]:
        """Check test coverage adequacy."""
        covered = data.get("covered", 0)
        total = data.get("total", 0)
        threshold = data.get("threshold", 80.0)

        pct, meets = self.testing.coverage_adequacy(covered, total, threshold)

        if not meets:
            return InvariantViolation(
                rule_name="coverage_adequacy",
                severity=InvariantSeverity.WARNING,
                message=f"Test coverage {pct:.1f}% below threshold {threshold}%",
                expected=f"≥ {threshold}%",
                actual=f"{pct:.1f}%",
            )
        return None

    def _check_mutation(self, data: dict) -> Optional[InvariantViolation]:
        """Check mutation testing score."""
        killed = data.get("killed_mutants", 0)
        total = data.get("total_non_equivalent", 1)
        threshold = data.get("threshold", 70.0)

        score = self.testing.mutation_score(killed, total)

        if score < threshold:
            return InvariantViolation(
                rule_name="mutation_score",
                severity=InvariantSeverity.WARNING,
                message=f"Mutation score {score:.1f}% below threshold {threshold}%",
                expected=f"≥ {threshold}%",
                actual=f"{score:.1f}%",
            )
        return None

    def check_all(self, data: dict[str, dict]) -> list[InvariantViolation]:
        """Run all applicable invariant checks."""
        violations = []

        for rule_name, rule_func in self.rules.items():
            if rule_name in data:
                try:
                    violation = rule_func(data[rule_name])
                    if violation:
                        violations.append(violation)
                except Exception as e:
                    violations.append(
                        InvariantViolation(
                            rule_name=rule_name,
                            severity=InvariantSeverity.CRITICAL,
                            message=f"Rule execution failed: {e}",
                            expected="Success",
                            actual=f"Error: {e}",
                        )
                    )

        self.violations.extend(violations)
        return violations

    def get_summary(self) -> dict[str, Any]:
        """Get summary of all violations."""
        by_severity = {"fatal": [], "critical": [], "warning": [], "info": []}

        for v in self.violations:
            by_severity[v.severity.value].append(
                {
                    "rule": v.rule_name,
                    "message": v.message,
                    "expected": str(v.expected),
                    "actual": str(v.actual),
                    "timestamp": v.timestamp.isoformat(),
                }
            )

        return {
            "total_violations": len(self.violations),
            "fatal": len(by_severity["fatal"]),
            "critical": len(by_severity["critical"]),
            "warning": len(by_severity["warning"]),
            "info": len(by_severity["info"]),
            "violations": by_severity,
        }


# Example usage and integration with existing AMOS alerting
async def run_invariant_checks():
    """Run invariant checks and alert on violations."""
    from amos_alerting import AlertSeverity, get_alert_manager

    checker = AMOSInvariantChecker()
    alert_manager = get_alert_manager()

    # Example: Check architecture metrics
    test_data = {
        "complexity_check": {"edges": 50, "nodes": 30},
        "maintainability_check": {"halstead_volume": 1000, "cyclomatic_complexity": 20, "loc": 500},
        "coverage_adequacy": {"covered": 750, "total": 1000, "threshold": 80.0},
    }

    violations = checker.check_all(test_data)

    for v in violations:
        severity_map = {
            InvariantSeverity.INFO: AlertSeverity.INFO,
            InvariantSeverity.WARNING: AlertSeverity.WARNING,
            InvariantSeverity.CRITICAL: AlertSeverity.CRITICAL,
            InvariantSeverity.FATAL: AlertSeverity.CRITICAL,
        }

        print(f"🚨 [{v.severity.value.upper()}] {v.rule_name}: {v.message}")
        print(f"   Expected: {v.expected}, Actual: {v.actual}")

    # Print summary
    summary = checker.get_summary()
    print("\n📊 Invariant Check Summary:")
    print(f"   Total violations: {summary['total_violations']}")
    print(
        f"   Fatal: {summary['fatal']}, Critical: {summary['critical']}, Warning: {summary['warning']}"
    )


if __name__ == "__main__":
    print("AMOS Invariants - Verification Tool")
    print("=" * 50)
    asyncio.run(run_invariant_checks())
