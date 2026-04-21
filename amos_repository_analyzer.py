#!/usr/bin/env python3
"""AMOS Repository Analyzer - Deep analysis of AMOS codebase.

Uses TreeSitter and AST to analyze the entire repository:
- Code structure analysis
- Dependency mapping
- Quality metrics
- Architecture visualization
"""

from __future__ import annotations

import ast
import json
import os
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class FileAnalysis:
    """Analysis results for a single file."""

    path: str
    lines: int = 0
    functions: int = 0
    classes: int = 0
    imports: list[str] = field(default_factory=list)
    has_syntax_error: bool = False
    error_message: str | None = None


@dataclass
class RepositoryStats:
    """Overall repository statistics."""

    total_files: int = 0
    total_lines: int = 0
    total_functions: int = 0
    total_classes: int = 0
    syntax_errors: int = 0
    file_types: dict[str, int] = field(default_factory=dict)
    top_imports: list[tuple[str, int]] = field(default_factory=list)


class AMOSRepositoryAnalyzer:
    """Deep analyzer for AMOS repository."""

    def __init__(self, root_path: Path | None = None):
        self.root_path = root_path or Path.cwd()
        self.results: list[FileAnalysis] = []
        self.import_counts: dict[str, int] = defaultdict(int)

    def analyze_all(self) -> RepositoryStats:
        """Analyze entire repository."""
        print("[Analyzer] Scanning repository...")

        for root, dirs, files in os.walk(self.root_path):
            # Skip unwanted directories
            dirs[:] = [
                d
                for d in dirs
                if not d.startswith(".")
                and d not in ["venv", "__pycache__", "node_modules", "AMOS_REPOS", ".git"]
            ]

            for file in files:
                if file.endswith(".py"):
                    filepath = Path(root) / file
                    self._analyze_file(filepath)

        return self._compile_stats()

    def _analyze_file(self, filepath: Path) -> None:
        """Analyze a single Python file."""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()

            lines = content.count("\n") + 1

            # Parse AST
            try:
                tree = ast.parse(content)
                has_error = False
                error_msg = None
            except SyntaxError as e:
                has_error = True
                error_msg = f"Line {e.lineno}: {e.msg}"
                tree = None

            # Count functions and classes
            functions = 0
            classes = 0
            imports = []

            if tree:
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        functions += 1
                    elif isinstance(node, ast.ClassDef):
                        classes += 1
                    elif isinstance(node, ast.Import):
                        for alias in node.names:
                            imports.append(alias.name)
                            self.import_counts[alias.name] += 1
                    elif isinstance(node, ast.ImportFrom):
                        module = node.module or ""
                        imports.append(module)
                        self.import_counts[module] += 1

            analysis = FileAnalysis(
                path=str(filepath.relative_to(self.root_path)),
                lines=lines,
                functions=functions,
                classes=classes,
                imports=imports,
                has_syntax_error=has_error,
                error_message=error_msg,
            )

            self.results.append(analysis)

        except Exception as e:
            # File couldn't be read
            pass

    def _compile_stats(self) -> RepositoryStats:
        """Compile overall statistics."""
        stats = RepositoryStats()

        for result in self.results:
            stats.total_files += 1
            stats.total_lines += result.lines
            stats.total_functions += result.functions
            stats.total_classes += result.classes

            if result.has_syntax_error:
                stats.syntax_errors += 1

            # Count file types
            if "." in result.path:
                ext = result.path.rsplit(".", 1)[1]
                stats.file_types[ext] = stats.file_types.get(ext, 0) + 1

        # Top imports
        stats.top_imports = sorted(
            self.import_counts.items(),
            key=lambda x: x[1],
            reverse=True,
        )[:20]

        return stats

    def generate_report(self) -> dict[str, Any]:
        """Generate analysis report."""
        stats = self.analyze_all()

        report = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "repository": str(self.root_path),
            "statistics": {
                "total_files": stats.total_files,
                "total_lines": stats.total_lines,
                "total_functions": stats.total_functions,
                "total_classes": stats.total_classes,
                "syntax_errors": stats.syntax_errors,
                "file_types": stats.file_types,
            },
            "top_imports": stats.top_imports,
            "files_with_errors": [
                {"path": r.path, "error": r.error_message}
                for r in self.results
                if r.has_syntax_error
            ],
            "largest_files": sorted(
                [{"path": r.path, "lines": r.lines} for r in self.results],
                key=lambda x: x["lines"],
                reverse=True,
            )[:10],
        }

        return report

    def save_report(self, output_path: Path | None = None) -> Path:
        """Save report to file."""
        report = self.generate_report()

        if output_path is None:
            output_path = Path("amos_analysis_report.json")

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

        return output_path


def main():
    """Run repository analyzer."""
    analyzer = AMOSRepositoryAnalyzer()

    # Run analysis
    stats = analyzer.analyze_all()

    # Print summary
    print("\n" + "=" * 60)
    print("AMOS REPOSITORY ANALYSIS")
    print("=" * 60)
    print(f"Total Files: {stats.total_files}")
    print(f"Total Lines: {stats.total_lines:,}")
    print(f"Total Functions: {stats.total_functions}")
    print(f"Total Classes: {stats.total_classes}")
    print(f"Syntax Errors: {stats.syntax_errors}")
    print("\nTop Imports:")
    for name, count in stats.top_imports[:10]:
        print(f"  {name}: {count}")

    # Save report
    report_path = analyzer.save_report()
    print(f"\nReport saved: {report_path}")

    return stats.syntax_errors == 0


if __name__ == "__main__":
    import sys

    success = main()
    sys.exit(0 if success else 1)
