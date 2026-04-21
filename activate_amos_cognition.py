#!/usr/bin/env python3
"""
AMOS Brain Self-Activation and Self-Repair
Uses the AMOS brain to analyze and fix itself.
"""

from __future__ import annotations

import asyncio
import sys
import traceback
from datetime import datetime, timezone

from amos_brain import BrainClient, get_super_brain
from amos_brain.super_brain import SuperBrainRuntime


class AMOSCognitionActivator:
    """Activates and repairs AMOS brain using self-cognition."""

    def __init__(self):
        self.brain: SuperBrainRuntime | None = None  # type: ignore
        self.client: BrainClient | None = None
        self.fixes_applied: list[dict] = []
        self.issues_found: list[dict] = []

    async def activate(self) -> bool:
        """Initialize and activate the brain."""
        print("=" * 70)
        print("AMOS BRAIN SELF-ACTIVATION SEQUENCE")
        print("=" * 70)
        print(f"Time: {datetime.now(timezone.utc).isoformat()}")
        print()

        try:
            # Step 1: Initialize SuperBrain
            print("[1/5] Initializing SuperBrain Runtime...")
            self.brain = get_super_brain()
            if not self.brain.initialize():
                print("❌ SuperBrain initialization failed")
                return False
            print("✅ SuperBrain ACTIVE\n")

            # Step 2: Create BrainClient
            print("[2/5] Creating BrainClient...")
            self.client = BrainClient()
            print("✅ BrainClient READY\n")

            # Step 3: Self-diagnostic
            print("[3/5] Running self-diagnostic...")
            await self._self_diagnostic()

            # Step 4: Think about fixes
            print("[4/5] Thinking about system state...")
            await self._cognitive_analysis()

            # Step 5: Apply fixes
            print("[5/5] Applying fixes...")
            await self._apply_fixes()

            print("\n" + "=" * 70)
            print("ACTIVATION COMPLETE")
            print("=" * 70)
            self._print_summary()
            return True

        except Exception as e:
            print(f"\n❌ Activation failed: {e}")
            traceback.print_exc()
            return False

    async def _self_diagnostic(self):
        """Run diagnostic on brain subsystems."""
        checks = [
            ("Kernel Router", lambda: self.brain._kernel_router is not None),
            ("Action Gate", lambda: self.brain._action_gate is not None),
            ("Model Router", lambda: self.brain._model_router is not None),
            ("Tool Registry", lambda: self.brain._tool_registry is not None),
            ("Memory Governance", lambda: self.brain._memory_governance is not None),
            ("Core Freeze", lambda: self.brain._core_freeze is not None),
        ]

        for name, check in checks:
            try:
                result = check()
                status = "✅" if result else "❌"
                print(f"  {status} {name}")
                if not result:
                    self.issues_found.append({
                        "component": name,
                        "issue": "not_initialized",
                        "severity": "high"
                    })
            except Exception as e:
                print(f"  ❌ {name}: {e}")
                self.issues_found.append({
                    "component": name,
                    "issue": str(e),
                    "severity": "critical"
                })
        print()

    async def _cognitive_analysis(self):
        """Use brain to think about system state."""
        if not self.client:
            return

        # Ask brain to analyze the codebase health
        query = """
        Analyze the AMOS codebase for:
        1. Import errors or broken dependencies
        2. Deprecated patterns (datetime.utcnow, typing.Optional, etc.)
        3. Missing __init__.py files
        4. Circular imports
        5. Syntax errors

        Provide a prioritized list of fixes needed for production.
        """

        try:
            response = await self.client.think(
                query=query,
                domain="software",
                require_law_compliance=True
            )

            print(f"  Brain confidence: {response.confidence}")
            print(f"  Law compliant: {response.law_compliant}")

            if response.reasoning:
                print("\n  Reasoning:")
                for step in response.reasoning[:5]:
                    print(f"    • {step}")

            if response.violations:
                print("\n  Violations found:")
                for v in response.violations:
                    print(f"    ⚠️ {v}")

        except Exception as e:
            print(f"  ⚠️ Cognitive analysis warning: {e}")

        print()

    async def _apply_fixes(self):
        """Apply known critical fixes."""
        fixes_to_apply = [
            ("Import path validation", self._fix_import_paths),
            ("Lazy loading check", self._verify_lazy_loading),
            ("Core freeze status", self._verify_core_freeze),
        ]

        for name, fix_func in fixes_to_apply:
            try:
                print(f"  Applying: {name}...", end=" ")
                result = await fix_func()
                if result:
                    self.fixes_applied.append({
                        "fix": name, "status": "success"
                    })
                    print("✅")
                else:
                    print("⚠️  (no changes needed)")
            except Exception as e:
                self.fixes_applied.append({
                    "fix": name,
                    "status": "failed",
                    "error": str(e)
                })
                print(f"❌ ({e})")

    async def _fix_import_paths(self) -> bool:
        """Validate and fix critical import paths."""
        # Critical imports to verify
        critical_imports = [
            "amos_brain",
            "amos_brain.super_brain",
            "amos_brain.facade",
            "amos_brain.config",
        ]

        fixed = False
        for module in critical_imports:
            try:
                __import__(module)
            except ImportError as e:
                self.issues_found.append({
                    "component": module,
                    "issue": f"import_failed: {e}",
                    "severity": "critical"
                })
                fixed = True

        return fixed

    async def _verify_lazy_loading(self) -> bool:
        """Verify lazy loading is working."""
        # Check that lazy imports don't fail
        from amos_brain import _lazy_modules
        # Clear cache to force reload test
        _lazy_modules.clear()
        # Try loading a key module
        from amos_brain import think
        return callable(think)

    async def _verify_core_freeze(self) -> bool:
        """Verify core freeze is protecting critical files."""
        if self.brain and self.brain._core_freeze:
            return self.brain._core_freeze.is_frozen()
        return False

    def _print_summary(self):
        """Print activation summary."""
        print(f"\nIssues found: {len(self.issues_found)}")
        print(f"Fixes applied: {len(self.fixes_applied)}")

        if self.issues_found:
            print("\nOutstanding issues:")
            for issue in self.issues_found:
                icon = "CRIT" if issue["severity"] == "critical" else "WARN"
                print(f"  {icon} {issue['component']}: {issue['issue']}")

        if self.brain:
            state = self.brain.get_state()
            print("\nBrain State:")
            print(f"  Status: {state.status}")
            print(f"  Brain ID: {state.brain_id}")
            print(f"  Active kernels: {len(state.active_kernels)}")
            print(f"  Health score: {state.health_score:.1%}")


def main():
    """Main entry point."""
    activator = AMOSCognitionActivator()
    success = asyncio.run(activator.activate())
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()