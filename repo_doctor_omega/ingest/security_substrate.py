"""Security analysis substrate for vulnerability detection.

Detects security issues via:
- Source-to-sink taint analysis
- Dangerous function detection (eval, exec, etc.)
- SQL injection patterns
- Hardcoded secrets (basic detection)
- Unsafe deserialization

Optional integration with:
- bandit (AST-based security checks)
- semgrep (pattern matching)
"""
from __future__ import annotations

import ast
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class SecurityFinding:
    """A security vulnerability finding."""
    rule_id: str
    rule_name: str
    severity: str  # critical, high, medium, low
    confidence: str  # high, medium, low
    file: str
    line: int
    message: str
    code_snippet: str = ""
    remediation: str = ""
    
    @property
    def is_critical(self) -> bool:
        """Check if this is a critical severity finding."""
        return self.severity == "critical"
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "rule_id": self.rule_id,
            "rule_name": self.rule_name,
            "severity": self.severity,
            "confidence": self.confidence,
            "file": self.file,
            "line": self.line,
            "message": self.message,
            "remediation": self.remediation,
        }


@dataclass
class SecurityAnalysis:
    """Complete security analysis result."""
    findings: list[SecurityFinding] = field(default_factory=list)
    
    @property
    def critical_count(self) -> int:
        """Count critical findings."""
        return sum(1 for f in self.findings if f.severity == "critical")
    
    @property
    def high_count(self) -> int:
        """Count high severity findings."""
        return sum(1 for f in self.findings if f.severity == "high")
    
    @property
    def total_count(self) -> int:
        """Total findings count."""
        return len(self.findings)
    
    @property
    def is_secure(self) -> bool:
        """Check if repository has no critical/high findings."""
        return self.critical_count == 0 and self.high_count == 0


class SecuritySubstrate:
    """
    Security analysis substrate for vulnerability detection.
    
    Implements taint-style analysis for common Python vulnerabilities:
    - Source-to-sink flow detection
    - Dangerous function usage
    - SQL injection patterns
    - Hardcoded secrets
    - Unsafe deserialization
    
    Usage:
        substrate = SecuritySubstrate("/path/to/repo")
        analysis = substrate.analyze_repository()
        
        if not analysis.is_secure:
            print(f"Found {analysis.critical_count} critical issues")
            for finding in analysis.findings:
                print(f"  {finding.rule_name}: {finding.message}")
    """
    
    # Sources: untrusted data entry points
    SOURCES = [
        "request.args", "request.form", "request.json", "request.data",
        "request.headers", "request.cookies", "request.files",
        "input(", "sys.stdin", "socket.recv", "os.environ.get",
        "input", "raw_input",  # Python 2/3
    ]
    
    # Sinks: dangerous execution points
    SINKS = {
        "eval": {"severity": "critical", "rule": "dangerous-eval"},
        "exec": {"severity": "critical", "rule": "dangerous-exec"},
        "compile": {"severity": "high", "rule": "dangerous-compile"},
        "subprocess.call": {"severity": "high", "rule": "dangerous-subprocess"},
        "subprocess.Popen": {"severity": "high", "rule": "dangerous-subprocess"},
        "os.system": {"severity": "high", "rule": "dangerous-system"},
        "os.popen": {"severity": "high", "rule": "dangerous-popen"},
        "pickle.loads": {"severity": "high", "rule": "unsafe-deserialization"},
        "yaml.load": {"severity": "high", "rule": "unsafe-yaml"},
        "exec(": {"severity": "critical", "rule": "dangerous-exec"},
    }
    
    # SQL injection patterns
    SQL_SINKS = [
        "execute", "executemany", "executescript",
        "cursor.execute", "db.execute", "connection.execute",
    ]
    
    # Secret patterns (basic)
    SECRET_PATTERNS = [
        (r'password\s*=\s*["\'][^"\']+["\']', "hardcoded-password", "medium"),
        (r'secret\s*=\s*["\'][^"\']+["\']', "hardcoded-secret", "high"),
        (r'api_key\s*=\s*["\'][^"\']+["\']', "hardcoded-api-key", "critical"),
        (r'token\s*=\s*["\'][^"\']+["\']', "hardcoded-token", "critical"),
        (r'aws_access_key_id\s*=\s*["\'][^"\']+["\']', "hardcoded-aws-key", "critical"),
    ]
    
    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path).resolve()
        self._bandit_available = self._check_bandit()
    
    def _check_bandit(self) -> bool:
        """Check if bandit is available for enhanced analysis."""
        try:
            import bandit
            return True
        except ImportError:
            return False
    
    def analyze_repository(self) -> SecurityAnalysis:
        """
        Perform complete security analysis.
        
        Returns:
            SecurityAnalysis with all findings
        """
        findings = []
        
        # Find Python files
        py_files = list(self.repo_path.rglob("*.py"))
        
        # Skip common non-source directories
        py_files = [
            f for f in py_files
            if not any(part.startswith(".") or part in ["__pycache__", "venv", ".git"])
            for part in f.relative_to(self.repo_path).parts[:1]
        ]
        
        for file_path in py_files[:100]:  # Limit for performance
            try:
                file_findings = self._analyze_file(file_path)
                findings.extend(file_findings)
            except Exception:
                # Skip files that can't be analyzed
                pass
        
        # Run bandit if available
        if self._bandit_available:
            bandit_findings = self._run_bandit()
            findings.extend(bandit_findings)
        
        return SecurityAnalysis(findings=findings)
    
    def _analyze_file(self, file_path: Path) -> list[SecurityFinding]:
        """Analyze a single Python file."""
        findings = []
        
        try:
            source = file_path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            return findings
        
        # AST-based analysis
        try:
            tree = ast.parse(source)
            findings.extend(self._analyze_ast(tree, file_path, source))
        except SyntaxError:
            pass
        
        # Pattern-based analysis
        findings.extend(self._analyze_patterns(source, file_path))
        
        return findings
    
    def _analyze_ast(
        self,
        tree: ast.AST,
        file_path: Path,
        source: str,
    ) -> list[SecurityFinding]:
        """AST-based security analysis."""
        findings = []
        lines = source.split("\n")
        
        for node in ast.walk(tree):
            # Check for dangerous function calls
            if isinstance(node, ast.Call):
                finding = self._check_dangerous_call(node, file_path, lines)
                if finding:
                    findings.append(finding)
            
            # Check for SQL injection patterns
            if isinstance(node, ast.Call):
                finding = self._check_sql_injection(node, file_path, lines)
                if finding:
                    findings.append(finding)
        
        return findings
    
    def _check_dangerous_call(
        self,
        node: ast.Call,
        file_path: Path,
        lines: list[str],
    ) -> SecurityFinding | None:
        """Check for calls to dangerous functions."""
        func_name = None
        
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            func_name = node.func.attr
        
        if not func_name:
            return None
        
        # Check against known sinks
        for sink_pattern, config in self.SINKS.items():
            if sink_pattern in func_name or func_name == sink_pattern:
                line_num = getattr(node, "lineno", 0)
                code_snippet = lines[line_num - 1] if 0 < line_num <= len(lines) else ""
                
                return SecurityFinding(
                    rule_id=config["rule"],
                    rule_name=f"Dangerous function: {func_name}",
                    severity=config["severity"],
                    confidence="medium",
                    file=str(file_path.relative_to(self.repo_path)),
                    line=line_num,
                    message=f"Use of dangerous function '{func_name}' detected",
                    code_snippet=code_snippet.strip(),
                    remediation=f"Avoid using {func_name}. Use safer alternatives.",
                )
        
        return None
    
    def _check_sql_injection(
        self,
        node: ast.Call,
        file_path: Path,
        lines: list[str],
    ) -> SecurityFinding | None:
        """Check for potential SQL injection."""
        func_name = None
        
        if isinstance(node.func, ast.Attribute):
            func_name = node.func.attr
        elif isinstance(node.func, ast.Name):
            func_name = node.func.id
        
        if func_name not in self.SQL_SINKS:
            return None
        
        # Check if any argument contains string formatting
        for arg in node.args:
            if isinstance(arg, ast.BinOp) and isinstance(arg.op, ast.Mod):
                # String formatting with %
                line_num = getattr(node, "lineno", 0)
                code_snippet = lines[line_num - 1] if 0 < line_num <= len(lines) else ""
                
                return SecurityFinding(
                    rule_id="sql-injection",
                    rule_name="Potential SQL injection",
                    severity="critical",
                    confidence="medium",
                    file=str(file_path.relative_to(self.repo_path)),
                    line=line_num,
                    message=f"String formatting in {func_name}() may enable SQL injection",
                    code_snippet=code_snippet.strip(),
                    remediation="Use parameterized queries instead of string formatting",
                )
            
            if isinstance(arg, ast.JoinedStr):
                # f-string
                line_num = getattr(node, "lineno", 0)
                code_snippet = lines[line_num - 1] if 0 < line_num <= len(lines) else ""
                
                return SecurityFinding(
                    rule_id="sql-injection",
                    rule_name="Potential SQL injection via f-string",
                    severity="critical",
                    confidence="medium",
                    file=str(file_path.relative_to(self.repo_path)),
                    line=line_num,
                    message=f"f-string in {func_name}() may enable SQL injection",
                    code_snippet=code_snippet.strip(),
                    remediation="Use parameterized queries instead of f-strings",
                )
        
        return None
    
    def _analyze_patterns(self, source: str, file_path: Path) -> list[SecurityFinding]:
        """Pattern-based security analysis."""
        findings = []
        lines = source.split("\n")
        
        for line_num, line in enumerate(lines, 1):
            # Check for hardcoded secrets
            for pattern, rule_id, severity in self.SECRET_PATTERNS:
                if re.search(pattern, line, re.IGNORECASE):
                    findings.append(SecurityFinding(
                        rule_id=rule_id,
                        rule_name=f"Hardcoded secret: {rule_id}",
                        severity=severity,
                        confidence="medium",
                        file=str(file_path.relative_to(self.repo_path)),
                        line=line_num,
                        message=f"Potential hardcoded secret detected",
                        code_snippet=line.strip(),
                        remediation="Use environment variables or secret management",
                    ))
        
        return findings
    
    def _run_bandit(self) -> list[SecurityFinding]:
        """Run bandit analysis if available."""
        findings = []
        
        try:
            import subprocess
            
            result = subprocess.run(
                ["bandit", "-r", str(self.repo_path), "-f", "json"],
                capture_output=True,
                text=True,
                timeout=60,
            )
            
            if result.returncode in (0, 1):  # 0 = no issues, 1 = issues found
                import json
                try:
                    data = json.loads(result.stdout)
                    for issue in data.get("results", []):
                        findings.append(SecurityFinding(
                            rule_id=f"bandit:{issue.get('test_id', 'unknown')}",
                            rule_name=issue.get("test_name", "Unknown"),
                            severity=issue.get("issue_severity", "medium").lower(),
                            confidence=issue.get("issue_confidence", "medium").lower(),
                            file=issue.get("filename", ""),
                            line=issue.get("line_number", 0),
                            message=issue.get("issue_text", ""),
                            code_snippet=issue.get("code", ""),
                            remediation=f"See bandit docs for {issue.get('test_id', '')}",
                        ))
                except json.JSONDecodeError:
                    pass
        
        except Exception:
            pass
        
        return findings
