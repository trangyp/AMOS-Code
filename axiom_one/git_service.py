"""Git Service for Axiom One"""

import subprocess
from datetime import datetime, timezone
UTC = timezone.utc, timezone

UTC = UTC
from pathlib import Path

from fastapi import HTTPException

from axiom_one.models import Branch, Commit, FileNode, FileNodeType


class GitService:
    def __init__(self, repo_base_path: Path):
        self.repo_base_path = repo_base_path

    def _run_git(self, repo_id: str, *args: str) -> Tuple[int, str, str]:
        repo_path = self.repo_base_path / repo_id
        try:
            result = subprocess.run(
                ["git"] + list(args),
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=30,
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return -1, "", "Command timed out"
        except FileNotFoundError:
            return -1, "", "Git not found"

    def get_file_tree(self, repo_id: str, path: str = "") -> List[FileNode]:
        repo_path = self.repo_base_path / repo_id / path
        if not repo_path.exists():
            return []

        nodes = []
        try:
            for item in sorted(repo_path.iterdir()):
                if item.name.startswith(".") and item.name != ".github":
                    continue

                node_type = FileNodeType.DIRECTORY if item.is_dir() else FileNodeType.FILE
                rel_path = str(item.relative_to(self.repo_base_path / repo_id))

                status_code, stdout, _ = self._run_git(repo_id, "status", "--porcelain", rel_path)
                git_status = stdout[:2].strip() if status_code == 0 and stdout else None

                node = FileNode(
                    path=rel_path,
                    name=item.name,
                    type=node_type,
                    size=item.stat().st_size if item.is_file() else 0,
                    children=None,
                    git_status=git_status,
                )

                if item.is_dir():
                    node.children = self.get_file_tree(repo_id, rel_path)

                nodes.append(node)
        except PermissionError:
            pass

        return nodes

    def get_file_content(self, repo_id: str, file_path: str, ref: str = None) -> str:
        if ref:
            code, stdout, stderr = self._run_git(repo_id, "show", f"{ref}:{file_path}")
            if code != 0:
                raise HTTPException(status_code=404, detail=f"File not found: {stderr}")
            return stdout
        else:
            full_path = self.repo_base_path / repo_id / file_path
            if not full_path.exists():
                raise HTTPException(status_code=404, detail="File not found")
            return full_path.read_text(encoding="utf-8", errors="replace")

    def write_file(self, repo_id: str, file_path: str, content: str) -> None:
        full_path = self.repo_base_path / repo_id / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content, encoding="utf-8")

    def get_branches(self, repo_id: str) -> List[Branch]:
        code, stdout, _ = self._run_git(
            repo_id,
            "branch",
            "-vv",
            "--format=%(refname:short)%09%(objectname:short)%09%(upstream:track)",
        )
        if code != 0:
            return []

        branches = []
        for line in stdout.strip().split("\n"):
            if "\t" not in line:
                continue
            parts = line.split("\t")
            name = parts[0].replace("* ", "").strip()
            sha = parts[1] if len(parts) > 1 else ""
            track = parts[2] if len(parts) > 2 else ""

            ahead = behind = 0
            if "ahead" in track:
                try:
                    ahead = int(track.split("ahead ")[1].split(",")[0].split("]")[0])
                except (IndexError, ValueError):
                    pass
            if "behind" in track:
                try:
                    behind = int(track.split("behind ")[1].split("]")[0])
                except (IndexError, ValueError):
                    pass

            branches.append(
                Branch(
                    name=name,
                    sha=sha,
                    is_default=name == "main" or name == "master",
                    ahead_count=ahead,
                    behind_count=behind,
                )
            )

        return branches

    def get_commits(self, repo_id: str, branch: str = "main", max_count: int = 50) -> List[Commit]:
        code, stdout, _ = self._run_git(
            repo_id,
            "log",
            branch,
            f"-{max_count}",
            "--format=%H%x00%an%x00%ae%x00%at%x00%cn%x00%ce%x00%ct%x00%P%x00%s",
        )
        if code != 0:
            return []

        commits = []
        for line in stdout.strip().split("\n"):
            parts = line.split("\x00")
            if len(parts) < 9:
                continue

            commits.append(
                Commit(
                    sha=parts[0],
                    author_name=parts[1],
                    author_email=parts[2],
                    authored_at=datetime.fromtimestamp(int(parts[3]), tz=timezone.utc),
                    committer_name=parts[4],
                    committer_email=parts[5],
                    committed_at=datetime.fromtimestamp(int(parts[6]), tz=timezone.utc),
                    parent_shas=parts[7].split(),
                    message=parts[8],
                )
            )

        return commits

    def create_branch(self, repo_id: str, name: str, base: str = "main") -> Branch:
        code, stdout, stderr = self._run_git(repo_id, "checkout", "-b", name, base)
        if code != 0:
            raise HTTPException(status_code=400, detail=f"Failed to create branch: {stderr}")
        return Branch(name=name, sha=stdout.strip(), is_default=False)

    def commit(self, repo_id: str, message: str, files: List[str] = None) -> Commit:
        if files:
            for f in files:
                self._run_git(repo_id, "add", f)
        else:
            self._run_git(repo_id, "add", "-A")

        code, stdout, stderr = self._run_git(repo_id, "commit", "-m", message)
        if code != 0:
            raise HTTPException(status_code=400, detail=f"Failed to commit: {stderr}")

        commits = self.get_commits(repo_id, max_count=1)
        return (
            commits[0]
            if commits
            else Commit(
                sha="",
                message=message,
                author_name="",
                author_email="",
                authored_at=datetime.now(timezone.utc),
                committer_name="",
                committer_email="",
                committed_at=datetime.now(timezone.utc),
                parent_shas=[],
            )
        )
