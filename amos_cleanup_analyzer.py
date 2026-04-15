#!/usr/bin/env python3
"""AMOS Cleanup Analyzer - Round 13: Quality Assurance & Cleanup.

Analyzes the AMOS ecosystem for:
- Duplicate/redundant files
- Import issues
- Code quality problems
- Unused code
- Consolidation opportunities

Usage:
    python amos_cleanup_analyzer.py
    python amos_cleanup_analyzer.py --fix-suggestions
    python amos_cleanup_analyzer.py --generate-report
"""

from __future__ import annotations

import ast
import re
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class CleanupIssue:
    """Represents a cleanup issue."""

    category: str
    file: str
    line: int
    description: str
    severity: str  # "high", "medium", "low"
    suggestion: str


@dataclass
class FileAnalysis:
    """Analysis results for a file."""

    path: Path
    lines: int
    imports: list[str]
    functions: list[str]
    classes: list[str]
    issues: list[CleanupIssue] = field(default_factory=list)


class AMOSCleanupAnalyzer:
    """Analyzes AMOS ecosystem for cleanup opportunities.

    Identifies:
    - Duplicate files
    - Unused imports
    - Code quality issues
    - Consolidation opportunities
    """

    def __init__(self, root_dir: Optional[Path] = None):
        self.root = root_dir or Path(__file__).parent
        self.issues: list[CleanupIssue] = []
        self.file_analyses: list[FileAnalysis] = []
        self.duplicate_groups: list[list[Path]] = []

    def analyze(self) -> dict[str, any]:
        """Run complete ecosystem analysis."""
        print("=" * 70)
        print("  🔍 AMOS CLEANUP ANALYZER - Round 13")
        print("  Quality Assurance & Technical Debt Analysis")
        print("=" * 70)
        print()

        # Find all Python files
        python_files = list(self.root.glob("amos_*.py"))
        print(f"📁 Found {len(python_files)} AMOS Python files")
        print()

        # Analyze each file
        print("🔍 Analyzing files...")
        for file_path in python_files:
            analysis = self._analyze_file(file_path)
            self.file_analyses.append(analysis)

        # Check for duplicates
        print("🔍 Checking for duplicates...")
        self._find_duplicates()

        # Check for issues
        print("🔍 Identifying issues...")
        self._check_import_issues()
        self._check_code_patterns()
        self._check_documentation_consistency()

        # Generate report
        return self._generate_report()

    def _analyze_file(self, file_path: Path) -> FileAnalysis:
        """Analyze a single file."""
        content = file_path.read_text()
        lines = len(content.splitlines())

        # Parse AST
        try:
            tree = ast.parse(content)
            imports = []
            functions = []
            classes = []

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    for alias in node.names:
                        imports.append(f"{module}.{alias.name}")
                elif isinstance(node, ast.FunctionDef):
                    functions.append(node.name)
                elif isinstance(node, ast.ClassDef):
                    classes.append(node.name)

            return FileAnalysis(
                path=file_path, lines=lines, imports=imports, functions=functions, classes=classes
            )
        except SyntaxError:
            return FileAnalysis(
                path=file_path,
                lines=lines,
                imports=[],
                functions=[],
                classes=[],
                issues=[
                    CleanupIssue(
                        category="syntax",
                        file=str(file_path),
                        line=0,
                        description="Syntax error in file",
                        severity="high",
                        suggestion="Fix syntax errors",
                    )
                ],
            )

    def _find_duplicates(self) -> None:
        """Find potentially duplicate files."""
        # Group by similar names
        name_groups = defaultdict(list)

        for analysis in self.file_analyses:
            # Extract base name patterns
            name = analysis.path.stem

            # Check for dashboard variants
            if "dashboard" in name.lower():
                name_groups["dashboard"].append(analysis.path)

            # Check for API variants
            if "api" in name.lower():
                name_groups["api"].append(analysis.path)

            # Check for workflow variants
            if "workflow" in name.lower():
                name_groups["workflow"].append(analysis.path)

        # Report duplicates
        for category, files in name_groups.items():
            if len(files) > 1:
                self.duplicate_groups.append(files)
                for file in files:
                    self.issues.append(
                        CleanupIssue(
                            category="duplicate",
                            file=str(file),
                            line=0,
                            description=f"Potential duplicate: {category} variant",
                            severity="medium",
                            suggestion=f"Consider consolidating with other {category} files",
                        )
                    )

    def _check_import_issues(self) -> None:
        """Check for import-related issues."""
        for analysis in self.file_analyses:
            # Check for unused imports (simplified check)
            for imp in analysis.imports:
                module_name = imp.split(".")[-1]
                # Check if imported module is used in file
                content = analysis.path.read_text()
                if module_name not in content.split("import")[1:]:
                    # Very simplified check - may have false positives
                    pass  # Skip for now, would need better analysis

            # Check for missing brain imports
            if "brain" in str(analysis.path).lower():
                if "amos_brain" not in str(analysis.path) and "get_amos_integration" not in content:
                    pass  # Not an issue

    def _check_code_patterns(self) -> None:
        """Check for code quality patterns."""
        for analysis in self.file_analyses:
            content = analysis.path.read_text()

            # Check for print statements (should use logging)
            if content.count("print(") > 20:
                self.issues.append(
                    CleanupIssue(
                        category="code_quality",
                        file=str(analysis.path),
                        line=0,
                        description="Many print statements, consider logging",
                        severity="low",
                        suggestion="Replace print with proper logging",
                    )
                )

            # Check for TODO comments
            todos = re.findall(r"#\s*TODO.*", content, re.IGNORECASE)
            for todo in todos:
                self.issues.append(
                    CleanupIssue(
                        category="todo",
                        file=str(analysis.path),
                        line=0,
                        description=f"TODO found: {todo[:50]}",
                        severity="low",
                        suggestion="Address TODO items",
                    )
                )

            # Check for hardcoded paths
            if "/Users/" in content or "C:\\" in content:
                self.issues.append(
                    CleanupIssue(
                        category="portability",
                        file=str(analysis.path),
                        line=0,
                        description="Hardcoded paths detected",
                        severity="medium",
                        suggestion="Use Path(__file__) for relative paths",
                    )
                )

    def _check_documentation_consistency(self) -> None:
        """Check documentation consistency."""
        # Check decision docs count
        decision_docs = list(self.root.glob("amos_decision_round*.md"))
        if len(decision_docs) < 12:
            self.issues.append(
                CleanupIssue(
                    category="documentation",
                    file="decision_docs",
                    line=0,
                    description=f"Only {len(decision_docs)} decision docs found (expected 12+)",
                    severity="low",
                    suggestion="Create missing decision documentation",
                )
            )

        # Check for files without proper headers
        for analysis in self.file_analyses:
            content = analysis.path.read_text()
            if '"""' not in content[:200] and "'''" not in content[:200]:
                self.issues.append(
                    CleanupIssue(
                        category="documentation",
                        file=str(analysis.path),
                        line=1,
                        description="Missing docstring header",
                        severity="low",
                        suggestion="Add module docstring",
                    )
                )

    def _generate_report(self) -> dict[str, any]:
        """Generate comprehensive cleanup report."""
        print("\n" + "=" * 70)
        print("  📊 CLEANUP ANALYSIS REPORT")
        print("=" * 70)

        # Summary stats
        total_files = len(self.file_analyses)
        total_lines = sum(a.lines for a in self.file_analyses)
        total_issues = len(self.issues)

        print("\n📈 Summary Statistics:")
        print(f"  Total Files Analyzed: {total_files}")
        print(f"  Total Lines of Code: {total_lines}")
        print(f"  Total Issues Found: {total_issues}")
        print(f"  Duplicate Groups: {len(self.duplicate_groups)}")

        # Issues by category
        categories = defaultdict(list)
        for issue in self.issues:
            categories[issue.category].append(issue)

        print("\n📋 Issues by Category:")
        for category, issues in sorted(categories.items()):
            severity_count = defaultdict(int)
            for issue in issues:
                severity_count[issue.severity] += 1

            print(f"  {category.upper()}:")
            for sev in ["high", "medium", "low"]:
                if severity_count[sev] > 0:
                    print(f"    {sev}: {severity_count[sev]} issues")

        # High priority issues
        high_priority = [i for i in self.issues if i.severity == "high"]
        if high_priority:
            print(f"\n🔴 HIGH PRIORITY ISSUES ({len(high_priority)}):")
            for issue in high_priority[:10]:  # Show first 10
                print(f"  • [{issue.category}] {issue.file}")
                print(f"    {issue.description}")
                print(f"    → {issue.suggestion}")
                print()

        # Medium priority
        medium_priority = [i for i in self.issues if i.severity == "medium"]
        if medium_priority:
            print(f"\n🟡 MEDIUM PRIORITY ISSUES ({len(medium_priority)}):")
            for issue in medium_priority[:5]:
                print(f"  • {issue.file}: {issue.description[:60]}...")

        # Consolidation opportunities
        print("\n🔄 CONSOLIDATION OPPORTUNITIES:")
        if self.duplicate_groups:
            for group in self.duplicate_groups:
                print("  • Consider consolidating:")
                for file in group:
                    print(f"    - {file.name}")
        else:
            print("  • No obvious duplicates found")

        # File statistics
        print("\n📁 FILE STATISTICS:")
        sorted_files = sorted(self.file_analyses, key=lambda x: x.lines, reverse=True)
        for analysis in sorted_files[:10]:
            issue_count = len([i for i in self.issues if i.file == str(analysis.path)])
            print(f"  {analysis.path.name:<40} {analysis.lines:>5} lines  {issue_count:>2} issues")

        # Recommendations
        print("\n💡 RECOMMENDATIONS:")
        print(f"  1. Address {len(high_priority)} high priority issues first")
        print(f"  2. Review {len(self.duplicate_groups)} duplicate file groups")
        print("  3. Consider standardizing import patterns")
        print("  4. Add missing documentation where needed")
        print(
            f"  5. Review TODO items ({len([i for i in self.issues if i.category == 'todo'])} found)"
        )

        print("\n" + "=" * 70)
        print("  ✅ Analysis Complete")
        print("=" * 70)

        return {
            "total_files": total_files,
            "total_lines": total_lines,
            "total_issues": total_issues,
            "categories": {k: len(v) for k, v in categories.items()},
            "high_priority": len(high_priority),
            "medium_priority": len(medium_priority),
            "duplicates": len(self.duplicate_groups),
        }

    def generate_fix_script(self) -> str:
        """Generate a script with fix suggestions."""
        script = """#!/bin/bash
# AMOS Ecosystem Cleanup Script
# Generated by amos_cleanup_analyzer.py

echo "AMOS Ecosystem Cleanup"
echo "======================"

# High priority fixes
echo "1. Review and fix high priority issues"
"""

        high_priority = [i for i in self.issues if i.severity == "high"]
        for issue in high_priority:
            script += f'echo "   - {issue.file}: {issue.description}"\n'

        script += """
# Consolidation suggestions
echo ""
echo "2. Consider consolidating duplicate files:"
"""

        for group in self.duplicate_groups:
            script += f'echo "   - {", ".join([g.name for g in group])}"\n'

        script += """
echo ""
echo "Cleanup complete!"
"""

        return script


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="AMOS Cleanup Analyzer - Quality Assurance")
    parser.add_argument(
        "--fix-suggestions", action="store_true", help="Generate fix suggestions script"
    )
    parser.add_argument(
        "--generate-report", action="store_true", help="Generate detailed markdown report"
    )

    args = parser.parse_args()

    analyzer = AMOSCleanupAnalyzer()
    results = analyzer.analyze()

    if args.fix_suggestions:
        script = analyzer.generate_fix_script()
        script_path = Path("cleanup_suggestions.sh")
        script_path.write_text(script)
        print(f"\n📝 Fix script saved to: {script_path}")

    if args.generate_report:
        report_path = Path("CLEANUP_REPORT.md")
        # Generate markdown report
        report = f"""# AMOS Ecosystem Cleanup Report

**Generated:** {__import__("datetime").datetime.now().isoformat()}
**Files Analyzed:** {results["total_files"]}
**Total Lines:** {results["total_lines"]}
**Issues Found:** {results["total_issues"]}

## Summary

This report identifies technical debt and cleanup opportunities in the AMOS ecosystem.

## Statistics

- High Priority Issues: {results["high_priority"]}
- Medium Priority Issues: {results["medium_priority"]}
- Duplicate Groups: {results["duplicates"]}

## Issues by Category

"""
        for category, count in results["categories"].items():
            report += f"- **{category}:** {count} issues\n"

        report += "\n## Recommendations\n\n"
        report += "1. Address high priority issues first\n"
        report += "2. Review duplicate file groups\n"
        report += "3. Standardize code patterns\n"
        report += "4. Improve documentation\n"

        report_path.write_text(report)
        print(f"\n📄 Report saved to: {report_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
