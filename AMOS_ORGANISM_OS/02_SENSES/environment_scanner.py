"""Environment Scanner — Filesystem and change detection for AMOS."""

import hashlib
import os
import subprocess
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Set

UTC = timezone.utc


@dataclass
class FileChange:
    """A detected file change."""

    path: str
    change_type: str  # created, modified, deleted, moved
    old_hash: str = ""
    new_hash: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    size_delta: int = 0


@dataclass
class ScanResult:
    """Result of an environment scan."""

    timestamp: str
    files_scanned: int
    changes: List[FileChange]
    new_files: List[str]
    modified_files: List[str]
    deleted_files: List[str]


class EnvironmentScanner:
    """Scans the filesystem and detects changes.

    Responsibilities:
    - Monitor filesystem for changes
    - Track file hashes for integrity
    - Detect new, modified, deleted files
    - Git status integration
    """

    def __init__(self, watch_paths: List[str] = None):
        self._watch_paths = watch_paths or ["."]
        self._file_hashes: Dict[str, str] = {}
        self._file_sizes: Dict[str, int] = {}
        self._last_scan: str = None
        self._ignore_patterns = [
            ".git",
            "__pycache__",
            "*.pyc",
            "*.pyo",
            ".DS_Store",
            "node_modules",
            ".env",
            "*.log",
            "*.tmp",
            ".pytest_cache",
        ]

    def _should_ignore(self, path: str) -> bool:
        """Check if path should be ignored."""
        for pattern in self._ignore_patterns:
            if pattern in path:
                return True
        return False

    def _compute_hash(self, filepath: str) -> str:
        """Compute MD5 hash of file."""
        try:
            with open(filepath, "rb") as f:
                return hashlib.md5(f.read()).hexdigest()[:16]
        except Exception:
            return ""

    def scan(self, path: str = None) -> ScanResult:
        """Scan environment for changes."""
        scan_path = path or self._watch_paths[0]
        changes = []
        new_files = []
        modified_files = []
        deleted_files = []
        current_files: Set[str] = set()

        # Walk directory
        files_scanned = 0
        for root, dirs, files in os.walk(scan_path):
            # Filter ignored directories
            dirs[:] = [d for d in dirs if not self._should_ignore(d)]

            for filename in files:
                if self._should_ignore(filename):
                    continue

                filepath = os.path.join(root, filename)
                current_files.add(filepath)
                files_scanned += 1

                # Compute hash
                file_hash = self._compute_hash(filepath)
                file_size = os.path.getsize(filepath)

                # Check for changes
                if filepath not in self._file_hashes:
                    changes.append(
                        FileChange(
                            path=filepath,
                            change_type="created",
                            new_hash=file_hash,
                            size_delta=file_size,
                        )
                    )
                    new_files.append(filepath)
                elif self._file_hashes[filepath] != file_hash:
                    old_size = self._file_sizes.get(filepath, 0)
                    changes.append(
                        FileChange(
                            path=filepath,
                            change_type="modified",
                            old_hash=self._file_hashes[filepath],
                            new_hash=file_hash,
                            size_delta=file_size - old_size,
                        )
                    )
                    modified_files.append(filepath)

                # Update tracking
                self._file_hashes[filepath] = file_hash
                self._file_sizes[filepath] = file_size

        # Check for deletions
        for old_file in set(self._file_hashes.keys()) - current_files:
            changes.append(
                FileChange(
                    path=old_file,
                    change_type="deleted",
                    old_hash=self._file_hashes[old_file],
                    size_delta=-self._file_sizes.get(old_file, 0),
                )
            )
            deleted_files.append(old_file)
            del self._file_hashes[old_file]
            if old_file in self._file_sizes:
                del self._file_sizes[old_file]

        self._last_scan = datetime.now(UTC).isoformat()

        return ScanResult(
            timestamp=self._last_scan,
            files_scanned=files_scanned,
            changes=changes,
            new_files=new_files,
            modified_files=modified_files,
            deleted_files=deleted_files,
        )

    def get_git_status(self) -> Dict[str, Any]:
        """Get git repository status."""
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True,
                timeout=10,
            )

            staged = []
            unstaged = []
            untracked = []

            for line in result.stdout.strip().split("\n"):
                if not line:
                    continue
                status_code = line[:2]
                filename = line[3:]

                if status_code[0] in "AMDRC":
                    staged.append(filename)
                if status_code[1] in "MD":
                    unstaged.append(filename)
                if status_code == "??":
                    untracked.append(filename)

            return {
                "is_repo": True,
                "branch": self._get_git_branch(),
                "staged": staged,
                "unstaged": unstaged,
                "untracked": untracked,
                "clean": len(staged) + len(unstaged) + len(untracked) == 0,
            }
        except Exception as e:
            return {"is_repo": False, "error": str(e)}

    def _get_git_branch(self) -> str:
        """Get current git branch."""
        try:
            result = subprocess.run(
                ["git", "branch", "--show-current"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            return result.stdout.strip()
        except Exception:
            return "unknown"

    def get_directory_summary(self, path: str = ".") -> Dict[str, Any]:
        """Get summary of directory contents."""
        try:
            total_files = 0
            total_dirs = 0
            total_size = 0
            extensions: Dict[str, int] = {}

            for root, dirs, files in os.walk(path):
                if self._should_ignore(root):
                    continue

                total_dirs += len(dirs)

                for f in files:
                    if self._should_ignore(f):
                        continue
                    total_files += 1
                    filepath = os.path.join(root, f)
                    try:
                        size = os.path.getsize(filepath)
                        total_size += size

                        # Count by extension
                        ext = Path(f).suffix or "no_extension"
                        extensions[ext] = extensions.get(ext, 0) + 1
                    except OSError:
                        pass

            return {
                "path": path,
                "total_files": total_files,
                "total_directories": total_dirs,
                "total_size_bytes": total_size,
                "extensions": dict(sorted(extensions.items(), key=lambda x: -x[1])[:10]),
            }
        except Exception as e:
            return {"error": str(e)}

    def status(self) -> Dict[str, Any]:
        """Get scanner status."""
        return {
            "watch_paths": self._watch_paths,
            "tracked_files": len(self._file_hashes),
            "last_scan": self._last_scan,
            "ignore_patterns": len(self._ignore_patterns),
        }
