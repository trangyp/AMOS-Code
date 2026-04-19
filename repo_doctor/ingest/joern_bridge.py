"""
Joern Bridge - Code Property Graph Integration

Builds cross-language code property graphs with:
- Abstract Syntax Tree (AST)
- Control Flow Graph (CFG)
- Data Flow Graph (DFG)
- Taint analysis capabilities
"""

import json
import logging
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class CPGNode:
    """A node in the Code Property Graph."""

    id: int
    label: str
    properties: Dict[str, Any] = field(default_factory=dict)
    edges: List[CPGEdge] = field(default_factory=list)


@dataclass
class CPGEdge:
    """An edge in the Code Property Graph."""

    source: int
    target: int
    label: str
    properties: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CodePropertyGraph:
    """Complete CPG for a codebase."""

    nodes: dict[int, CPGNode] = field(default_factory=dict)
    edges: List[CPGEdge] = field(default_factory=list)
    language: str = "unknown"
    source_root: Optional[Path] = None

    def get_by_label(self, label: str) -> List[CPGNode]:
        """Get all nodes with a given label."""
        return [n for n in self.nodes.values() if n.label == label]

    def get_callers(self, method_name: str) -> List[CPGNode]:
        """Find all methods that call a given method."""
        # Requires DFG edges - placeholder
        return []

    def get_data_flows(self, source: str) -> list[dict[str, Any]]:
        """Find data flows from a given source."""
        # Requires taint analysis - placeholder
        return []


class JoernBridge:
    """
    Bridge to Joern code property graph analyzer.

    Features:
    - Build CPG from source code
    - Query with Cypher-like syntax
    - Taint analysis for security
    - Cross-language support (C, C++, Java, Python, JS)
    """

    def __init__(self, repo_path: Path, joern_cli: Optional[Path] = None):
        self.repo_path = Path(repo_path)
        self.joern_cli = joern_cli or self._find_joern()
        self.cpg_path: Optional[Path] = None
        self.current_cpg: Optional[CodePropertyGraph] = None
        self.cache_dir = self.repo_path / ".joern_cache"
        self.cache_dir.mkdir(exist_ok=True)

    def _find_joern(self) -> Optional[Path]:
        """Find Joern CLI in PATH."""
        try:
            result = subprocess.run(
                ["which", "joern"],
                capture_output=True,
                text=True,
                check=True,
            )
            return Path(result.stdout.strip())
        except (subprocess.CalledProcessError, FileNotFoundError):
            # Try common locations
            for path in [
                Path.home() / ".local/bin/joern",
                Path("/usr/local/bin/joern"),
                Path("/opt/joern/joern-cli/joern"),
            ]:
                if path.exists():
                    return path
            return None

    def is_available(self) -> bool:
        """Check if Joern CLI is available."""
        if not self.joern_cli:
            return False
        try:
            result = subprocess.run(
                [str(self.joern_cli), "--version"],
                capture_output=True,
                text=True,
            )
            return result.returncode == 0
        except Exception:
            return False

    def build_cpg(
        self, input_path: Optional[Path] = None, language: str = None
    ) -> Optional[CodePropertyGraph]:
        """
        Build Code Property Graph from source.

        Args:
        ----
            input_path: Path to analyze (defaults to repo_path)
            language: Language hint (c, cpp, java, python, javascript)

        Returns:
        -------
            CodePropertyGraph if successful

        """
        if not self.is_available():
            logger.warning("Joern CLI not available")
            return None

        input_path = input_path or self.repo_path
        cpg_name = f"{input_path.name}.cpg.bin"
        self.cpg_path = self.cache_dir / cpg_name

        # Remove existing CPG
        if self.cpg_path.exists():
            import shutil

            shutil.rmtree(self.cpg_path)

        try:
            # Build CPG using joern-parse
            parse_cmd = [
                str(self.joern_cli).replace("joern", "joern-parse"),
                str(input_path),
                "--output",
                str(self.cpg_path),
            ]

            if language:
                parse_cmd.extend(["--language", language])

            logger.info(f"Building CPG: {' '.join(parse_cmd)}")
            result = subprocess.run(
                parse_cmd,
                capture_output=True,
                text=True,
                timeout=300,
            )

            if result.returncode != 0:
                logger.error(f"CPG build failed: {result.stderr}")
                return None

            # Load and parse CPG
            self.current_cpg = self._load_cpg_from_binary(self.cpg_path, language)
            return self.current_cpg

        except subprocess.TimeoutExpired:
            logger.error("CPG build timed out")
            return None
        except Exception as e:
            logger.error(f"CPG build error: {e}")
            return None

    def _load_cpg_from_binary(self, cpg_path: Path, language: str) -> CodePropertyGraph:
        """Load CPG from binary file (placeholder)."""
        # Joern stores CPG in binary format
        # We would need to query it via joern console
        # For now, return empty CPG structure
        return CodePropertyGraph(
            language=language or "unknown",
            source_root=self.repo_path,
        )

    def query(self, cypher_query: str) -> list[dict[str, Any]]:
        """
        Execute Cypher query against CPG.

        Args:
        ----
            cypher_query: Cypher-like query string

        Returns:
        -------
            Query results as list of dictionaries

        """
        if not self.is_available() or not self.cpg_path:
            return []

        try:
            # Write query to script file
            script_path = self.cache_dir / "query.sc"
            script_path.write_text(
                f"""
importCpg("{self.cpg_path}")
{cypher_query}
            """
            )

            # Execute with joern
            cmd = [
                str(self.joern_cli),
                "--script",
                str(script_path),
                "--params",
                f"cpgPath={self.cpg_path}",
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60,
            )

            if result.returncode == 0:
                # Parse output (JSON if available)
                try:
                    return json.loads(result.stdout)
                except json.JSONDecodeError:
                    return [{"output": result.stdout}]
            else:
                logger.error(f"Query failed: {result.stderr}")
                return []

        except Exception as e:
            logger.error(f"Query error: {e}")
            return []

    def taint_analysis(self, sources: List[str], sinks: List[str]) -> list[dict[str, Any]]:
        """
        Run taint analysis from sources to sinks.

        Args:
        ----
            sources: List of source patterns (e.g., ["user_input", "request.params"])
            sinks: List of sink patterns (e.g., ["exec", "eval", "sql_query"])

        Returns:
        -------
            List of taint flows found

        """
        if not self.current_cpg:
            logger.warning("No CPG loaded. Run build_cpg() first.")
            return []

        # Joern taint analysis query
        query = f"""
        def sources = cpg.call.name("({"|".join(sources)})")
        def sinks = cpg.call.name("({"|".join(sinks)})")
        sinks.reachableBy(sources).p
        """

        return self.query(query)

    def find_dead_code(self) -> list[dict[str, Any]]:
        """Find unreachable/dead code."""
        query = """
        cpg.method.where(_.caller.isEmpty).name.p
        """
        return self.query(query)

    def find_complex_methods(self, complexity_threshold: int = 10) -> list[dict[str, Any]]:
        """Find methods with high cyclomatic complexity."""
        query = f"""
        cpg.method.filter(_.controlStructureCount > {complexity_threshold}).name.p
        """
        return self.query(query)

    def export_to_dot(self, output_path: Path) -> bool:
        """Export CPG to Graphviz DOT format."""
        if not self.cpg_path:
            return False

        try:
            query = f"""
            importCpg("{self.cpg_path}")
            cpg.method.take(100).plotDotCfg("{output_path}")
            """
            self.query(query)
            return output_path.exists()
        except Exception as e:
            logger.error(f"DOT export failed: {e}")
            return False
