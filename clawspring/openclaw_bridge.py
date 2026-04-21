"""OpenClaw Bridge - First-Class Integration Module

Connects ClawSpring (OpenClaw agent runtime) with:
1. Model Fabric (Ollama-native provider for tool calling)
2. Repo Doctor Security Scanner (deterministic verification)
3. AMOS Kernel Runtime (lawful agent execution)

Design Principle:
    OpenClaw uses native Ollama API (not /v1 OpenAI-compatible) for reliable tool calling.

Architecture:
    ┌─────────────┐     ┌──────────────┐     ┌─────────────────┐
    │ OpenClaw    │────▶│ Bridge       │────▶│ Security Engine │
    │ Session     │     │              │     │ (Repo Doctor)   │
    └─────────────┘     └──────────────┘     └─────────────────┘
                               │
                               ▼
                        ┌──────────────┐
                        │ Ollama       │
                        │ Native API   │
                        └──────────────┘
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone

UTC = timezone.utc

from enum import Enum
from pathlib import Path
from typing import Any

# Repo Doctor imports
from repo_doctor.security_scanner import (
    SecurityVerificationEngine,
    VerificationReceipt,
)

# ClawSpring imports
from clawspring.providers import stream_ollama

logger = logging.getLogger(__name__)


class AgentMode(Enum):
    """Operating modes for OpenClaw agents."""

    PERSISTENT = "persistent"  # Always-on assistant
    TASK = "task"  # One-shot task execution
    VERIFIER = "verifier"  # Security-focused verification agent
    REPAIR = "repair"  # Code repair with security gates


@dataclass
class OpenClawSession:
    """OpenClaw session configuration."""

    session_id: str
    workspace_id: str
    agent_mode: AgentMode
    ollama_base_url: str = "http://localhost:11434"
    model: str = "qwen2.5-coder:14b"
    enable_security_gates: bool = True
    auto_verify_patches: bool = True
    max_repair_attempts: int = 3
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class PatchProposal:
    """A proposed code patch with verification status."""

    patch_id: str
    session_id: str
    file_path: str
    original_content: str
    proposed_content: str
    description: str
    agent_reasoning: str
    verification_receipt: VerificationReceipt = None
    status: str = "pending"  # pending, verifying, blocked, approved, applied
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class OllamaNativeProvider:
    """Native Ollama API provider with proper tool calling support.

    Unlike OpenAI-compatible mode, native Ollama API supports reliable
    tool/function calling without compatibility issues.
    """

    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url.rstrip("/")
        self._available_models: list[str] = []

    async def check_health(self) -> bool:
        """Check if Ollama is available."""
        import aiohttp

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/api/tags", timeout=5) as resp:
                    return resp.status == 200
        except Exception:
            return False

    async def list_models(self) -> list[str]:
        """List available Ollama models."""
        import aiohttp

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/api/tags") as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        models = [m["name"] for m in data.get("models", [])]
                        self._available_models = models
                        return models
        except Exception as e:
            logger.warning(f"Failed to list Ollama models: {e}")
        return []

    def stream(
        self,
        model: str,
        system: str,
        messages: list[dict],
        tool_schemas: list[dict | None] = None,
        context_limit: int = 128000,
    ):
        """Stream from Ollama native API with tool support."""
        # Use clawspring's native Ollama streaming
        config = {"context_limit": context_limit}
        yield from stream_ollama(
            base_url=self.base_url,
            model=model,
            system=system,
            messages=messages,
            tool_schemas=tool_schemas or [],
            config=config,
        )


class SecurityGate:
    """Security verification gate for AI patches.

    All patches must pass through this gate before being applied.
    """

    def __init__(self, verification_engine: SecurityVerificationEngine = None):
        self.engine = verification_engine or SecurityVerificationEngine()
        self._patch_history: list[PatchProposal] = []

    async def verify_patch(
        self,
        patch: PatchProposal,
        repo_path: Path,
    ) -> PatchProposal:
        """Verify a patch through the security pipeline.

        Steps:
        1. Write proposed changes to temp location
        2. Run full security scan
        3. Generate verification receipt
        4. Update patch status
        """
        import shutil
        import tempfile

        patch.status = "verifying"

        # Create temp copy with proposed changes
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_repo = Path(temp_dir) / "repo"
            shutil.copytree(repo_path, temp_repo, ignore=lambda x, y: [".git"])

            # Apply proposed changes
            target_file = temp_repo / patch.file_path
            if target_file.exists():
                target_file.write_text(patch.proposed_content)

            # Run security verification
            receipt = await self.engine.verify(
                repo_path=temp_repo,
                commit_hash=None,
                receipt_id=patch.patch_id,
            )

            patch.verification_receipt = receipt

            # Determine status based on findings
            if (
                receipt.critical_count > 0
                or receipt.high_count > 0
                and patch.agent_mode != AgentMode.REPAIR
            ):
                patch.status = "blocked"
            elif receipt.overall_passed:
                patch.status = "approved"
            else:
                patch.status = "needs_review"

        self._patch_history.append(patch)
        return patch

    def get_blocking_findings(self, patch: PatchProposal) -> list[str]:
        """Get human-readable list of blocking issues."""
        if not patch.verification_receipt:
            return ["No verification receipt available"]

        blocking = []
        for finding in patch.verification_receipt.blocking_findings:
            blocking.append(
                f"[{finding.severity.value.upper()}] {finding.tool}: {finding.message}"
                f" ({finding.file_path}:{finding.line_number})"
            )
        return blocking


class OpenClawBridge:
    """First-class OpenClaw integration bridge.

    Provides:
    - Ollama-native provider connection (not /v1 compatible mode)
    - Security-gated patch workflow
    - Persistent agent sessions
    - Repo Doctor integration
    - AMOS Kernel Runtime binding
    """

    def __init__(
        self,
        ollama_url: str = "http://localhost:11434",
        workspace_dir: Path = None,
    ):
        self.ollama = OllamaNativeProvider(ollama_url)
        self.security_gate = SecurityGate()
        self.workspace_dir = workspace_dir or Path.cwd()
        self._sessions: dict[str, OpenClawSession] = {}
        self._memory: MemoryStore = None
        self._active_patches: dict[str, PatchProposal] = {}

    async def initialize(self) -> bool:
        """Initialize bridge and verify Ollama connection."""
        if not await self.ollama.check_health():
            logger.error(f"Ollama not available at {self.ollama.base_url}")
            return False

        models = await self.ollama.list_models()
        logger.info(f"OpenClaw Bridge initialized. Available models: {models}")
        return True

    def create_session(
        self,
        workspace_id: str,
        mode: AgentMode = AgentMode.PERSISTENT,
        model: str = "qwen2.5-coder:14b",
    ) -> OpenClawSession:
        """Create a new OpenClaw agent session."""
        import uuid

        session_id = f"claw-{uuid.uuid4().hex[:12]}"
        session = OpenClawSession(
            session_id=session_id,
            workspace_id=workspace_id,
            agent_mode=mode,
            ollama_base_url=self.ollama.base_url,
            model=model,
        )
        self._sessions[session_id] = session
        logger.info(f"Created OpenClaw session: {session_id} (mode={mode.value})")
        return session

    async def propose_patch(
        self,
        session: OpenClawSession,
        file_path: str,
        original: str,
        proposed: str,
        description: str,
        reasoning: str,
    ) -> PatchProposal:
        """Propose a code patch through the security-gated workflow.

        This is the core integration point: all AI patches go through
        Repo Doctor's security verification before being approved.
        """
        import uuid

        patch_id = f"patch-{uuid.uuid4().hex[:8]}"
        proposal = PatchProposal(
            patch_id=patch_id,
            session_id=session.session_id,
            file_path=file_path,
            original_content=original,
            proposed_content=proposed,
            description=description,
            agent_reasoning=reasoning,
        )

        if session.enable_security_gates:
            logger.info(f"Patch {patch_id} entering security verification...")
            proposal = await self.security_gate.verify_patch(proposal, self.workspace_dir)

            if proposal.status == "blocked":
                blocking = self.security_gate.get_blocking_findings(proposal)
                logger.warning(f"Patch {patch_id} BLOCKED by security findings:")
                for finding in blocking:
                    logger.warning(f"  - {finding}")
            elif proposal.status == "approved":
                logger.info(f"Patch {patch_id} APPROVED by security verification")
        else:
            proposal.status = "approved"

        self._active_patches[patch_id] = proposal
        return proposal

    async def repair_with_verification(
        self,
        session: OpenClawSession,
        issue_description: str,
        file_path: str,
        max_attempts: int = None,
    ) -> PatchProposal:
        """Iterative repair loop with security verification.

        Attempts to fix an issue, verifies the fix, and retries if
        security issues are introduced.
        """
        max_attempts = max_attempts or session.max_repair_attempts
        target_file = self.workspace_dir / file_path

        if not target_file.exists():
            logger.error(f"File not found: {file_path}")
            return None

        original_content = target_file.read_text()
        current_content = original_content

        for attempt in range(max_attempts):
            logger.info(f"Repair attempt {attempt + 1}/{max_attempts} for {file_path}")

            # Generate repair via Ollama
            repair_prompt = self._build_repair_prompt(issue_description, file_path, current_content)
            proposed = await self._generate_repair(session, repair_prompt)

            if not proposed:
                logger.error("Failed to generate repair")
                continue

            # Propose and verify
            patch = await self.propose_patch(
                session=session,
                file_path=file_path,
                original=current_content,
                proposed=proposed,
                description=f"Repair: {issue_description}",
                reasoning=f"Attempt {attempt + 1} generated by {session.model}",
            )

            if patch.status == "approved":
                logger.info(f"Repair approved after {attempt + 1} attempts")
                return patch

            # If blocked, use the blocking findings as context for next attempt
            if patch.status == "blocked":
                blocking = self.security_gate.get_blocking_findings(patch)
                issue_description += "\n\nPrevious attempt introduced issues:\n" + "\n".join(
                    blocking
                )
                current_content = proposed  # Try to fix the broken fix

        logger.error(f"Failed to generate passing repair after {max_attempts} attempts")
        return None

    async def apply_approved_patch(self, patch_id: str) -> bool:
        """Apply an approved patch to the workspace."""
        if patch_id not in self._active_patches:
            logger.error(f"Unknown patch: {patch_id}")
            return False

        patch = self._active_patches[patch_id]
        if patch.status != "approved":
            logger.error(f"Patch {patch_id} is not approved (status={patch.status})")
            return False

        target_file = self.workspace_dir / patch.file_path
        try:
            target_file.write_text(patch.proposed_content)
            patch.status = "applied"
            logger.info(f"Applied patch {patch_id} to {patch.file_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to apply patch: {e}")
            return False

    def _build_repair_prompt(self, issue: str, file_path: str, content: str) -> str:
        """Build repair prompt for the agent."""
        return f"""You are a security-conscious code repair agent.

FILE: {file_path}
ISSUE: {issue}

CURRENT CONTENT:
```
{content}
```

Provide the complete fixed version of this file. Your fix must:
1. Resolve the described issue
2. NOT introduce security vulnerabilities (no secrets, no injection risks)
3. NOT break existing functionality
4. Follow the existing code style

Return ONLY the fixed file content, no explanations."""

    async def _generate_repair(self, session: OpenClawSession, prompt: str) -> str:
        """Generate repair using Ollama."""
        messages = [{"role": "user", "content": prompt}]

        try:
            full_response = []
            for chunk in self.ollama.stream(
                model=session.model,
                system="You are a precise code repair agent. Output only valid code.",
                messages=messages,
            ):
                if hasattr(chunk, "text"):
                    full_response.append(chunk.text)

            return "".join(full_response)
        except Exception as e:
            logger.error(f"Generation failed: {e}")
            return None

    def get_session_status(self, session_id: str) -> dict[str, Any]:
        """Get status of an OpenClaw session."""
        if session_id not in self._sessions:
            return {"error": "Session not found"}

        session = self._sessions[session_id]
        patches = [p for p in self._active_patches.values() if p.session_id == session_id]

        return {
            "session_id": session_id,
            "workspace_id": session.workspace_id,
            "mode": session.agent_mode.value,
            "model": session.model,
            "security_gates_enabled": session.enable_security_gates,
            "patches_total": len(patches),
            "patches_approved": len([p for p in patches if p.status == "approved"]),
            "patches_blocked": len([p for p in patches if p.status == "blocked"]),
            "patches_applied": len([p for p in patches if p.status == "applied"]),
        }


# Global singleton
_openclaw_bridge: OpenClawBridge = None


def get_openclaw_bridge(
    ollama_url: str = "http://localhost:11434",
    workspace_dir: Path = None,
) -> OpenClawBridge:
    """Get or create global OpenClaw bridge."""
    global _openclaw_bridge
    if _openclaw_bridge is None:
        _openclaw_bridge = OpenClawBridge(ollama_url, workspace_dir)
    return _openclaw_bridge


async def demo():
    """Demonstrate OpenClaw Bridge workflow."""
    print("=" * 60)
    print("OpenClaw Bridge Demo - Security-Gated Repair Workflow")
    print("=" * 60)

    bridge = get_openclaw_bridge()

    if not await bridge.initialize():
        print("ERROR: Ollama not available. Start Ollama first.")
        return

    # Create repair session
    session = bridge.create_session(
        workspace_id="demo-workspace",
        mode=AgentMode.REPAIR,
        model="qwen2.5-coder:14b",
    )

    print(f"\nCreated session: {session.session_id}")
    print(f"Model: {session.model}")
    print(f"Security gates: {'ENABLED' if session.enable_security_gates else 'DISABLED'}")

    # Demo: Create a file with an issue
    demo_file = bridge.workspace_dir / "demo_vulnerable.py"
    vulnerable_code = """
import os

def run_command(user_input):
    # Security issue: command injection
    os.system("echo " + user_input)
    return True
"""
    demo_file.write_text(vulnerable_code)
    print(f"\nCreated demo file: {demo_file}")
    print("Issue: Command injection vulnerability")

    # Attempt repair with verification
    print("\n--- Attempting Repair with Security Verification ---")

    patch = await bridge.repair_with_verification(
        session=session,
        issue_description="Fix the command injection vulnerability in run_command function",
        file_path="demo_vulnerable.py",
        max_attempts=2,
    )

    if patch:
        print(f"\nPatch Status: {patch.status.upper()}")

        if patch.verification_receipt:
            receipt = patch.verification_receipt
            print(f"\nVerification Receipt: {receipt.receipt_id}")
            print(f"  Critical: {receipt.critical_count}")
            print(f"  High: {receipt.high_count}")
            print(f"  Medium: {receipt.medium_count}")
            print(f"  Low: {receipt.low_count}")

        if patch.status == "approved":
            print("\n✅ Patch approved! Applying...")
            await bridge.apply_approved_patch(patch.patch_id)

            # Show final content
            final = demo_file.read_text()
            print("\nFinal file content:")
            print(final)
        elif patch.status == "blocked":
            print("\n❌ Patch blocked by security findings:")
            for finding in bridge.security_gate.get_blocking_findings(patch):
                print(f"   - {finding}")

    # Cleanup
    demo_file.unlink(missing_ok=True)
    print("\n" + "=" * 60)
    print("Demo complete")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(demo())
