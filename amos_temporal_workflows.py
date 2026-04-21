"""AMOS Temporal Workflows - Durable execution for cross-repo operations."""

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from temporalio import activity, workflow
from temporalio.common import RetryPolicy

# ============================================================
# WORKFLOW INPUT/OUTPUT DEFINITIONS
# ============================================================


@dataclass
class RepoScanInput:
    """Input for repository scanning workflow."""

    repo_name: str
    repo_url: str
    scan_depth: str = "full"  # quick, standard, full
    branch: str = "main"
    commit_sha: Optional[str] = None


@dataclass
class RepoScanOutput:
    """Output from repository scanning workflow."""

    repo_name: str
    scan_id: str
    status: str  # success, partial, failed
    issues_found: int
    files_scanned: int
    issues: list[dict[str, Any]]
    timestamp: str
    duration_seconds: float


@dataclass
class MultiRepoFixInput:
    """Input for multi-repository fix workflow."""

    repos: list[RepoScanInput]
    fix_strategy: str = "auto"  # auto, conservative, aggressive
    dry_run: bool = True
    approval_required: bool = True


@dataclass
class MultiRepoFixOutput:
    """Output from multi-repository fix workflow."""

    workflow_id: str
    status: str
    results: list[dict[str, Any]]
    repos_fixed: int
    repos_failed: int
    repos_pending_approval: int
    timestamp: str


@dataclass
class CrossRepoReleaseInput:
    """Input for cross-repository release workflow."""

    version: str
    repos: list[str]  # List of repo names to release
    release_notes: str
    skip_tests: bool = False
    require_approval: bool = True


@dataclass
class CrossRepoReleaseOutput:
    """Output from cross-repository release workflow."""

    release_id: str
    version: str
    status: str
    repo_results: dict[str, Any]
    packages_published: list[str]
    timestamp: str


@dataclass
class KnowledgeSyncInput:
    """Input for knowledge synchronization workflow."""

    source_repo: str
    target_repos: list[str]
    knowledge_types: list[str]  # schemas, equations, invariants
    force_update: bool = False


@dataclass
class KnowledgeSyncOutput:
    """Output from knowledge synchronization workflow."""

    sync_id: str
    items_synced: int
    repos_updated: int
    conflicts: list[dict[str, Any]]
    timestamp: str


# ============================================================
# ACTIVITIES
# ============================================================


@activity.defn
async def scan_repository(input: RepoScanInput) -> RepoScanOutput:
    """Activity: Scan a single repository for issues."""
    import time

    start_time = time.time()

    # Simulate repo scanning (replace with actual implementation)
    activity.heartbeat(f"Scanning {input.repo_name}...")

    # In real implementation:
    # - Clone/pull repo
    # - Run static analysis
    # - Check for deprecations
    # - Detect architectural drift

    issues = [
        {"type": "deprecation", "file": "example.py", "line": 10},
        {"type": "architectural", "file": "service.py", "line": 25},
    ]

    return RepoScanOutput(
        repo_name=input.repo_name,
        scan_id=f"scan-{input.repo_name}-{datetime.now(timezone.utc).isoformat()}",
        status="success",
        issues_found=len(issues),
        files_scanned=150,
        issues=issues,
        timestamp=datetime.now(timezone.utc).isoformat(),
        duration_seconds=time.time() - start_time,
    )


@activity.defn
async def apply_fixes(repo_name: str, issues: list[dict], dry_run: bool) -> dict[str, Any]:
    """Activity: Apply fixes to a repository."""
    activity.heartbeat(f"Applying fixes to {repo_name}...")

    # In real implementation:
    # - Checkout repo
    # - Apply automated fixes
    # - Run tests
    # - Create PR if tests pass

    if dry_run:
        return {"status": "dry_run", "fixes_applied": 0, "fixes_would_apply": len(issues)}

    return {
        "status": "success",
        "fixes_applied": len(issues),
        "pr_url": f"https://github.com/trangyp/{repo_name}/pull/123",
        "commit_sha": "abc123",
    }


@activity.defn
async def wait_for_approval(workflow_id: str, repo_name: str) -> bool:
    """Activity: Wait for human approval (external signal)."""
    # This activity should be designed to complete via external signal
    # Temporal will handle the waiting state
    activity.heartbeat(f"Waiting for approval on {repo_name}...")

    # Return False by default - workflow will be signaled externally
    return False


@activity.defn
async def run_tests(repo_name: str, branch: str) -> dict[str, Any]:
    """Activity: Run tests on a repository."""
    activity.heartbeat(f"Running tests on {repo_name}...")

    # In real implementation:
    # - Checkout repo
    # - Install dependencies
    # - Run test suite
    # - Report results

    return {
        "repo": repo_name,
        "branch": branch,
        "tests_passed": 45,
        "tests_failed": 0,
        "coverage": 85.5,
        "status": "passed",
    }


@activity.defn
async def build_package(repo_name: str, version: str) -> dict[str, Any]:
    """Activity: Build package for a repository."""
    activity.heartbeat(f"Building {repo_name} v{version}...")

    return {
        "repo": repo_name,
        "version": version,
        "package_url": f"https://pypi.org/project/{repo_name}/{version}/",
        "status": "built",
    }


@activity.defn
async def publish_package(repo_name: str, version: str) -> dict[str, Any]:
    """Activity: Publish package to registry."""
    activity.heartbeat(f"Publishing {repo_name} v{version}...")

    return {"repo": repo_name, "version": version, "registry": "pypi", "status": "published"}


@activity.defn
async def sync_knowledge_to_repo(
    source_repo: str, target_repo: str, knowledge_types: list[str]
) -> dict[str, Any]:
    """Activity: Sync knowledge from source to target repo."""
    activity.heartbeat(f"Syncing knowledge from {source_repo} to {target_repo}...")

    # In real implementation:
    # - Pull latest from source
    # - Identify changed knowledge
    # - Push to target repo
    # - Create PR if needed

    return {
        "source": source_repo,
        "target": target_repo,
        "types_synced": knowledge_types,
        "items_synced": 15,
        "conflicts": 0,
    }


@activity.defn
async def notify_stakeholders(message: str, channels: list[str] = None) -> dict[str, Any]:
    """Activity: Send notifications to stakeholders."""
    channels = channels or ["slack", "email"]

    # In real implementation:
    # - Send Slack message
    # - Send email
    # - Update dashboard

    return {"message_sent": message, "channels": channels, "status": "sent"}


# ============================================================
# WORKFLOWS
# ============================================================


@workflow.defn
class RepoScanWorkflow:
    """Workflow: Scan a single repository."""

    @workflow.run
    async def run(self, input: RepoScanInput) -> RepoScanOutput:
        return await workflow.execute_activity(
            scan_repository,
            input,
            start_to_close_timeout=timedelta(minutes=10),
            retry_policy=RetryPolicy(
                initial_interval=timedelta(seconds=5),
                maximum_interval=timedelta(minutes=1),
                maximum_attempts=3,
            ),
        )


@workflow.defn
class MultiRepoScanWorkflow:
    """Workflow: Scan multiple repositories in parallel."""

    @workflow.run
    async def run(self, repos: list[RepoScanInput]) -> list[RepoScanOutput]:
        # Execute scans in parallel
        tasks = [
            workflow.execute_child_workflow(
                RepoScanWorkflow.run,
                repo_input,
                id=f"scan-{repo_input.repo_name}-{workflow.now().timestamp()}",
            )
            for repo_input in repos
        ]

        results = await workflow.gather(*tasks)
        return list(results)


@workflow.defn
class MultiRepoFixWorkflow:
    """Workflow: Fix issues across multiple repositories with approval gates."""

    @workflow.run
    async def run(self, input: MultiRepoFixInput) -> MultiRepoFixOutput:
        workflow_id = workflow.info().workflow_id

        # Phase 1: Scan all repos
        scan_results = await workflow.execute_child_workflow(
            MultiRepoScanWorkflow.run, input.repos, id=f"{workflow_id}-scan"
        )

        # Phase 2: Apply fixes (with approval if required)
        fix_results = []
        repos_pending_approval = 0
        repos_failed = 0

        for scan_result in scan_results:
            if scan_result.issues_found == 0:
                fix_results.append(
                    {"repo": scan_result.repo_name, "status": "no_issues", "action": "skipped"}
                )
                continue

            if input.approval_required:
                # Wait for human approval signal
                approval = await workflow.execute_activity(
                    wait_for_approval,
                    (workflow_id, scan_result.repo_name),
                    start_to_close_timeout=timedelta(hours=24),
                )

                if not approval:
                    repos_pending_approval += 1
                    fix_results.append(
                        {
                            "repo": scan_result.repo_name,
                            "status": "pending_approval",
                            "issues_found": scan_result.issues_found,
                        }
                    )
                    continue

            # Apply fixes
            fix_result = await workflow.execute_activity(
                apply_fixes,
                (scan_result.repo_name, scan_result.issues, input.dry_run),
                start_to_close_timeout=timedelta(minutes=30),
            )

            if fix_result.get("status") == "failed":
                repos_failed += 1

            fix_results.append(
                {"repo": scan_result.repo_name, "scan": scan_result, "fix": fix_result}
            )

        # Notify completion
        await workflow.execute_activity(
            notify_stakeholders,
            (f"Fix workflow completed: {len(fix_results)} repos processed",),
            start_to_close_timeout=timedelta(minutes=1),
        )

        return MultiRepoFixOutput(
            workflow_id=workflow_id,
            status="completed",
            results=fix_results,
            repos_fixed=len(
                [r for r in fix_results if r.get("fix", {}).get("status") == "success"]
            ),
            repos_failed=repos_failed,
            repos_pending_approval=repos_pending_approval,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )


@workflow.defn
class CrossRepoReleaseWorkflow:
    """Workflow: Coordinate release across multiple repositories."""

    @workflow.run
    async def run(self, input: CrossRepoReleaseInput) -> CrossRepoReleaseOutput:
        workflow_id = workflow.info().workflow_id
        release_id = f"release-{input.version}-{workflow.now().timestamp()}"

        repo_results = {}
        packages_published = []

        for repo_name in input.repos:
            # Step 1: Run tests
            if not input.skip_tests:
                test_result = await workflow.execute_activity(
                    run_tests, (repo_name, "main"), start_to_close_timeout=timedelta(minutes=20)
                )

                if test_result.get("status") != "passed":
                    repo_results[repo_name] = {"status": "failed", "phase": "tests"}
                    continue

            # Step 2: Build package
            build_result = await workflow.execute_activity(
                build_package,
                (repo_name, input.version),
                start_to_close_timeout=timedelta(minutes=15),
            )

            if build_result.get("status") != "built":
                repo_results[repo_name] = {"status": "failed", "phase": "build"}
                continue

            # Step 3: Wait for approval (if required)
            if input.require_approval:
                approved = await workflow.execute_activity(
                    wait_for_approval,
                    (workflow_id, repo_name),
                    start_to_close_timeout=timedelta(hours=48),
                )

                if not approved:
                    repo_results[repo_name] = {"status": "pending_approval", "phase": "publish"}
                    continue

            # Step 4: Publish
            publish_result = await workflow.execute_activity(
                publish_package,
                (repo_name, input.version),
                start_to_close_timeout=timedelta(minutes=10),
            )

            if publish_result.get("status") == "published":
                packages_published.append(f"{repo_name}@{input.version}")
                repo_results[repo_name] = {"status": "published", "version": input.version}
            else:
                repo_results[repo_name] = {"status": "failed", "phase": "publish"}

        # Notify stakeholders
        await workflow.execute_activity(
            notify_stakeholders,
            (
                f"Release {input.version} completed: {len(packages_published)} packages published",
                ["slack", "email"],
            ),
            start_to_close_timeout=timedelta(minutes=1),
        )

        return CrossRepoReleaseOutput(
            release_id=release_id,
            version=input.version,
            status="completed",
            repo_results=repo_results,
            packages_published=packages_published,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )


@workflow.defn
class KnowledgeSyncWorkflow:
    """Workflow: Synchronize knowledge across repositories."""

    @workflow.run
    async def run(self, input: KnowledgeSyncInput) -> KnowledgeSyncOutput:
        workflow_id = workflow.info().workflow_id
        sync_id = f"sync-{workflow.now().timestamp()}"

        # Sync to all target repos in parallel
        sync_tasks = [
            workflow.execute_activity(
                sync_knowledge_to_repo,
                (input.source_repo, target_repo, input.knowledge_types),
                start_to_close_timeout=timedelta(minutes=15),
            )
            for target_repo in input.target_repos
        ]

        sync_results = await workflow.gather(*sync_tasks)

        # Calculate totals
        total_synced = sum(r.get("items_synced", 0) for r in sync_results)
        total_conflicts = sum(r.get("conflicts", 0) for r in sync_results)

        # Build conflicts list
        conflicts = [
            {"repo": r.get("target"), "conflicts": r.get("conflicts")}
            for r in sync_results
            if r.get("conflicts", 0) > 0
        ]

        return KnowledgeSyncOutput(
            sync_id=sync_id,
            items_synced=total_synced,
            repos_updated=len(input.target_repos),
            conflicts=conflicts,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )


# ============================================================
# WORKFLOW REGISTRATION HELPERS
# ============================================================

WORKFLOWS = [
    RepoScanWorkflow,
    MultiRepoScanWorkflow,
    MultiRepoFixWorkflow,
    CrossRepoReleaseWorkflow,
    KnowledgeSyncWorkflow,
]

ACTIVITIES = [
    scan_repository,
    apply_fixes,
    wait_for_approval,
    run_tests,
    build_package,
    publish_package,
    sync_knowledge_to_repo,
    notify_stakeholders,
]


def register_workflows(worker):
    """Register all workflows and activities with a Temporal worker."""
    for wf in WORKFLOWS:
        worker.register_workflow_implementation_type(wf)

    for act in ACTIVITIES:
        worker.register_activity_implementation(act)
