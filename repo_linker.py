#!/usr/bin/env python3

from typing import Any

"""AMOS Repo Linker - Link all GitHub repos into one monorepo.

Usage:
    python repo_linker.py --username YOUR_GITHUB_USERNAME --method subtree
    python repo_linker.py --username YOUR_GITHUB_USERNAME --method submodules
    python repo_linker.py --token $GITHUB_TOKEN --method subtree
"""

import argparse
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path


def get_github_repos(username: str, token: str | None = None) -> list[dict[str, Any]]:
    """Fetch all repos for a GitHub user."""
    url = f"https://api.github.com/users/{username}/repos?per_page=100"
    headers = {"Accept": "application/vnd.github.v3+json"}

    if token:
        headers["Authorization"] = f"token {token}"

    req = urllib.request.Request(url, headers=headers)

    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        print(f"Error fetching repos: {e!s}")
        if e.code == 401:
            print("Invalid or missing GitHub token")
        elif e.code == 404:
            print(f"User '{username}' not found")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


def run_cmd(cmd: List[str], cwd: Path | None = None) -> Tuple[int, str, str]:
    """Run shell command and return (exit_code, stdout, stderr)."""
    try:
        result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=False)
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return 1, "", str(e)


def create_monorepo_subtree(repos: list[dict[str, Any]], output_dir: Path) -> None:
    """Create monorepo using git subtree."""
    print(f"\n🚀 Creating monorepo with {len(repos)} repos using git subtree...")

    # Initialize repo
    run_cmd(["git", "init"], cwd=output_dir)
    run_cmd(["git", "checkout", "-b", "main"], cwd=output_dir)

    # Create README
    readme = output_dir / "README.md"
    readme.write_text(f"""# AMOS Unified Monorepo

This monorepo contains {len(repos)} linked repositories.

## Structure
""")

    run_cmd(["git", "add", "."], cwd=output_dir)
    run_cmd(["git", "commit", "-m", "Initial commit"], cwd=output_dir)

    # Add each repo as subtree
    for i, repo in enumerate(repos, 1):
        name = repo["name"]
        clone_url = repo["clone_url"]
        default_branch = repo.get("default_branch", "main")

        print(f"\n[{i}/{len(repos)}] Adding {name}...")

        # Add remote
        run_cmd(["git", "remote", "add", name, clone_url], cwd=output_dir)

        # Fetch
        ret, _, err = run_cmd(["git", "fetch", name], cwd=output_dir)
        if ret != 0:
            print(f"  ⚠ Failed to fetch {name}: {err}")
            continue

        # Add as subtree
        prefix = f"packages/{name}"
        ret, out, err = run_cmd(
            ["git", "subtree", "add", "--prefix", prefix, name, default_branch], cwd=output_dir
        )

        if ret == 0:
            print(f"  ✓ Added to {prefix}")
            # Append to README
            with open(readme, "a") as f:
                f.write(f"\n- `{prefix}/` - [{name}]({repo['html_url']})\n")
        else:
            print(f"  ❌ Failed: {err}")

    # Commit README update
    run_cmd(["git", "add", "README.md"], cwd=output_dir)
    run_cmd(["git", "commit", "-m", "Add repo index"], cwd=output_dir)

    print("\n✓ Monorepo created at: " + str(output_dir))
    print(f"   Total repos linked: {len(repos)}")


def create_monorepo_submodules(repos: list[dict[str, Any]], output_dir: Path) -> None:
    """Create monorepo using git submodules."""
    print(f"\n🚀 Creating monorepo with {len(repos)} repos using git submodules...")

    # Initialize repo
    run_cmd(["git", "init"], cwd=output_dir)
    run_cmd(["git", "checkout", "-b", "main"], cwd=output_dir)

    # Create README
    readme = output_dir / "README.md"
    readme_content = f"""# AMOS Unified Monorepo (Submodules)

This monorepo links {len(repos)} repositories as submodules.

## Clone with all submodules
```bash
git clone --recursive <this-repo-url>
```

## Update all submodules
```bash
git submodule update --init --recursive
```

## Structure
"""

    # Add each repo as submodule
    for i, repo in enumerate(repos, 1):
        name = repo["name"]
        clone_url = repo["clone_url"]

        print(f"\n[{i}/{len(repos)}] Adding {name}...")

        path = f"packages/{name}"
        ret, _, err = run_cmd(["git", "submodule", "add", clone_url, path], cwd=output_dir)

        if ret == 0:
            print(f"  ✓ Added as submodule: {path}")
            readme_content += f"\n- `{path}/` - [{name}]({repo['html_url']})\n"
        else:
            print(f"  ❌ Failed: {err}")

    # Write README
    readme.write_text(readme_content)

    # Commit
    run_cmd(["git", "add", "."], cwd=output_dir)
    run_cmd(["git", "commit", "-m", f"Add {len(repos)} submodules"], cwd=output_dir)

    print("\n✓ Monorepo with submodules created at: " + str(output_dir))
    print("   To clone with all submodules:")
    print("   git clone --recursive <repo-url>")


def main() -> int:
    parser = argparse.ArgumentParser(description="Link all GitHub repos into a monorepo")
    parser.add_argument(
        "--username", "-u", help="GitHub username", default=os.getenv("GITHUB_USERNAME")
    )
    parser.add_argument(
        "--token", "-t", help="GitHub personal access token", default=os.getenv("GITHUB_TOKEN")
    )
    parser.add_argument(
        "--method",
        "-m",
        choices=["subtree", "submodules"],
        default="subtree",
        help="Linking method (default: subtree)",
    )
    parser.add_argument("--output", "-o", help="Output directory", default="amos-monorepo")

    args = parser.parse_args()

    if not args.username:
        print("Error: GitHub username required (--username or GITHUB_USERNAME env)")
        return 1

    print(f"🔍 Fetching repos for: {args.username}")
    repos = get_github_repos(args.username, args.token)

    if not repos:
        print("No repositories found.")
        return 0

    print(f"Found {len(repos)} repositories")

    # Create output directory
    output_dir = Path(args.output).resolve()
    if output_dir.exists():
        print(f"Error: Directory {output_dir} already exists")
        return 1

    output_dir.mkdir(parents=True)

    # Create monorepo based on method
    if args.method == "subtree":
        create_monorepo_subtree(repos, output_dir)
    else:
        create_monorepo_submodules(repos, output_dir)

    print("\n📁 Monorepo location: " + str(output_dir))
    print("\nNext steps:")
    print(f"  cd {output_dir}")
    print("  git remote add origin https://github.com/YOURNAME/amos-monorepo.git")
    print("  git push -u origin main")

    return 0


if __name__ == "__main__":
    sys.exit(main())
