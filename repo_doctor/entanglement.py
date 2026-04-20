"""
Entanglement Analysis Module - Dependency Entanglement Matrix

Tracks how modules co-fail and co-change:
    M_ij = alpha*import_link(i,j) + beta*test_coupling(i,j) + gamma*git_cochange(i,j)

High M_ij means:
- changes in i often destabilize j
- they should be tested together
- they should be bisected together
- they may need contract isolation
"""

from __future__ import annotations

import ast
import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass
class EntanglementEdge:
    """Represents entanglement between two modules."""

    module_a: str
    module_b: str
    import_weight: float
    test_weight: float
    git_weight: float
    total_weight: float


class EntanglementMatrix:
    """
    Computes the dependency entanglement matrix for a repository.

    M_ij = alpha*import_link(i,j) + beta*test_coupling(i,j) + gamma*git_cochange(i,j)
    """

    # Default coefficients
    ALPHA = 0.5  # Import coupling weight
    BETA = 0.3  # Test coupling weight
    GAMMA = 0.2  # Git co-change weight

    THRESHOLD = 0.3  # Threshold for high entanglement

    def __init__(self, repo_path: Union[str, Path]):
        self.repo_path = Path(repo_path).resolve()
        self.modules: set[str] = set()
        self.import_links: dict[tuple[str, str], float] = {}
        self.test_coupling: dict[tuple[str, str], float] = {}
        self.git_cochange: dict[tuple[str, str], float] = {}
        self.matrix: dict[tuple[str, str], float] = {}
        self.edges: list[EntanglementEdge] = []

    def analyze(self) -> list[EntanglementEdge]:
        """Compute full entanglement matrix."""
        self._collect_modules()
        self._compute_import_links()
        self._compute_test_coupling()
        self._compute_git_cochange()
        self._build_matrix()
        return self.edges

    def _collect_modules(self):
        """Collect all Python modules in the repo."""
        for py_file in self.repo_path.rglob("*.py"):
            if any(p.startswith(".") for p in py_file.relative_to(self.repo_path).parts):
                continue

            # Compute module name
            rel_path = py_file.relative_to(self.repo_path)
            parts = list(rel_path.parts)
            if py_file.name == "__init__.py":
                parts = parts[:-1]
            else:
                parts[-1] = py_file.stem

            module_name = ".".join(parts)
            self.modules.add(module_name)

    def _compute_import_links(self):
        """Compute import coupling between modules."""
        for py_file in self.repo_path.rglob("*.py"):
            if any(p.startswith(".") for p in py_file.relative_to(self.repo_path).parts):
                continue

            # Get source module name
            rel_path = py_file.relative_to(self.repo_path)
            source_module = self._path_to_module(rel_path)

            try:
                content = py_file.read_text()
                tree = ast.parse(content)

                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            target = alias.name.split(".")[0]
                            if target in self.modules and target != source_module:
                                key = tuple(sorted([source_module, target]))
                                self.import_links[key] = self.import_links.get(key, 0) + 1

                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            target = node.module.split(".")[0]
                            if target in self.modules and target != source_module:
                                key = tuple(sorted([source_module, target]))
                                self.import_links[key] = self.import_links.get(key, 0) + 1
            except Exception:
                pass

        # Normalize
        max_val = max(self.import_links.values()) if self.import_links else 1
        for key in self.import_links:
            self.import_links[key] /= max_val

    def _compute_test_coupling(self):
        """Compute test coupling - which modules are tested together."""
        test_dir = self.repo_path / "tests"
        if not test_dir.exists():
            return

        for test_file in test_dir.rglob("*.py"):
            try:
                content = test_file.read_text()
                tree = ast.parse(content)

                # Find all imports in this test file
                imported_modules = set()
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            mod = alias.name.split(".")[0]
                            if mod in self.modules:
                                imported_modules.add(mod)
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            mod = node.module.split(".")[0]
                            if mod in self.modules:
                                imported_modules.add(mod)

                # Create coupling between all modules tested together
                imported_list = list(imported_modules)
                for i in range(len(imported_list)):
                    for j in range(i + 1, len(imported_list)):
                        key = tuple(sorted([imported_list[i], imported_list[j]]))
                        self.test_coupling[key] = self.test_coupling.get(key, 0) + 1

            except Exception:
                pass

        # Normalize
        max_val = max(self.test_coupling.values()) if self.test_coupling else 1
        for key in self.test_coupling:
            self.test_coupling[key] /= max_val

    def _compute_git_cochange(self):
        """Compute git co-change frequency."""
        try:
            # Get commit history with file changes
            result = subprocess.run(
                ["git", "log", "--name-only", "--pretty=format:%H", "-50"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode != 0:
                return

            # Parse commits and files
            commits = result.stdout.split("\n\n")

            for commit in commits:
                lines = commit.strip().split("\n")
                if len(lines) < 2:
                    continue

                # Get files changed in this commit
                files = [l.strip() for l in lines[1:] if l.strip().endswith(".py")]
                modules_in_commit = []

                for f in files:
                    path = Path(f)
                    if path.suffix == ".py":
                        mod = self._path_to_module(path)
                        if mod in self.modules:
                            modules_in_commit.append(mod)

                # Create co-change edges
                for i in range(len(modules_in_commit)):
                    for j in range(i + 1, len(modules_in_commit)):
                        key = tuple(sorted([modules_in_commit[i], modules_in_commit[j]]))
                        self.git_cochange[key] = self.git_cochange.get(key, 0) + 1

            # Normalize
            max_val = max(self.git_cochange.values()) if self.git_cochange else 1
            for key in self.git_cochange:
                self.git_cochange[key] /= max_val

        except Exception:
            pass

    def _build_matrix(self):
        """Build the final entanglement matrix."""
        all_pairs = (
            set(self.import_links.keys())
            | set(self.test_coupling.keys())
            | set(self.git_cochange.keys())
        )

        for pair in all_pairs:
            import_w = self.import_links.get(pair, 0)
            test_w = self.test_coupling.get(pair, 0)
            git_w = self.git_cochange.get(pair, 0)

            total = self.ALPHA * import_w + self.BETA * test_w + self.GAMMA * git_w

            self.matrix[pair] = total

            if total >= self.THRESHOLD:
                self.edges.append(
                    EntanglementEdge(
                        module_a=pair[0],
                        module_b=pair[1],
                        import_weight=import_w,
                        test_weight=test_w,
                        git_weight=git_w,
                        total_weight=total,
                    )
                )

        # Sort by total weight
        self.edges.sort(key=lambda e: e.total_weight, reverse=True)

    def _path_to_module(self, path: Path) -> str:
        """Convert a file path to module name."""
        parts = list(path.parts)
        if path.name == "__init__.py":
            parts = parts[:-1]
        else:
            parts[-1] = path.stem
        return ".".join(parts)

    def get_high_entanglement_pairs(self, threshold: float = None) -> list[EntanglementEdge]:
        """Get pairs with entanglement above threshold."""
        thresh = threshold or self.THRESHOLD
        return [e for e in self.edges if e.total_weight >= thresh]

    def get_most_entangled(self, n: int = 10) -> list[EntanglementEdge]:
        """Get the n most entangled module pairs."""
        return self.edges[:n]

    def get_report(self) -> str:
        """Generate entanglement report."""
        lines = [
            "=" * 60,
            "ENTANGLEMENT MATRIX ANALYSIS",
            "=" * 60,
            f"Modules analyzed: {len(self.modules)}",
            f"Import links: {len(self.import_links)}",
            f"Test couplings: {len(self.test_coupling)}",
            f"Git co-changes: {len(self.git_cochange)}",
            f"High entanglement pairs (>{self.THRESHOLD}): {len(self.edges)}",
            "-" * 60,
        ]

        if self.edges:
            lines.append("TOP ENTANGLED MODULE PAIRS:")
            for edge in self.edges[:10]:
                lines.append(f"  {edge.module_a} <-> {edge.module_b}")
                lines.append(
                    f"    Total: {edge.total_weight:.2f} "
                    f"(import: {edge.import_weight:.2f}, "
                    f"test: {edge.test_weight:.2f}, "
                    f"git: {edge.git_weight:.2f})"
                )
        else:
            lines.append("No high-entanglement module pairs found")

        lines.append("=" * 60)

        return "\n".join(lines)
