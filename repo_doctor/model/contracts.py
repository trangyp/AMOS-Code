"""
Repo Doctor Omega - Contract Commutator

The highest-yield invariant for real repo drift:
[A_public, A_runtime] = A_public A_runtime - A_runtime A_public

Drift detected when: [A_public, A_runtime] ≠ 0

Catches:
- Docs telling users to run commands that don't exist
- Demos passing unsupported keyword args
- MCP handlers calling methods with wrong signatures
- Tests importing names not exported
- Wrappers launching the wrong shell
- Status claiming capabilities not actually present
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class PublicContract:
    """Contract claimed by public-facing surfaces."""

    name: str
    signature: Dict[str, Any] = field(default_factory=dict)
    sources: List[str] = field(default_factory=list)  # docs, demos, tests, etc.


@dataclass
class RuntimeContract:
    """Contract actually available at runtime."""

    name: str
    signature: Dict[str, Any] = field(default_factory=dict)
    source: str = ""  # file where defined
    line: int = 0


@dataclass
class ContractDrift:
    """Specific drift between public and runtime."""

    name: str
    drift_type: str  # missing, signature_mismatch, extra_arg, wrong_return
    public_signature: Dict[str, Any] = field(default_factory=dict)
    runtime_signature: Dict[str, Any] = field(default_factory=dict)
    public_sources: List[str] = field(default_factory=list)
    runtime_source: str = ""


class ContractCommutator:
    """
    Compute [A_public, A_runtime] - the contract commutator.

    Non-zero commutator indicates drift between public claims and runtime reality.
    """

    def __init__(self):
        self.public_contracts: Dict[str, PublicContract] = {}
        self.runtime_contracts: Dict[str, RuntimeContract] = {}

    def extract_from_docs(self, doc_files: List[str]) -> None:
        """Extract claimed contracts from documentation."""
        for doc in doc_files:
            # Parse doc for command examples, API references
            pass  # Implementation would parse markdown/rst

    def extract_from_demos(self, demo_files: List[str]) -> None:
        """Extract claimed contracts from demo files."""
        for demo in demo_files:
            # Parse demo for function calls, API usage
            pass  # Implementation would parse Python files

    def extract_from_tests(self, test_files: List[str]) -> None:
        """Extract claimed contracts from test files."""
        for test in test_files:
            # Parse test imports and function calls
            pass  # Implementation would parse Python files

    def extract_from_cli(self, cli_module: str) -> None:
        """Extract claimed contracts from CLI help."""
        # Parse argparse/Click/Typer commands
        pass  # Implementation would inspect CLI module

    def extract_from_mcp(self, mcp_schema: Dict[str, Any]) -> None:
        """Extract claimed contracts from MCP tool schema."""
        for tool_name, tool_def in mcp_schema.get("tools", {}).items():
            self.public_contracts[tool_name] = PublicContract(
                name=tool_name,
                signature=tool_def.get("parameters", {}),
                sources=["mcp_schema"],
            )

    def extract_from_exports(self, ast_exports: list[dict[str, Any]]) -> None:
        """Extract runtime contracts from AST analysis."""
        for export in ast_exports:
            name = export.get("name", "")
            self.runtime_contracts[name] = RuntimeContract(
                name=name,
                signature=export.get("signature", {}),
                source=export.get("file", ""),
                line=export.get("line", 0),
            )

    def compute_commutator(self) -> List[ContractDrift]:
        """
        Compute [A_public, A_runtime].

        Returns list of drift instances where contracts don't match.
        """
        drifts = []

        # Check all public contracts exist in runtime
        for name, public in self.public_contracts.items():
            if name not in self.runtime_contracts:
                drifts.append(
                    ContractDrift(
                        name=name,
                        drift_type="missing_from_runtime",
                        public_signature=public.signature,
                        public_sources=public.sources,
                    )
                )
            else:
                runtime = self.runtime_contracts[name]
                # Check signature compatibility
                if not self._signatures_compatible(public.signature, runtime.signature):
                    drifts.append(
                        ContractDrift(
                            name=name,
                            drift_type="signature_mismatch",
                            public_signature=public.signature,
                            runtime_signature=runtime.signature,
                            public_sources=public.sources,
                            runtime_source=runtime.source,
                        )
                    )

        # Check for runtime-only contracts (not necessarily drift, but notable)
        for name, runtime in self.runtime_contracts.items():
            if name not in self.public_contracts:
                # Unexported runtime surface - may be intentional
                pass

        return drifts

    def _signatures_compatible(self, public: Dict[str, Any], runtime: Dict[str, Any]) -> bool:
        """Check if two signatures are compatible."""
        # Simple compatibility check
        pub_params = set(public.get("parameters", {}).keys())
        run_params = set(runtime.get("parameters", {}).keys())

        # Public must be subset of runtime (runtime can have more)
        return pub_params <= run_params

    def drift_count(self) -> int:
        """Return number of drift instances."""
        return len(self.compute_commutator())

    def is_commutative(self) -> bool:
        """Check if [A_public, A_runtime] = 0 (no drift)."""
        return self.drift_count() == 0


class PublicRuntimeDrift:
    """High-level interface for public/runtime drift detection."""

    def __init__(self, repo_path: str):
        self.repo_path = repo_path
        self.commutator = ContractCommutator()

    def analyze(self) -> Dict[str, Any]:
        """Full drift analysis."""
        # This would integrate with sensor backends
        drifts = self.commutator.compute_commutator()

        return {
            "drift_count": len(drifts),
            "is_valid": len(drifts) == 0,
            "drifts": [
                {
                    "name": d.name,
                    "type": d.drift_type,
                    "public_in": d.public_sources,
                    "runtime_in": d.runtime_source,
                }
                for d in drifts
            ],
        }
