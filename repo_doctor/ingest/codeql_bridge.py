"""
CodeQL Bridge - Semantic Database Integration

Extracts semantic databases with AST, control-flow, and data-flow
for deep program analysis.
"""

from __future__ import annotations

import json
import logging
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class CodeQLDatabase:
    """A CodeQL database for a language."""

    language: str
    db_path: Path
    source_root: Path
    is_built: bool = False


@dataclass
class QueryResult:
    """Result of a CodeQL query."""

    query_name: str
    rows: list[dict[str, Any]] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    @property
    def count(self) -> int:
        return len(self.rows)


class CodeQLBridge:
    """
    Bridge to CodeQL semantic analysis.

    Features:
    - Create CodeQL databases from source
    - Run security/quality queries
    - Extract AST, CFG, data-flow information
    - Query results as structured data
    """

    def __init__(self, repo_path: Path, codeql_cli: Path | None = None):
        self.repo_path = Path(repo_path)
        self.codeql_cli = codeql_cli or self._find_codeql()
        self.databases: dict[str, CodeQLDatabase] = {}
        self.cache_dir = self.repo_path / ".codeql_cache"
        self.cache_dir.mkdir(exist_ok=True)

    def _find_codeql(self) -> Path | None:
        """Find CodeQL CLI in PATH."""
        try:
            result = subprocess.run(
                ["which", "codeql"],
                capture_output=True,
                text=True,
                check=True,
            )
            return Path(result.stdout.strip())
        except (subprocess.CalledProcessError, FileNotFoundError):
            # Try common locations
            for path in [
                Path.home() / ".local/bin/codeql",
                Path("/usr/local/bin/codeql"),
                Path("/opt/codeql/codeql"),
            ]:
                if path.exists():
                    return path
            return None

    def is_available(self) -> bool:
        """Check if CodeQL CLI is available."""
        if not self.codeql_cli:
            return False
        try:
            result = subprocess.run(
                [str(self.codeql_cli), "--version"],
                capture_output=True,
                text=True,
            )
            return result.returncode == 0
        except Exception:
            return False

    def create_database(self, language: str, db_name: str | None = None) -> CodeQLDatabase | None:
        """
        Create a CodeQL database for the repository.

        Args:
        ----
            language: Programming language (python, javascript, go, etc.)
            db_name: Name for the database (defaults to "{repo}_{lang}")

        Returns:
        -------
            CodeQLDatabase if successful

        """
        if not self.is_available():
            logger.warning("CodeQL CLI not available")
            return None

        if db_name is None:
            db_name = f"{self.repo_path.name}_{language}"

        db_path = self.cache_dir / db_name

        # Remove existing database
        if db_path.exists():
            import shutil

            shutil.rmtree(db_path)

        try:
            cmd = [
                str(self.codeql_cli),
                "database",
                "create",
                str(db_path),
                f"--language={language}",
                f"--source-root={self.repo_path}",
                "--overwrite",
            ]

            logger.info(f"Creating CodeQL database: {' '.join(cmd)}")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
            )

            if result.returncode == 0:
                db = CodeQLDatabase(
                    language=language,
                    db_path=db_path,
                    source_root=self.repo_path,
                    is_built=True,
                )
                self.databases[language] = db
                return db
            else:
                logger.error(f"CodeQL database creation failed: {result.stderr}")
                return None

        except subprocess.TimeoutExpired:
            logger.error("CodeQL database creation timed out")
            return None
        except Exception as e:
            logger.error(f"CodeQL database creation error: {e}")
            return None

    def run_query(
        self, database: CodeQLDatabase, query_file: Path, output_format: str = "json"
    ) -> QueryResult:
        """
        Run a CodeQL query against a database.

        Args:
        ----
            database: CodeQLDatabase to query
            query_file: Path to .ql query file
            output_format: Output format (json, csv, sarif)

        Returns:
        -------
            QueryResult with query output

        """
        if not self.is_available():
            return QueryResult(
                query_name=query_file.name,
                errors=["CodeQL CLI not available"],
            )

        output_path = self.cache_dir / f"{query_file.stem}_results.{output_format}"

        try:
            cmd = [
                str(self.codeql_cli),
                "query",
                "run",
                str(query_file),
                f"--database={database.db_path}",
                f"--output={output_path}",
                f"--format={output_format}",
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60,
            )

            if result.returncode == 0 and output_path.exists():
                if output_format == "json":
                    with open(output_path) as f:
                        data = json.load(f)
                    return QueryResult(
                        query_name=query_file.name,
                        rows=data.get("#select", {}).get("tuples", []),
                    )
                else:
                    return QueryResult(query_name=query_file.name)
            else:
                return QueryResult(
                    query_name=query_file.name,
                    errors=[result.stderr],
                )

        except Exception as e:
            return QueryResult(
                query_name=query_file.name,
                errors=[str(e)],
            )

    def run_security_queries(self, language: str = "python") -> dict[str, QueryResult]:
        """
        Run built-in security queries.

        Args:
        ----
            language: Language to analyze

        Returns:
        -------
            Dictionary mapping query names to results

        """
        if language not in self.databases:
            db = self.create_database(language)
            if not db:
                return {}

        database = self.databases[language]
        results = {}

        # Security query suites
        security_suites = [
            "codeql/{language}-queries/Security/CWE-020-ExternalAPIsUsedWithUntrustedData.ql",
            "codeql/{language}-queries/Security/CWE-078-CommandInjection.ql",
            "codeql/{language}-queries/Security/CWE-089-SQLInjection.ql",
            "codeql/{language}-queries/Security/CWE-094-CodeInjection.ql",
        ]

        for suite_template in security_suites:
            suite = suite_template.format(language=language)
            # These are built-in queries - need to reference properly
            # For now, use analyze command with security suite
            break

        # Use codeql analyze with security suite
        try:
            cmd = [
                str(self.codeql_cli),
                "database",
                "analyze",
                str(database.db_path),
                "--format=sarif-latest",
                f"--output={self.cache_dir / 'security_results.sarif'}",
                "--sarif-add-snippets",
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,
            )

            if result.returncode == 0:
                sarif_path = self.cache_dir / "security_results.sarif"
                if sarif_path.exists():
                    with open(sarif_path) as f:
                        sarif = json.load(f)

                    # Parse SARIF results
                    for run in sarif.get("runs", []):
                        for rule in run.get("tool", {}).get("driver", {}).get("rules", []):
                            rule_id = rule.get("id", "unknown")
                            results[rule_id] = QueryResult(
                                query_name=rule_id,
                                rows=run.get("results", []),
                            )

        except Exception as e:
            logger.error(f"Security analysis failed: {e}")

        return results

    def get_dataflow_graph(self, language: str = "python") -> dict[str, Any] | None:
        """
        Extract data-flow graph from CodeQL database.

        Returns
        -------
            Data-flow graph with sources, sinks, and flows

        """
        # This requires custom CodeQL queries
        # For now, return placeholder structure
        return {
            "sources": [],
            "sinks": [],
            "flows": [],
            "language": language,
        }
