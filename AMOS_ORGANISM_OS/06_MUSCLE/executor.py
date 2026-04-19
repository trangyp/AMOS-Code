"""Muscle Executor — The execution engine for AMOS."""

import json
import subprocess
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any


class ExecutionStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILURE = "failure"
    CANCELLED = "cancelled"


@dataclass
class ExecutionResult:
    """Result of an execution task."""

    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    command: str = ""
    status: ExecutionStatus = ExecutionStatus.PENDING
    stdout: str = ""
    stderr: str = ""
    return_code: int = 0
    start_time: str = ""
    end_time: str = ""
    duration_ms: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            **asdict(self),
            "status": self.status.value,
        }


@dataclass
class ExecutionContext:
    """Context for execution."""

    working_dir: Path = field(default_factory=Path.cwd)
    env_vars: Dict[str, str] = field(default_factory=dict)
    timeout_seconds: int = 60
    allow_shell: bool = False
    capture_output: bool = True


class MuscleExecutor:
    """The execution engine for AMOS MUSCLE subsystem.

    Responsibilities:
    - Execute shell commands safely
    - Run code in various languages
    - Manage execution contexts
    - Track execution history
    - Integrate with workflow engine
    """

    HISTORY_DIR = Path(__file__).parent / "execution_history"

    def __init__(self):
        self._history: List[ExecutionResult] = []
        self.HISTORY_DIR.mkdir(parents=True, exist_ok=True)

    def execute(
        self,
        command: str,
        context: ExecutionContext = None,
    ) -> ExecutionResult:
        """Execute a shell command safely."""
        ctx = context or ExecutionContext()
        result = ExecutionResult(command=command)
        result.start_time = datetime.now(UTC).isoformat()

        # Safety check
        if not ctx.allow_shell and self._is_dangerous(command):
            result.status = ExecutionStatus.CANCELLED
            result.stderr = "Command blocked by safety policy"
            result.end_time = datetime.now(UTC).isoformat()
            self._record(result)
            return result

        try:
            proc = subprocess.run(
                command,
                shell=True,
                cwd=ctx.working_dir,
                env={**dict(subprocess.os.environ), **ctx.env_vars},
                capture_output=ctx.capture_output,
                text=True,
                timeout=ctx.timeout_seconds,
            )
            result.stdout = proc.stdout
            result.stderr = proc.stderr
            result.return_code = proc.returncode
            result.status = (
                ExecutionStatus.SUCCESS if proc.returncode == 0 else ExecutionStatus.FAILURE
            )
        except subprocess.TimeoutExpired:
            result.status = ExecutionStatus.CANCELLED
            result.stderr = f"Timeout after {ctx.timeout_seconds}s"
        except Exception as e:
            result.status = ExecutionStatus.FAILURE
            result.stderr = str(e)

        result.end_time = datetime.now(UTC).isoformat()
        if result.start_time and result.end_time:
            start = datetime.fromisoformat(result.start_time)
            end = datetime.fromisoformat(result.end_time)
            result.duration_ms = int((end - start).total_seconds() * 1000)

        self._record(result)
        return result

    def _is_dangerous(self, command: str) -> bool:
        """Check if a command is potentially dangerous."""
        dangerous = [
            "rm -rf /",
            "rm -rf /*",
            "dd if=/dev/zero",
            ":(){ :|:& };:",
            "mkfs.",
            "format ",
            "> /dev/sda",
            "mv / /dev/null",
        ]
        cmd_lower = command.lower()
        return any(d in cmd_lower for d in dangerous)

    def _record(self, result: ExecutionResult):
        """Record execution result."""
        self._history.append(result)
        # Persist to file
        filepath = self.HISTORY_DIR / f"{result.id}.json"
        filepath.write_text(json.dumps(result.to_dict(), indent=2))

    def get_history(self, n: int = 10) -> List[ExecutionResult]:
        """Get recent execution history."""
        return self._history[-n:]

    def get_result(self, result_id: str) -> Optional[ExecutionResult]:
        """Get a specific execution result."""
        for r in self._history:
            if r.id == result_id:
                return r
        # Try to load from disk
        filepath = self.HISTORY_DIR / f"{result_id}.json"
        if filepath.exists():
            data = json.loads(filepath.read_text())
            data["status"] = ExecutionStatus(data["status"])
            return ExecutionResult(**data)
        return None

    def status(self) -> Dict[str, Any]:
        """Get executor status."""
        counts = dict.fromkeys(ExecutionStatus, 0)
        for r in self._history:
            counts[r.status] += 1
        return {
            "total_executions": len(self._history),
            "by_status": {k.value: v for k, v in counts.items()},
            "history_dir": str(self.HISTORY_DIR),
        }
