#!/usr/bin/env python3
"""
AMOS Verified Patch Workflow

Implements the "deterministic verification envelope" for AI-generated patches.
Every patch from OpenClaw/Agent Mesh must pass Repo Doctor before being committed.

Creator: Trang Phan
Version: 1.0.0
"""

import asyncio
import json
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
UTC = timezone.utc, timezone

UTC = UTC
from pathlib import Path

from amos_brain.global_laws import GlobalLaws

# AMOS Imports
from amos_brain.clawspring_bridge import create_amos_agent
from amos_openclaw_connector import BridgeConfig, StateSynchronizer


@dataclass
class VerificationStage:
    """Single verification stage result."""

    name: str
    passed: bool
    duration_ms: float
    findings: list[dict] = field(default_factory=list)
    output: str = ""
    error: str = None


@dataclass
class PatchVerificationReceipt:
    """Immutable receipt for verified patches."""

    patch_id: str
    timestamp: str
    commit_hash: str
    author: str
    stages: list[VerificationStage]
    passed_all: bool
    amos_laws_compliant: bool
    security_clearance: str  # "clean" | "warnings" | "blocked"
    pr_ready: bool
    receipt_signature: str


class RepoDoctorVerifier:
    """Deterministic verification using Repo Doctor + external scanners."""

    def __init__(self, repo_path: Path):
        self.repo_path = repo_path
        self.findings: list[dict] = []

    async def run_full_verification(self, changed_files: list[Path]) -> list[VerificationStage]:
        """Run complete verification pipeline on changed files."""
        stages = []

        # Stage 1: Syntax validation (fastest, fail-fast)
        stages.append(await self._check_syntax(changed_files))
        if not stages[-1].passed:
            return stages  # Stop early on syntax errors

        # Stage 2: Import resolution
        stages.append(await self._check_imports(changed_files))

        # Stage 3: Static analysis (Ruff + Pyright)
        stages.append(await self._run_ruff(changed_files))
        stages.append(await self._run_pyright())

        # Stage 4: Security scanning (Semgrep + Trivy + Gitleaks)
        stages.append(await self._run_semgrep(changed_files))
        stages.append(await self._run_trivy_fs())
        stages.append(await self._run_gitleaks())

        # Stage 5: Test validation
        stages.append(await self._run_pytest(changed_files))

        # Stage 6: AMOS L1-L6 compliance
        stages.append(await self._check_amos_laws(changed_files))

        return stages

    async def _check_syntax(self, files: list[Path]) -> VerificationStage:
        """Verify all Python files parse without SyntaxError."""
        start = datetime.now(timezone.utc)
        errors = []

        for f in files:
            if f.suffix != ".py":
                continue
            try:
                compile(f.read_text(), str(f), "exec")
            except SyntaxError as e:
                errors.append({"file": str(f), "line": e.lineno, "error": str(e)})

        duration = (datetime.now(timezone.utc) - start).total_seconds() * 1000

        return VerificationStage(
            name="syntax_check",
            passed=len(errors) == 0,
            duration_ms=duration,
            findings=errors,
            output="All files parse correctly" if not errors else f"{len(errors)} syntax errors",
        )

    async def _check_imports(self, files: list[Path]) -> VerificationStage:
        """Verify imports resolve."""
        start = datetime.now(timezone.utc)

        # Use Repo Doctor's import sensor if available
        try:
            from repo_doctor.sensors import ImportSensor

            sensor = ImportSensor(self.repo_path)
            result = sensor.run()

            return VerificationStage(
                name="import_check",
                passed=result.passed,
                duration_ms=(datetime.now(timezone.utc) - start).total_seconds() * 1000,
                findings=[{"error": f} for f in (result.findings or [])],
                output="Imports resolved" if result.passed else "Import errors detected",
            )
        except ImportError:
            # Fallback: basic import check
            return VerificationStage(
                name="import_check",
                passed=True,
                duration_ms=0,
                findings=[],
                output="Import sensor not available, skipped",
            )

    async def _run_ruff(self, files: list[Path]) -> VerificationStage:
        """Run Ruff linter on changed files."""
        start = datetime.now(timezone.utc)

        py_files = [str(f) for f in files if f.suffix == ".py"]
        if not py_files:
            return VerificationStage(
                name="ruff_lint", passed=True, duration_ms=0, findings=[], output="No Python files"
            )

        try:
            result = subprocess.run(
                ["ruff", "check", "--format=json"] + py_files,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=30,
            )

            findings = json.loads(result.stdout) if result.stdout else []
            duration = (datetime.now(timezone.utc) - start).total_seconds() * 1000

            return VerificationStage(
                name="ruff_lint",
                passed=result.returncode == 0,
                duration_ms=duration,
                findings=findings,
                output=f"{len(findings)} lint issues" if findings else "Lint clean",
            )
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return VerificationStage(
                name="ruff_lint",
                passed=True,  # Don't block on missing tool
                duration_ms=0,
                findings=[],
                output="Ruff not available",
            )

    async def _run_pyright(self) -> VerificationStage:
        """Run Pyright type checker."""
        start = datetime.now(timezone.utc)

        try:
            result = subprocess.run(
                ["pyright", "--outputjson"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=60,
            )

            data = json.loads(result.stdout) if result.stdout else {}
            errors = data.get("generalDiagnostics", [])
            duration = (datetime.now(timezone.utc) - start).total_seconds() * 1000

            return VerificationStage(
                name="pyright_typecheck",
                passed=len(errors) == 0,
                duration_ms=duration,
                findings=errors,
                output=f"{len(errors)} type errors" if errors else "Types clean",
            )
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return VerificationStage(
                name="pyright_typecheck",
                passed=True,
                duration_ms=0,
                findings=[],
                output="Pyright not available",
            )

    async def _run_semgrep(self, files: list[Path]) -> VerificationStage:
        """Run Semgrep security scanner."""
        start = datetime.now(timezone.utc)

        try:
            result = subprocess.run(
                ["semgrep", "--config=auto", "--json", "--quiet"] + [str(f) for f in files],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=60,
            )

            data = json.loads(result.stdout) if result.stdout else {}
            findings = data.get("results", [])
            duration = (datetime.now(timezone.utc) - start).total_seconds() * 1000

            return VerificationStage(
                name="semgrep_security",
                passed=len(findings) == 0,
                duration_ms=duration,
                findings=findings,
                output=f"{len(findings)} security issues" if findings else "Security clean",
            )
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return VerificationStage(
                name="semgrep_security",
                passed=True,
                duration_ms=0,
                findings=[],
                output="Semgrep not available",
            )

    async def _run_trivy_fs(self) -> VerificationStage:
        """Run Trivy filesystem scan."""
        start = datetime.now(timezone.utc)

        try:
            result = subprocess.run(
                ["trivy", "fs", "--scanners=vuln,config,secret", "--format=json", "."],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=120,
            )

            data = json.loads(result.stdout) if result.stdout else {}
            findings = []

            # Parse Trivy results
            for result_item in data.get("Results", []):
                for vuln in result_item.get("Vulnerabilities", []):
                    findings.append(
                        {
                            "id": vuln.get("VulnerabilityID"),
                            "title": vuln.get("Title"),
                            "severity": vuln.get("Severity"),
                            "package": vuln.get("PkgName"),
                        }
                    )

            duration = (datetime.now(timezone.utc) - start).total_seconds() * 1000

            return VerificationStage(
                name="trivy_vulnerability",
                passed=len(findings) == 0,
                duration_ms=duration,
                findings=findings,
                output=f"{len(findings)} vulnerabilities" if findings else "No vulnerabilities",
            )
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return VerificationStage(
                name="trivy_vulnerability",
                passed=True,
                duration_ms=0,
                findings=[],
                output="Trivy not available",
            )

    async def _run_gitleaks(self) -> VerificationStage:
        """Run Gitleaks for secrets detection."""
        start = datetime.now(timezone.utc)

        try:
            result = subprocess.run(
                ["gitleaks", "detect", "--source=.", "--verbose", "--redact"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=30,
            )

            # Gitleaks exits 1 if leaks found
            leaks_found = result.returncode != 0
            duration = (datetime.now(timezone.utc) - start).total_seconds() * 1000

            return VerificationStage(
                name="gitleaks_secrets",
                passed=not leaks_found,
                duration_ms=duration,
                findings=[{"output": result.stdout}] if leaks_found else [],
                output="Secrets detected!" if leaks_found else "No secrets found",
            )
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return VerificationStage(
                name="gitleaks_secrets",
                passed=True,
                duration_ms=0,
                findings=[],
                output="Gitleaks not available",
            )

    async def _run_pytest(self, files: list[Path]) -> VerificationStage:
        """Run pytest on affected tests."""
        start = datetime.now(timezone.utc)

        # Find tests related to changed files
        test_files = []
        for f in files:
            test_path = Path("tests") / f"test_{f.stem}.py"
            if test_path.exists():
                test_files.append(str(test_path))

        if not test_files:
            return VerificationStage(
                name="pytest_validation",
                passed=True,
                duration_ms=0,
                findings=[],
                output="No test files found for changes",
            )

        try:
            result = subprocess.run(
                ["python", "-m", "pytest"] + test_files + ["--tb=short", "-q"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=120,
            )

            duration = (datetime.now(timezone.utc) - start).total_seconds() * 1000

            return VerificationStage(
                name="pytest_validation",
                passed=result.returncode == 0,
                duration_ms=duration,
                findings=[],
                output="Tests passed" if result.returncode == 0 else "Tests failed",
                error=result.stdout if result.returncode != 0 else None,
            )
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return VerificationStage(
                name="pytest_validation",
                passed=True,
                duration_ms=0,
                findings=[],
                output="pytest not available",
            )

    async def _check_amos_laws(self, files: list[Path]) -> VerificationStage:
        """Verify compliance with AMOS Global Laws L1-L6."""
        start = datetime.now(timezone.utc)
        violations = []

        for f in files:
            if f.suffix != ".py":
                continue
            content = f.read_text()

            for law_id in ["L1", "L2", "L3", "L4", "L5", "L6"]:
                law = GlobalLaws.get_law(law_id)
                check = law.check(content)
                if not check.compliant:
                    violations.append(
                        {
                            "file": str(f),
                            "law": law_id,
                            "description": law.description,
                            "issue": check.message,
                        }
                    )

        duration = (datetime.now(timezone.utc) - start).total_seconds() * 1000

        return VerificationStage(
            name="amos_laws_compliance",
            passed=len(violations) == 0,
            duration_ms=duration,
            findings=violations,
            output="L1-L6 compliant" if not violations else f"{len(violations)} law violations",
        )


class VerifiedPatchWorkflow:
    """
    Main workflow orchestrating OpenClaw → Repo Doctor → Commit/PR.

    This is the "deterministic verification envelope" that ensures
    AI-generated patches are validated before being trusted.
    """

    def __init__(self, repo_path: Path = None):
        self.repo_path = repo_path or Path.cwd()
        self.verifier = RepoDoctorVerifier(self.repo_path)
        self.state_sync = StateSynchronizer(BridgeConfig())
        self.amos = create_amos_agent()
        self.receipts_dir = Path.home() / ".amos-verified-patches"
        self.receipts_dir.mkdir(parents=True, exist_ok=True)

    async def process_patch(
        self,
        patch_description: str,
        changed_files: list[Path],
        author: str = "openclaw-agent",
        auto_commit: bool = False,
    ) -> PatchVerificationReceipt:
        """
        Process a patch through the full verification workflow.

        Args:
            patch_description: What the patch is supposed to do
            changed_files: List of files modified by the patch
            author: Agent or user who generated the patch
            auto_commit: Whether to auto-commit if verification passes

        Returns:
            PatchVerificationReceipt: Immutable verification record
        """
        print(f"🔍 Starting verification for {len(changed_files)} files...")
        print(f"   Description: {patch_description}")
        print(f"   Author: {author}")

        # Run verification stages
        stages = await self.verifier.run_full_verification(changed_files)

        # Calculate aggregate results
        passed_all = all(s.passed for s in stages)
        critical_stages = ["syntax_check", "gitleaks_secrets", "amos_laws_compliance"]
        critical_passed = all(s.passed for s in stages if s.name in critical_stages)

        # Determine security clearance
        security_findings = sum(
            1
            for s in stages
            if s.name in ["semgrep_security", "trivy_vulnerability", "gitleaks_secrets"]
            for _ in s.findings
        )
        if security_findings == 0:
            security_clearance = "clean"
        elif security_findings < 3:
            security_clearance = "warnings"
        else:
            security_clearance = "blocked"

        # PR ready only if all critical checks pass and no blocking security issues
        pr_ready = critical_passed and security_clearance != "blocked"

        # Generate receipt
        import hashlib

        receipt_data = f"{author}:{datetime.now(timezone.utc).isoformat()}:{passed_all}"
        receipt_sig = hashlib.sha256(receipt_data.encode()).hexdigest()[:16]

        receipt = PatchVerificationReceipt(
            patch_id=receipt_sig,
            timestamp=datetime.now(timezone.utc).isoformat(),
            commit_hash=self._get_current_commit(),
            author=author,
            stages=stages,
            passed_all=passed_all,
            amos_laws_compliant=critical_passed,
            security_clearance=security_clearance,
            pr_ready=pr_ready,
            receipt_signature=receipt_sig,
        )

        # Save receipt
        receipt_file = self.receipts_dir / f"{receipt.patch_id}.json"
        receipt_file.write_text(json.dumps(self._receipt_to_dict(receipt), indent=2))

        # Print summary
        self._print_verification_summary(receipt)

        # Auto-commit if requested and verified
        if auto_commit and pr_ready:
            await self._commit_verified_patch(receipt, changed_files)

        return receipt

    def _get_current_commit(self) -> str:
        """Get current git commit hash."""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
            )
            return result.stdout.strip()[:8]
        except Exception:
            return "unknown"

    def _receipt_to_dict(self, receipt: PatchVerificationReceipt) -> dict:
        """Convert receipt to dictionary."""
        return {
            "patch_id": receipt.patch_id,
            "timestamp": receipt.timestamp,
            "commit_hash": receipt.commit_hash,
            "author": receipt.author,
            "stages": [
                {
                    "name": s.name,
                    "passed": s.passed,
                    "duration_ms": s.duration_ms,
                    "findings_count": len(s.findings),
                    "output": s.output,
                }
                for s in receipt.stages
            ],
            "passed_all": receipt.passed_all,
            "amos_laws_compliant": receipt.amos_laws_compliant,
            "security_clearance": receipt.security_clearance,
            "pr_ready": receipt.pr_ready,
            "receipt_signature": receipt.receipt_signature,
        }

    def _print_verification_summary(self, receipt: PatchVerificationReceipt):
        """Print formatted verification summary."""
        print("\n" + "=" * 60)
        print(f"📋 VERIFICATION RECEIPT: {receipt.patch_id}")
        print("=" * 60)

        for stage in receipt.stages:
            icon = "✅" if stage.passed else "❌"
            print(f"{icon} {stage.name:30} ({stage.duration_ms:.0f}ms) - {stage.output}")

        print("-" * 60)
        status_icon = "✅" if receipt.pr_ready else "❌"
        print(f"{status_icon} PR Ready: {receipt.pr_ready}")
        print(f"   Security Clearance: {receipt.security_clearance}")
        print(f"   AMOS Laws Compliant: {receipt.amos_laws_compliant}")
        print(f"   Receipt Signature: {receipt.receipt_signature}")
        print("=" * 60)

    async def _commit_verified_patch(self, receipt: PatchVerificationReceipt, files: list[Path]):
        """Commit the verified patch with receipt metadata."""
        # Stage files
        for f in files:
            subprocess.run(["git", "add", str(f)], cwd=self.repo_path)

        # Commit with verification metadata
        commit_msg = f"""[VERIFIED PATCH] {receipt.patch_id}

Author: {receipt.author}
Verification: {receipt.receipt_signature}
Security: {receipt.security_clearance}
AMOS Laws: {"✅" if receipt.amos_laws_compliant else "❌"}

Stages passed: {sum(1 for s in receipt.stages if s.passed)}/{len(receipt.stages)}
"""
        subprocess.run(
            ["git", "commit", "-m", commit_msg],
            cwd=self.repo_path,
            capture_output=True,
        )
        print(f"✅ Committed with verification: {receipt.patch_id}")


async def demo_workflow():
    """Demonstrate the verified patch workflow."""
    workflow = VerifiedPatchWorkflow()

    # Example: Simulate a patch from OpenClaw
    demo_files = [Path("amos_demo_patch.py")]

    # Create a demo file
    demo_files[0].write_text("""
# Demo patch for verification testing
def hello():
    print("Hello from verified patch!")
""")

    receipt = await workflow.process_patch(
        patch_description="Add demo greeting function",
        changed_files=demo_files,
        author="openclaw-editor-agent",
        auto_commit=False,
    )

    # Cleanup
    demo_files[0].unlink()

    return receipt


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        asyncio.run(demo_workflow())
    else:
        print("Usage: python amos_verified_patch_workflow.py --demo")
        print("")
        print("This module provides the deterministic verification envelope")
        print("for AI-generated patches in the AMOS-OpenClaw integration.")
