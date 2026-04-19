"""
Evolution Opportunity Detector - Finds Recurring Weaknesses.

Uses Repo Doctor's own invariants to analyze the AMOS codebase itself,
detecting structural weaknesses suitable for self-evolution.

Detection Patterns:
- Repeated structural hotspots (monoliths, duplicates)
- Recurring manual fix patterns
- Unnecessary complexity
- Missing abstractions
- Performance bottlenecks
"""

import ast
import hashlib
from dataclasses import dataclass
from pathlib import Path


@dataclass
class StructuralHotspot:
    """A detected structural weakness suitable for evolution."""

    hotspot_id: str
    pattern_type: str
    location: str
    severity: float
    description: str
    recurrence_count: int
    suggested_evolution: str
    affected_files: List[str]


class EvolutionOpportunityDetector:
    """Detects self-evolution opportunities in the AMOS codebase."""

    PATTERN_THRESHOLD = 3  # Minimum recurrences to be considered

    def __init__(self, amos_root: str) -> None:
        """Initialize detector with AMOS codebase root."""
        self.amos_root = Path(amos_root)
        self.hotspots: List[StructuralHotspot] = []

    def detect_all(self) -> List[StructuralHotspot]:
        """Run all detection patterns and return hotspots."""
        self.hotspots = []

        # Detect duplicate code patterns
        self._detect_code_duplication()

        # Detect oversized modules
        self._detect_monoliths()

        # Detect missing abstractions
        self._detect_missing_abstractions()

        # Detect TODO/FIXME accumulation
        self._detect_deferred_work()

        # Detect import cycles
        self._detect_import_cycles()

        return self.hotspots

    # Common false positives to ignore
    IGNORED_PATTERNS = {
        # Dunder methods that legitimately appear everywhere
        "__init__",
        "__post_init__",
        "__repr__",
        "__str__",
        "__eq__",
        "__hash__",
        "__call__",
        "__enter__",
        "__exit__",
        "__iter__",
        "__next__",
        "__getitem__",
        "__setitem__",
        "__len__",
        "__contains__",
        "to_dict",
        "from_dict",
        "validate",
        "execute",
        "run",
        "check",
        "parse",
        "read",
        "write",
        "get",
        "set",
        "main",
        "setup",
        "teardown",
    }

    def _detect_code_duplication(self) -> None:
        """Detect repeated code patterns that should be unified."""
        py_files = list(self.amos_root.rglob("*.py"))

        # Simple AST-based duplicate detection
        function_signatures: dict[str, list[str]] = {}

        for file_path in py_files:
            if "__pycache__" in str(file_path) or ".venv" in str(file_path):
                continue

            # Skip test files - their duplication is expected
            if "test_" in str(file_path) or "_test" in str(file_path):
                continue

            try:
                content = file_path.read_text()
                tree = ast.parse(content)

                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        func_name = node.name

                        # Skip common false positives
                        if func_name in self.IGNORED_PATTERNS:
                            continue
                        if func_name.startswith("test_") or func_name.startswith("_"):
                            continue

                        # Only flag functions with meaningful bodies (not just pass)
                        if len(node.body) <= 1:
                            continue

                        # Create signature from function name and arg count
                        sig = f"{func_name}:{len(node.args.args)}:{len(node.body)}"
                        if sig not in function_signatures:
                            function_signatures[sig] = []
                        function_signatures[sig].append(str(file_path))

            except SyntaxError:
                continue

        # Find duplicates - require higher threshold and more files
        for sig, files in function_signatures.items():
            if len(files) >= self.PATTERN_THRESHOLD and len(files) <= 20:
                # Limit to reasonable number - too many is likely a false positive
                func_name = sig.split(":")[0]
                hotspot = StructuralHotspot(
                    hotspot_id=hashlib.md5(sig.encode()).hexdigest()[:8],
                    pattern_type="duplicate_function_signature",
                    location=f"Multiple files: {files[0]}",
                    severity=min(len(files) * 0.1, 1.0),
                    description=f"Function '{func_name}' with similar signature appears {len(files)} times",
                    recurrence_count=len(files),
                    suggested_evolution="Extract common function to shared module",
                    affected_files=files,
                )
                self.hotspots.append(hotspot)

    def _detect_monoliths(self) -> None:
        """Detect oversized modules that should be split."""
        py_files = list(self.amos_root.rglob("*.py"))

        for file_path in py_files:
            if "__pycache__" in str(file_path):
                continue

            try:
                content = file_path.read_text()
                lines = content.split("\n")
                line_count = len(lines)

                # Flag files over 500 lines
                if line_count > 500:
                    hotspot = StructuralHotspot(
                        hotspot_id=hashlib.md5(str(file_path).encode()).hexdigest()[:8],
                        pattern_type="monolithic_module",
                        location=str(file_path),
                        severity=min((line_count - 500) / 500, 1.0),
                        description=f"Module has {line_count} lines (threshold: 500)",
                        recurrence_count=1,
                        suggested_evolution="Split into focused submodules by responsibility",
                        affected_files=[str(file_path)],
                    )
                    self.hotspots.append(hotspot)

                # Count classes and functions
                tree = ast.parse(content)
                classes = [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
                functions = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]

                if len(classes) > 10 or len(functions) > 30:
                    hotspot = StructuralHotspot(
                        hotspot_id=hashlib.md5(f"{file_path}_complexity".encode()).hexdigest()[:8],
                        pattern_type="high_complexity",
                        location=str(file_path),
                        severity=min((len(classes) + len(functions)) / 50, 1.0),
                        description=f"Module has {len(classes)} classes and {len(functions)} functions",
                        recurrence_count=1,
                        suggested_evolution="Refactor into cohesive classes with single responsibility",
                        affected_files=[str(file_path)],
                    )
                    self.hotspots.append(hotspot)

            except SyntaxError:
                continue

    def _detect_missing_abstractions(self) -> None:
        """Detect repeated patterns that should be abstracted."""
        # Check for repeated string literals that should be constants
        string_patterns: dict[str, list[str]] = {}

        py_files = list(self.amos_root.rglob("*.py"))
        for file_path in py_files:
            if "__pycache__" in str(file_path):
                continue

            try:
                content = file_path.read_text()
                tree = ast.parse(content)

                for node in ast.walk(tree):
                    if isinstance(node, ast.Constant) and isinstance(node.value, str):
                        if len(node.value) > 10:  # Meaningful strings only
                            if node.value not in string_patterns:
                                string_patterns[node.value] = []
                            string_patterns[node.value].append(str(file_path))

            except SyntaxError:
                continue

        # Find repeated strings
        for string, files in string_patterns.items():
            if len(files) >= self.PATTERN_THRESHOLD and len(string) < 100:
                hotspot = StructuralHotspot(
                    hotspot_id=hashlib.md5(string.encode()).hexdigest()[:8],
                    pattern_type="repeated_literal",
                    location=files[0],
                    severity=min(len(files) * 0.15, 0.8),
                    description=f"String literal repeated {len(files)} times: '{string[:50]}...'",
                    recurrence_count=len(files),
                    suggested_evolution="Extract to named constant",
                    affected_files=list(set(files)),
                )
                self.hotspots.append(hotspot)

    def _detect_deferred_work(self) -> None:
        """Detect accumulation of TODO/FIXME comments."""
        py_files = list(self.amos_root.rglob("*.py"))

        for file_path in py_files:
            if "__pycache__" in str(file_path):
                continue

            try:
                content = file_path.read_text()
                todos = content.count("TODO") + content.count("FIXME") + content.count("XXX")

                if todos >= 5:
                    hotspot = StructuralHotspot(
                        hotspot_id=hashlib.md5(f"{file_path}_todos".encode()).hexdigest()[:8],
                        pattern_type="deferred_work_accumulation",
                        location=str(file_path),
                        severity=min(todos / 20, 1.0),
                        description=f"File has {todos} TODO/FIXME markers",
                        recurrence_count=todos,
                        suggested_evolution="Address deferred work or schedule explicit fixes",
                        affected_files=[str(file_path)],
                    )
                    self.hotspots.append(hotspot)

            except Exception:
                continue

    def _detect_import_cycles(self) -> None:
        """Detect circular import patterns."""
        # Build import graph
        imports: dict[str, list[str]] = {}

        py_files = list(self.amos_root.rglob("*.py"))
        for file_path in py_files:
            if "__pycache__" in str(file_path):
                continue

            try:
                content = file_path.read_text()
                tree = ast.parse(content)

                file_imports = []
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            file_imports.append(alias.name)
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            file_imports.append(node.module)

                imports[str(file_path)] = file_imports

            except SyntaxError:
                continue

        # Simple cycle detection (2-file cycles)
        for file1, imports1 in imports.items():
            for imp in imports1:
                for file2, imports2 in imports.items():
                    if file1 != file2:
                        for imp2 in imports2:
                            if file1 in imp2 and file2 in imp:
                                # Potential cycle
                                hotspot = StructuralHotspot(
                                    hotspot_id=hashlib.md5(f"{file1}{file2}".encode()).hexdigest()[
                                        :8
                                    ],
                                    pattern_type="import_cycle",
                                    location=f"{file1} <-> {file2}",
                                    severity=0.7,
                                    description="Potential circular import between modules",
                                    recurrence_count=1,
                                    suggested_evolution="Refactor to eliminate cycle (extract shared code)",
                                    affected_files=[file1, file2],
                                )
                                # Avoid duplicates
                                if not any(
                                    h.hotspot_id == hotspot.hotspot_id for h in self.hotspots
                                ):
                                    self.hotspots.append(hotspot)
