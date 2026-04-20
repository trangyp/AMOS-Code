#!/usr/bin/env python3
"""Migration script to move server files to AMOS-Consulting repository.

This script identifies all server/gateway files that should be moved
to the AMOS-Consulting repository for proper library/server separation.
"""

import shutil
from pathlib import Path

# Server files that should move to AMOS-Consulting
SERVER_FILES = [
    # Root-level server files
    "amos_fastapi_gateway.py",
    "amos_api_gateway.py",
    "amos_api_server.py",
    "amos_api_server_fixed.py",
    "amos_api_enhanced.py",
    "amos_api_hub.py",
    "amos_57_api_server.py",
    "amos_production_runtime.py",
    "amos_production_server.py",
    "amos_websocket_manager.py",
    "amos_execution_mcp_server.py",
    "amos_mcp_server.py",
    "amos_mcp_server_fastapi.py",
    "amos_grpc_server.py",
    "amos_gateway_cli.py",
    "amos_platform_gateway.py",
    "amos_unified_gateway.py",
    "equation_api_gateway.py",
    "axiom_one_api_server.py",
    "axiom_one_server.py",
    "mcp_server_bridge.py",
    "start_amos_servers.py",
    "websocket_server.py",
    # Backend directory
    "backend/",
]


def identify_server_files(repo_root: str = ".") -> list[Path]:
    """Identify all server-related files in the repository."""
    root = Path(repo_root)
    files_found = []

    for pattern in SERVER_FILES:
        path = root / pattern
        if path.exists():
            files_found.append(path)

    return files_found


def create_migration_plan(target_repo: str = "../AMOS-Consulting") -> dict:
    """Create a migration plan for server files."""
    files = identify_server_files()

    plan = {
        "source_repo": ".",
        "target_repo": target_repo,
        "files_to_migrate": [],
        "dependencies_to_add": [
            "fastapi>=0.104.0",
            "uvicorn[standard]>=0.24.0",
            "websockets>=12.0",
            "flask>=3.0.0",
            "flask-cors>=4.0.0",
        ],
        "post_migration_steps": [
            "Update imports in migrated files",
            "Add amos-brain as dependency in AMOS-Consulting",
            "Update pyproject.toml entry points",
            "Create docker-compose for server stack",
        ],
    }

    for file in files:
        plan["files_to_migrate"].append(
            {
                "source": str(file),
                "target": f"{target_repo}/{file.name if file.is_file() else file}",
                "type": "file" if file.is_file() else "directory",
            }
        )

    return plan


def print_migration_plan(plan: dict) -> None:
    """Print the migration plan."""
    print("=" * 60)
    print("AMOS SERVER MIGRATION PLAN")
    print("=" * 60)
    print(f"\nSource: {plan['source_repo']}")
    print(f"Target: {plan['target_repo']}")
    print(f"\nFiles to migrate ({len(plan['files_to_migrate'])}):")

    for item in plan["files_to_migrate"]:
        icon = "📄" if item["type"] == "file" else "📁"
        print(f"  {icon} {item['source']} -> {item['target']}")

    print("\nDependencies to add in target:")
    for dep in plan["dependencies_to_add"]:
        print(f"  📦 {dep}")

    print("\nPost-migration steps:")
    for step in plan["post_migration_steps"]:
        print(f"  ✓ {step}")

    print("\n" + "=" * 60)


def execute_migration(plan: dict, dry_run: bool = True) -> None:
    """Execute or simulate the migration."""
    if dry_run:
        print("\n🏃 DRY RUN - No files will be moved")
        print("Run with dry_run=False to execute actual migration\n")
        return

    target_path = Path(plan["target_repo"])
    if not target_path.exists():
        print(f"❌ Target repository not found: {target_path}")
        print("Please clone AMOS-Consulting repository first")
        return

    for item in plan["files_to_migrate"]:
        source = Path(item["source"])
        target = Path(item["target"])

        if not source.exists():
            print(f"⚠️  Source not found: {source}")
            continue

        # Create parent directories
        target.parent.mkdir(parents=True, exist_ok=True)

        if item["type"] == "file":
            shutil.move(str(source), str(target))
            print(f"✅ Moved: {source} -> {target}")
        else:
            shutil.move(str(source), str(target))
            print(f"✅ Moved directory: {source} -> {target}")

    print("\n✅ Migration complete!")
    print("Next steps:")
    print("  1. Update AMOS-Consulting pyproject.toml")
    print("  2. Update imports in migrated files")
    print("  3. Test server functionality")
    print("  4. Commit and push changes")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Migrate AMOS server files to AMOS-Consulting")
    parser.add_argument(
        "--execute", action="store_true", help="Execute actual migration (default: dry run)"
    )
    parser.add_argument(
        "--target", default="../AMOS-Consulting", help="Path to AMOS-Consulting repository"
    )

    args = parser.parse_args()

    plan = create_migration_plan(args.target)
    print_migration_plan(plan)
    execute_migration(plan, dry_run=not args.execute)
