#!/usr/bin/env python3
"""AMOS Project Scanner - Real Feature Using AMOS Brain.

Uses AMOS cognitive engine to analyze projects and provide recommendations.
"""

import ast
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

try:
    from amos_kernel.active_cognitive_engine import ActiveCognitiveEngine
except ImportError:
    # Fallback for circular import scenarios
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from active_cognitive_engine import ActiveCognitiveEngine


@dataclass
class ScanResult:
    """Result of scanning a file or project."""
    filepath: str
    issues: list[dict] = field(default_factory=list)
    metrics: dict = field(default_factory=dict)
    recommendations: list[str] = field(default_factory=list)


class ProjectScanner:
    """Scan Python projects using AMOS cognitive engine."""
    
    def __init__(self):
        self.engine = ActiveCognitiveEngine()
        self.results: list[ScanResult] = []
    
    def scan_file(self, filepath: str) -> ScanResult:
        """Scan a single Python file."""
        result = ScanResult(filepath=filepath)
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check syntax
            try:
                ast.parse(content)
                result.metrics['syntax_valid'] = True
            except SyntaxError as e:
                result.issues.append({
                    'type': 'syntax_error',
                    'message': str(e),
                    'severity': 'critical'
                })
                result.metrics['syntax_valid'] = False
            
            # Check for code quality issues
            lines = content.split('\n')
            
            # Long lines
            for i, line in enumerate(lines, 1):
                if len(line) > 100:
                    result.issues.append({
                        'type': 'long_line',
                        'line': i,
                        'length': len(line),
                        'severity': 'warning'
                    })
            
            # Bare except clauses
            for i, line in enumerate(lines, 1):
                if 'except:' in line and 'except Exception' not in line:
                    result.issues.append({
                        'type': 'bare_except',
                        'line': i,
                        'severity': 'error'
                    })
            
            # Missing docstrings
            if '"""' not in content[:200] and "'''" not in content[:200]:
                result.issues.append({
                    'type': 'missing_docstring',
                    'severity': 'warning'
                })
            
            # Calculate metrics
            result.metrics['total_lines'] = len(lines)
            result.metrics['code_lines'] = len([l for l in lines if l.strip() and not l.strip().startswith('#')])
            result.metrics['comment_lines'] = len([l for l in lines if l.strip().startswith('#')])
            
        except Exception as e:
            result.issues.append({
                'type': 'read_error',
                'message': str(e),
                'severity': 'error'
            })
        
        return result
    
    def scan_project(self, project_path: str) -> list[ScanResult]:
        """Scan entire project directory."""
        results = []
        
        for root, dirs, files in os.walk(project_path):
            # Skip virtual environments and cache
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['venv', '__pycache__']]
            
            for file in files:
                if file.endswith('.py'):
                    filepath = os.path.join(root, file)
                    result = self.scan_file(filepath)
                    results.append(result)
        
        self.results = results
        return results
    
    def generate_recommendations(self) -> list[str]:
        """Use AMOS cognitive engine to generate recommendations."""
        if not self.results:
            return []
        
        # Aggregate issues
        total_issues = sum(len(r.issues) for r in self.results)
        critical_issues = sum(1 for r in self.results for i in r.issues if i.get('severity') == 'critical')
        
        # Use AMOS to reason about priorities
        decision = self.engine.reason(
            f"Project has {total_issues} issues including {critical_issues} critical. What to prioritize?",
            {
                'assumptions': [
                    'Critical issues break functionality',
                    'Warnings reduce code quality',
                    'Syntax errors must be fixed first'
                ]
            }
        )
        
        recommendations = []
        
        if critical_issues > 0:
            recommendations.append(f"URGENT: Fix {critical_issues} critical syntax errors immediately")
        
        bare_excepts = sum(1 for r in self.results for i in r.issues if i.get('type') == 'bare_except')
        if bare_excepts > 0:
            recommendations.append(f"Fix {bare_excepts} bare except clauses for better error handling")
        
        long_lines = sum(1 for r in self.results for i in r.issues if i.get('type') == 'long_line')
        if long_lines > 0:
            recommendations.append(f"Refactor {long_lines} long lines for readability")
        
        missing_docs = sum(1 for r in self.results for i in r.issues if i.get('type') == 'missing_docstring')
        if missing_docs > 0:
            recommendations.append(f"Add docstrings to {missing_docs} files")
        
        # Add AMOS cognitive insight
        recommendations.append(f"AMOS Analysis: {decision['recommendation']}")
        
        return recommendations
    
    def print_report(self):
        """Print scan report."""
        print("="*70)
        print("AMOS PROJECT SCANNER - COGNITIVE ANALYSIS REPORT")
        print("="*70)
        
        total_files = len(self.results)
        total_issues = sum(len(r.issues) for r in self.results)
        
        print(f"\nFiles Scanned: {total_files}")
        print(f"Total Issues: {total_issues}")
        
        if self.results:
            total_lines = sum(r.metrics.get('total_lines', 0) for r in self.results)
            code_lines = sum(r.metrics.get('code_lines', 0) for r in self.results)
            print(f"Total Lines: {total_lines}")
            print(f"Code Lines: {code_lines}")
        
        print("\n" + "="*70)
        print("AMOS COGNITIVE RECOMMENDATIONS")
        print("="*70)
        
        recommendations = self.generate_recommendations()
        for i, rec in enumerate(recommendations, 1):
            print(f"{i}. {rec}")
        
        print("\n" + "="*70)


def main():
    """Run project scanner on current directory."""
    scanner = ProjectScanner()
    
    print("Scanning project with AMOS cognitive engine...")
    scanner.scan_project('.')
    scanner.print_report()


if __name__ == "__main__":
    main()
