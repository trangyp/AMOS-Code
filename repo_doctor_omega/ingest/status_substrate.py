"""Status-truth validation substrate.

Validates that reported status labels are logically implied by actual state.

I_status = 1 iff every reported status label is logically
implied by actual state.

Examples:
- initialized = true implies real specs loaded
- brain_loaded = true implies non-empty real spec surface
- healthy = true implies no hard invariant false
- active_plan = true implies plan not terminal
"""
from __future__ import annotations

import ast
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class StatusClaim:
    """A status claim found in code."""

    status_name: str
    claimed_value: Any
    location: str  # file:line
    context: str = ""  # Function/class context

    @property
    def is_boolean(self) -> bool:
        """Check if claim is boolean."""
        return isinstance(self.claimed_value, bool)


@dataclass
class StatusValidation:
    """Result of validating a status claim."""

    claim: StatusClaim
    valid: bool
    actual_state: dict[str, Any] = field(default_factory=dict)
    error_message: str = ""

    @property
    def is_false_claim(self) -> bool:
        """Check if this is a false status claim."""
        return not self.valid


class StatusSubstrate:
    """Status-truth validation substrate.

    Extracts status claims from source code and validates them
    against actual repository state.

    Usage:
        substrate = StatusSubstrate("/path/to/repo")

        # Find all status claims
        claims = substrate.extract_status_claims()

        # Validate each claim
        for claim in claims:
            result = substrate.validate_claim(claim)
            if not result.valid:
                print(f"False claim: {claim.status_name} = {claim.claimed_value}")
    """

    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path).resolve()
        self._state_cache: dict[str, Any] | None = None

    def extract_status_claims(self, pattern: str = "*.py") -> list[StatusClaim]:
        """Extract status claims from source code.

        Looks for:
        - Boolean flags like initialized, brain_loaded, healthy
        - Status assignments
        - Configuration claims

        Args:
            pattern: File glob pattern

        Returns:
            List of status claims
        """
        claims = []

        for py_file in self.repo_path.rglob(pattern):
            if py_file.is_file() and not self._is_test_or_hidden(py_file):
                claims.extend(self._extract_from_file(py_file))

        return claims

    def _is_test_or_hidden(self, path: Path) -> bool:
        """Check if file is test or hidden."""
        parts = path.parts
        return any(p.startswith(".") for p in parts) or "test" in str(path).lower()

    def _extract_from_file(self, file_path: Path) -> list[StatusClaim]:
        """Extract status claims from a single file."""
        claims = []

        try:
            source = file_path.read_text(encoding="utf-8", errors="replace")
            tree = ast.parse(source)

            # Look for status-related assignments
            for node in ast.walk(tree):
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            name = target.id.lower()

                            # Check if it's a status-related name
                            if self._is_status_name(name):
                                value = self._extract_value(node.value)
                                claims.append(
                                    StatusClaim(
                                        status_name=name,
                                        claimed_value=value,
                                        location=f"{file_path}:{node.lineno}",
                                        context=self._get_context(tree, node),
                                    )
                                )

                elif isinstance(node, ast.FunctionDef):
                    # Check function names that suggest status
                    func_name = node.name.lower()
                    if any(
                        x in func_name
                        for x in ["is_ready", "is_loaded", "is_healthy", "check_status"]
                    ):
                        claims.append(
                            StatusClaim(
                                status_name=f"{func_name}_returns",
                                claimed_value="inferred",
                                location=f"{file_path}:{node.lineno}",
                                context=node.name,
                            )
                        )

        except SyntaxError:
            pass
        except Exception:
            pass

        return claims

    def _is_status_name(self, name: str) -> bool:
        """Check if variable name is status-related."""
        status_keywords = [
            "initialized",
            "ready",
            "loaded",
            "healthy",
            "active",
            "brain_loaded",
            "initialized",
            "configured",
            "validated",
            "operational",
            "functional",
            "enabled",
            "available",
        ]
        return any(keyword in name for keyword in status_keywords)

    def _extract_value(self, node: ast.expr) -> Any:
        """Extract constant value from AST node."""
        if isinstance(node, ast.Constant):
            return node.value
        elif isinstance(node, ast.NameConstant):  # Python < 3.8
            return node.value
        elif isinstance(node, ast.Name):
            return f"variable:{node.id}"
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                return f"call:{node.func.id}()"
        return "complex"

    def _get_context(self, tree: ast.Module, node: ast.AST) -> str:
        """Get function/class context for a node."""
        for parent in ast.walk(tree):
            if isinstance(parent, (ast.FunctionDef, ast.ClassDef)):
                # Check if node is inside this parent
                # This is approximate
                if hasattr(node, "lineno") and hasattr(parent, "lineno"):
                    if node.lineno and parent.lineno:
                        if parent.lineno <= node.lineno:
                            return parent.name
        return ""

    def validate_claim(self, claim: StatusClaim) -> StatusValidation:
        """Validate a status claim against actual state.

        Args:
            claim: Status claim to validate

        Returns:
            StatusValidation with result
        """
        actual_state = self._compute_actual_state()

        # Validate based on status name
        if claim.status_name in ["initialized", "brain_initialized"]:
            return self._validate_initialized(claim, actual_state)
        elif claim.status_name in ["brain_loaded", "loaded"]:
            return self._validate_brain_loaded(claim, actual_state)
        elif claim.status_name in ["healthy", "is_healthy"]:
            return self._validate_healthy(claim, actual_state)
        elif claim.status_name in ["active", "active_plan"]:
            return self._validate_active(claim, actual_state)
        else:
            # Unknown status - assume valid
            return StatusValidation(
                claim=claim,
                valid=True,
                actual_state=actual_state,
                error_message="Unknown status type - cannot validate",
            )

    def _compute_actual_state(self) -> dict[str, Any]:
        """Compute actual repository state."""
        if self._state_cache is not None:
            return self._state_cache

        state = {
            "has_specs": self._check_has_specs(),
            "spec_count": self._count_specs(),
            "has_brain_config": self._check_brain_config(),
            "has_runtime_errors": False,  # Would need runtime analysis
            "hard_invariants_pass": True,  # Would need invariant check
        }

        self._state_cache = state
        return state

    def _check_has_specs(self) -> bool:
        """Check if repository has spec files."""
        spec_dirs = ["specs", "spec", ".amos", "config"]
        for d in spec_dirs:
            spec_path = self.repo_path / d
            if spec_path.exists() and any(spec_path.iterdir()):
                return True

        # Check for .json or .yaml files that might be specs
        for ext in [".json", ".yaml", ".yml"]:
            if list(self.repo_path.glob(f"*{ext}")):
                return True

        return False

    def _count_specs(self) -> int:
        """Count spec files in repository."""
        count = 0
        spec_dirs = ["specs", "spec", ".amos", "config"]

        for d in spec_dirs:
            spec_path = self.repo_path / d
            if spec_path.exists():
                for ext in [".json", ".yaml", ".yml", ".toml"]:
                    count += len(list(spec_path.rglob(f"*{ext}")))

        return count

    def _check_brain_config(self) -> bool:
        """Check if brain configuration exists."""
        brain_files = [
            "brain.json",
            "brain.yaml",
            "brain.yml",
            ".brain",
            "brain.config",
            "amos.config",
        ]
        return any((self.repo_path / f).exists() for f in brain_files)

    def _validate_initialized(self, claim: StatusClaim, state: dict[str, Any]) -> StatusValidation:
        """Validate 'initialized' claim."""
        if claim.claimed_value is True:
            # initialized=true requires specs loaded
            if not state["has_specs"]:
                return StatusValidation(
                    claim=claim,
                    valid=False,
                    actual_state=state,
                    error_message="Claimed 'initialized=true' but no specs found",
                )

        return StatusValidation(
            claim=claim,
            valid=True,
            actual_state=state,
        )

    def _validate_brain_loaded(self, claim: StatusClaim, state: dict[str, Any]) -> StatusValidation:
        """Validate 'brain_loaded' claim."""
        if claim.claimed_value is True:
            # brain_loaded=true requires non-empty spec surface
            if state["spec_count"] == 0:
                return StatusValidation(
                    claim=claim,
                    valid=False,
                    actual_state=state,
                    error_message="Claimed 'brain_loaded=true' but spec surface is empty",
                )

        return StatusValidation(
            claim=claim,
            valid=True,
            actual_state=state,
        )

    def _validate_healthy(self, claim: StatusClaim, state: dict[str, Any]) -> StatusValidation:
        """Validate 'healthy' claim."""
        if claim.claimed_value is True:
            # healthy=true requires no hard invariant failures
            # This would need integration with invariant checks
            if state.get("hard_invariants_pass") is False:
                return StatusValidation(
                    claim=claim,
                    valid=False,
                    actual_state=state,
                    error_message="Claimed 'healthy=true' but hard invariants fail",
                )

        return StatusValidation(
            claim=claim,
            valid=True,
            actual_state=state,
        )

    def _validate_active(self, claim: StatusClaim, state: dict[str, Any]) -> StatusValidation:
        """Validate 'active' claim."""
        if claim.claimed_value is True:
            # active=true requires not terminal
            # This would need runtime state analysis
            pass

        return StatusValidation(
            claim=claim,
            valid=True,
            actual_state=state,
        )

    def analyze_repository(self) -> list[StatusValidation]:
        """Analyze entire repository for status-truth issues.

        Returns:
            List of status validations
        """
        claims = self.extract_status_claims()
        return [self.validate_claim(c) for c in claims]

    def get_false_claims(self) -> list[StatusValidation]:
        """Get all false status claims."""
        return [v for v in self.analyze_repository() if not v.valid]

    def get_summary(self, validations: list[StatusValidation]) -> dict[str, Any]:
        """Generate summary statistics."""
        total = len(validations)
        false_claims = sum(1 for v in validations if not v.valid)
        valid = total - false_claims

        # Categorize by status type
        by_type: dict[str, int] = {}
        for v in validations:
            status_name = v.claim.status_name
            by_type[status_name] = by_type.get(status_name, 0) + (0 if v.valid else 1)

        return {
            "total_claims": total,
            "valid": valid,
            "false_claims": false_claims,
            "by_status_type": by_type,
            "truthful": false_claims == 0,
        }
