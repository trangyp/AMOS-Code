"""Built-in tools for AMOS SuperBrain.

Core tools that provide essential capabilities for the AMOS ecosystem.
These tools are registered during SuperBrain initialization.
"""

import json
import subprocess
from datetime import datetime, timezone
UTC = timezone.utc
from pathlib import Path
from typing import Any, Dict


def analyze_code_structure(file_path: str) -> Dict[str, Any]:
    """Analyze Python code structure and extract key information.

    Args:
        file_path: Path to the Python file to analyze

    Returns:
        Analysis results with functions, classes, imports
    """
    try:
        path = Path(file_path)
        if not path.exists():
            return {"error": f"File not found: {file_path}"}

        content = path.read_text(encoding="utf-8")
        lines = content.split("\n")

        # Simple analysis
        functions = []
        classes = []
        imports = []

        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped.startswith("def ") and "(" in stripped:
                func_name = stripped[4 : stripped.index("(")].strip()
                functions.append({"name": func_name, "line": i})
            elif stripped.startswith("class "):
                class_name = stripped[
                    6 : stripped.index(":") if ":" in stripped else len(stripped)
                ].strip()
                classes.append({"name": class_name, "line": i})
            elif stripped.startswith("import ") or stripped.startswith("from "):
                imports.append(stripped)

        return {
            "file": str(path),
            "total_lines": len(lines),
            "functions": functions,
            "classes": classes,
            "import_count": len(imports),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    except Exception as e:
        return {"error": str(e), "file": file_path}


def execute_shell_command(command: str, timeout: int = 30) -> Dict[str, Any]:
    """Execute a shell command safely.

    Args:
        command: Shell command to execute
        timeout: Maximum execution time in seconds

    Returns:
        Command output and status
    """
    import shlex

    try:
        # SECURITY: Use shell=False and shlex.split to prevent injection
        cmd_parts = shlex.split(command)
        result = subprocess.run(
            cmd_parts, shell=False, capture_output=True, text=True, timeout=timeout
        )
        return {
            "command": command,
            "returncode": result.returncode,
            "stdout": result.stdout[:1000],  # Limit output
            "stderr": result.stderr[:500],
            "success": result.returncode == 0,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    except subprocess.TimeoutExpired:
        return {"command": command, "error": f"Timeout after {timeout}s", "success": False}
    except Exception as e:
        return {"command": command, "error": str(e), "success": False}


def search_files(pattern: str, directory: str = ".", max_results: int = 20) -> Dict[str, Any]:
    """Search for files matching a pattern.

    Args:
        pattern: Glob pattern to search for
        directory: Directory to search in
        max_results: Maximum number of results

    Returns:
        Matching files with metadata
    """
    try:
        import fnmatch
        import os

        matches = []
        for root, dirs, files in os.walk(directory):
            # Skip common directories to avoid noise
            dirs[:] = [
                d
                for d in dirs
                if d not in {"node_modules", ".git", "__pycache__", ".venv", ".pytest_cache"}
            ]

            for filename in files:
                if fnmatch.fnmatch(filename, pattern):
                    full_path = os.path.join(root, filename)
                    try:
                        stat = os.stat(full_path)
                        matches.append(
                            {
                                "path": full_path,
                                "size": stat.st_size,
                                "modified": datetime.fromtimestamp(
                                    stat.st_mtime, tz=UTC
                                ).isoformat(),
                            }
                        )
                    except OSError:
                        matches.append({"path": full_path})

                    if len(matches) >= max_results:
                        break

            if len(matches) >= max_results:
                break

        return {
            "pattern": pattern,
            "directory": directory,
            "matches": matches,
            "count": len(matches),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    except Exception as e:
        return {"error": str(e), "pattern": pattern}


def get_system_info() -> Dict[str, Any]:
    """Get system information.

    Returns:
        System metrics and environment
    """
    import platform
    import sys

    return {
        "platform": platform.platform(),
        "python_version": sys.version,
        "python_executable": sys.executable,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def validate_json(data: str) -> Dict[str, Any]:
    """Validate and parse JSON data.

    Args:
        data: JSON string to validate

    Returns:
        Validation result
    """
    try:
        parsed = json.loads(data)
        return {
            "valid": True,
            "type": type(parsed).__name__,
            "keys": list(parsed.keys()) if isinstance(parsed, dict) else None,
            "length": len(parsed) if isinstance(parsed, (dict, list)) else None,
        }
    except json.JSONDecodeError as e:
        return {"valid": False, "error": str(e)}
    except Exception as e:
        return {"valid": False, "error": str(e)}


# Tool schemas for function calling
TOOL_SCHEMAS = {
    "analyze_code_structure": {
        "type": "object",
        "properties": {
            "file_path": {"type": "string", "description": "Path to the Python file to analyze"}
        },
        "required": ["file_path"],
    },
    "execute_shell_command": {
        "type": "object",
        "properties": {
            "command": {"type": "string", "description": "Shell command to execute"},
            "timeout": {
                "type": "integer",
                "description": "Timeout in seconds (default: 30)",
                "default": 30,
            },
        },
        "required": ["command"],
    },
    "search_files": {
        "type": "object",
        "properties": {
            "pattern": {
                "type": "string",
                "description": "Glob pattern to search for (e.g., '*.py')",
            },
            "directory": {
                "type": "string",
                "description": "Directory to search in (default: '.')",
                "default": ".",
            },
            "max_results": {
                "type": "integer",
                "description": "Maximum results (default: 20)",
                "default": 20,
            },
        },
        "required": ["pattern"],
    },
    "get_system_info": {"type": "object", "properties": {}, "required": []},
    "validate_json": {
        "type": "object",
        "properties": {"data": {"type": "string", "description": "JSON string to validate"}},
        "required": ["data"],
    },
}

TOOL_DESCRIPTIONS = {
    "analyze_code_structure": "Analyze Python code structure and extract functions, classes, and imports",
    "execute_shell_command": "Execute shell commands safely with timeout protection",
    "search_files": "Search for files matching a glob pattern",
    "get_system_info": "Get system information and environment details",
    "validate_json": "Validate and parse JSON data",
}
