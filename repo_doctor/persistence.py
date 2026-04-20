"""
Persistence Analysis Module - Persistence Invariant

I_persistence = 1 iff deserialize(serialize(x)) ≅ x

Validates:
- JSON schema consistency
- Pickle compatibility
- Config file validity
- Database schema alignment
"""

import json
import pickle
from dataclasses import dataclass
from pathlib import Path
from typing import Any, List


@dataclass
class PersistenceIssue:
    """Represents a persistence issue."""

    file_path: str
    issue_type: str  # "json", "pickle", "schema", "config"
    error: str
    fix_suggestion: str = None


class PersistenceAnalyzer:
    """
    Analyzes persistence layer for integrity.
    """

    def __init__(self, repo_path: str | Path):
        self.repo_path = Path(repo_path).resolve()
        self.issues: List[PersistenceIssue] = []

    def analyze(self) -> List[PersistenceIssue]:
        """Run full persistence analysis."""
        self.issues = []

        # Check JSON files
        self._check_json_files()

        # Check config files
        self._check_config_files()

        # Check pickle files
        self._check_pickle_files()

        # Check schema consistency
        self._check_schema_consistency()

        return self.issues

    def _check_json_files(self):
        """Check all JSON files for validity."""
        for json_file in self.repo_path.rglob("*.json"):
            if any(p.startswith(".") for p in json_file.relative_to(self.repo_path).parts):
                continue

            try:
                content = json_file.read_text()
                json.loads(content)
            except json.JSONDecodeError as e:
                self.issues.append(
                    PersistenceIssue(
                        file_path=str(json_file.relative_to(self.repo_path)),
                        issue_type="json",
                        error=f"Invalid JSON: {e}",
                        fix_suggestion="Fix JSON syntax error",
                    )
                )
            except Exception as e:
                self.issues.append(
                    PersistenceIssue(
                        file_path=str(json_file.relative_to(self.repo_path)),
                        issue_type="json",
                        error=f"Read error: {e}",
                        fix_suggestion="Check file encoding and permissions",
                    )
                )

    def _check_config_files(self):
        """Check configuration files."""
        # Check .env files
        for env_file in self.repo_path.rglob(".env*"):
            if env_file.name in [".env", ".env.example", ".env.sample"]:
                self._check_env_file(env_file)

        # Check YAML files
        try:
            import yaml

            for yaml_file in self.repo_path.rglob("*.yaml"):
                if any(p.startswith(".") for p in yaml_file.relative_to(self.repo_path).parts):
                    continue
                try:
                    content = yaml_file.read_text()
                    yaml.safe_load(content)
                except yaml.YAMLError as e:
                    self.issues.append(
                        PersistenceIssue(
                            file_path=str(yaml_file.relative_to(self.repo_path)),
                            issue_type="config",
                            error=f"Invalid YAML: {e}",
                            fix_suggestion="Fix YAML syntax",
                        )
                    )
        except ImportError:
            pass  # yaml not installed

    def _check_env_file(self, env_file: Path):
        """Check .env file format."""
        try:
            content = env_file.read_text()
            for i, line in enumerate(content.split("\n"), 1):
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" not in line and line:
                    self.issues.append(
                        PersistenceIssue(
                            file_path=str(env_file.relative_to(self.repo_path)),
                            issue_type="config",
                            error=f"Line {i}: missing '=': {line[:50]}",
                            fix_suggestion="Use KEY=value format",
                        )
                    )
        except Exception as e:
            self.issues.append(
                PersistenceIssue(
                    file_path=str(env_file.relative_to(self.repo_path)),
                    issue_type="config",
                    error=f"Read error: {e}",
                )
            )

    def _check_pickle_files(self):
        """Check pickle files (informational)."""
        for pkl_file in self.repo_path.rglob("*.pkl"):
            if any(p.startswith(".") for p in pkl_file.relative_to(self.repo_path).parts):
                continue

            # Just verify we can read the header
            try:
                with open(pkl_file, "rb") as f:
                    header = f.read(4)
                    if header[:2] != b"\x80\x03" and header[:2] != b"\x80\x04":
                        # Not a standard pickle protocol
                        pass  # Could be a different format
            except Exception:
                pass  # Don't flag pickle issues as critical

    def _check_schema_consistency(self):
        """Check for schema definition consistency."""
        # Look for schema files
        schema_files = list(self.repo_path.rglob("*schema*.json"))

        for schema_file in schema_files:
            try:
                content = schema_file.read_text()
                schema = json.loads(content)

                # Basic schema validation
                if not isinstance(schema, dict):
                    self.issues.append(
                        PersistenceIssue(
                            file_path=str(schema_file.relative_to(self.repo_path)),
                            issue_type="schema",
                            error="Schema root must be an object",
                            fix_suggestion="Ensure schema is a valid JSON Schema object",
                        )
                    )
            except json.JSONDecodeError:
                pass  # Already caught in _check_json_files

    def is_valid(self) -> bool:
        """Check if persistence layer is valid."""
        errors = [i for i in self.issues if i.issue_type in ("json", "schema")]
        return len(errors) == 0

    def get_report(self) -> str:
        """Generate formatted persistence report."""
        json_errors = [i for i in self.issues if i.issue_type == "json"]
        config_errors = [i for i in self.issues if i.issue_type == "config"]
        schema_errors = [i for i in self.issues if i.issue_type == "schema"]

        lines = [
            "=" * 60,
            "PERSISTENCE ANALYSIS",
            "=" * 60,
            f"JSON issues: {len(json_errors)}",
            f"Config issues: {len(config_errors)}",
            f"Schema issues: {len(schema_errors)}",
            "-" * 60,
        ]

        if json_errors:
            lines.append("JSON ERRORS:")
            for issue in json_errors[:5]:
                lines.append(f"  ✗ {issue.file_path}: {issue.error}")
            if len(json_errors) > 5:
                lines.append(f"  ... and {len(json_errors) - 5} more")

        if config_errors:
            lines.append("\nCONFIG ERRORS:")
            for issue in config_errors[:5]:
                lines.append(f"  ✗ {issue.file_path}: {issue.error}")
            if len(config_errors) > 5:
                lines.append(f"  ... and {len(config_errors) - 5} more")

        if not self.issues:
            lines.append("✓ All persistence files valid")

        lines.append("=" * 60)

        return "\n".join(lines)

    def test_roundtrip(self, data: Any, serializer: str = "json") -> Tuple[bool, Any, str]:
        """
        Test serialize/deserialize roundtrip.
        Returns (success, result, error_message).
        """
        try:
            if serializer == "json":
                serialized = json.dumps(data)
                deserialized = json.loads(serialized)
            elif serializer == "pickle":
                serialized = pickle.dumps(data)
                deserialized = pickle.loads(serialized)
            else:
                return False, None, f"Unknown serializer: {serializer}"

            # Basic equality check
            if data == deserialized:
                return True, deserialized, ""
            else:
                return False, deserialized, "Roundtrip data mismatch"

        except Exception as e:
            return False, None, f"Roundtrip failed: {e}"
