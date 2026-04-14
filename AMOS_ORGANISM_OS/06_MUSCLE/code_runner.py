"""Code Runner — Execute code in various languages.
"""

from __future__ import annotations

import subprocess
import tempfile
import uuid
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


class Language(Enum):
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    BASH = "bash"


@dataclass
class CodeRunResult:
    """Result of running code."""

    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    language: str = ""
    code: str = ""
    stdout: str = ""
    stderr: str = ""
    success: bool = False
    execution_time_ms: int = 0


class CodeRunner:
    """Run code snippets in various languages safely."""

    RUNNERS = {
        Language.PYTHON: {
            "cmd": ["python3", "-c"],
            "ext": ".py",
        },
        Language.JAVASCRIPT: {
            "cmd": ["node", "-e"],
            "ext": ".js",
        },
        Language.BASH: {
            "cmd": ["bash", "-c"],
            "ext": ".sh",
        },
    }

    def __init__(self, allow_bash: bool = False):
        self.allow_bash = allow_bash
        self._temp_dir = Path(tempfile.gettempdir()) / "amos_code_runner"
        self._temp_dir.mkdir(parents=True, exist_ok=True)

    def run(
        self,
        code: str,
        language: Language = Language.PYTHON,
        timeout: int = 30,
    ) -> CodeRunResult:
        """Run code and return result."""
        result = CodeRunResult(language=language.value, code=code)

        if language == Language.BASH and not self.allow_bash:
            result.stderr = "Bash execution disabled for security"
            return result

        runner = self.RUNNERS.get(language)
        if not runner:
            result.stderr = f"Unsupported language: {language}"
            return result

        try:
            if language == Language.PYTHON:
                proc = subprocess.run(
                    runner["cmd"] + [code],
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                )
            else:
                # For other languages, use temp file
                temp_file = self._temp_dir / f"run_{uuid.uuid4().hex[:8]}{runner['ext']}"
                temp_file.write_text(code)
                cmd = runner["cmd"].copy()
                if language == Language.BASH:
                    cmd.append(code)
                else:
                    cmd.append(str(temp_file))
                proc = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                )
                temp_file.unlink(missing_ok=True)

            result.stdout = proc.stdout
            result.stderr = proc.stderr
            result.success = proc.returncode == 0
        except subprocess.TimeoutExpired:
            result.stderr = f"Execution timeout after {timeout}s"
        except Exception as e:
            result.stderr = str(e)

        return result

    def run_python(self, code: str, timeout: int = 30) -> CodeRunResult:
        """Convenience method for Python."""
        return self.run(code, Language.PYTHON, timeout)

    def run_bash(self, code: str, timeout: int = 30) -> CodeRunResult:
        """Convenience method for Bash."""
        return self.run(code, Language.BASH, timeout)
