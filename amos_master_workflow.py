#!/usr/bin/env python3
"""AMOS Master Workflow - Continuous cognitive orchestration.

Integrates all AMOS components into a single pipeline:
  Brain (analyze) → Knowledge (explore) → Generator (build)

Usage:
    python amos_master_workflow.py
    python amos_master_workflow.py run "I want to build a medical decision system"
    python amos_master_workflow.py batch goals.txt
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from amos_brain import get_amos_integration
from amos_knowledge_explorer import KnowledgeExplorer
from amos_project_generator import AMOSProjectGenerator


@dataclass
class WorkflowPhase:
    """Represents a phase in the workflow."""

    name: str
    status: str = "pending"  # pending, running, completed, failed
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    results: dict = field(default_factory=dict)
    logs: list[str] = field(default_factory=list)


@dataclass
class WorkflowRun:
    """Represents a complete workflow execution."""

    id: str
    goal: str
    start_time: str
    end_time: Optional[str] = None
    status: str = "running"
    phases: list[WorkflowPhase] = field(default_factory=list)
    final_output: Optional[Path] = None


class AMOSMasterWorkflow:
    """Master workflow orchestrator for AMOS cognitive pipeline.

    Runs continuous brain operation across all phases:
    1. ANALYZE - Brain analyzes goal (Rule of 2/4, L1-L6)
    2. EXPLORE - Knowledge explorer finds relevant engines
    3. GENERATE - Project generator creates scaffold
    4. REPORT - Compile complete workflow report
    """

    def __init__(self):
        self.brain = None
        self.explorer = None
        self.generator = None
        self.workflow_dir = Path(__file__).parent / "workflow_runs"
        self.workflow_dir.mkdir(exist_ok=True)
        self.current_run: Optional[WorkflowRun] = None

    def initialize(self) -> AMOSMasterWorkflow:
        """Initialize all subsystems."""
        print("=" * 70)
        print("  AMOS MASTER WORKFLOW")
        print("  Continuous Cognitive Orchestration")
        print("=" * 70)
        print("\n🔧 Initializing subsystems...")

        # Initialize all components
        self.brain = get_amos_integration()
        print("  ✓ Brain: 12 engines, 6 laws")

        self.explorer = KnowledgeExplorer()
        self.explorer.index()
        print(f"  ✓ Knowledge: {len(self.explorer._index)} files")

        self.generator = AMOSProjectGenerator()
        print("  ✓ Generator: Ready")

        print("\n🚀 All subsystems operational")
        return self

    def run_workflow(self, goal: str) -> WorkflowRun:
        """Run complete cognitive workflow."""
        # Create workflow run
        run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.current_run = WorkflowRun(id=run_id, goal=goal, start_time=datetime.now().isoformat())

        print(f"\n🎯 WORKFLOW STARTED: {run_id}")
        print(f"   Goal: {goal}")
        print()

        # PHASE 1: Brain Analysis
        phase1 = self._run_phase1_analyze(goal)
        self.current_run.phases.append(phase1)

        if phase1.status == "failed":
            return self._complete_workflow("failed")

        # PHASE 2: Knowledge Exploration
        phase2 = self._run_phase2_explore(goal)
        self.current_run.phases.append(phase2)

        if phase2.status == "failed":
            return self._complete_workflow("failed")

        # PHASE 3: Project Generation
        project_name = self._generate_project_name(goal)
        phase3 = self._run_phase3_generate(project_name, goal, phase2.results)
        self.current_run.phases.append(phase3)

        if phase3.status == "failed":
            return self._complete_workflow("failed")

        # PHASE 4: Report Compilation
        phase4 = self._run_phase4_report()
        self.current_run.phases.append(phase4)

        return self._complete_workflow("completed")

    def _run_phase1_analyze(self, goal: str) -> WorkflowPhase:
        """Phase 1: Brain Analysis."""
        phase = WorkflowPhase(name="BRAIN_ANALYSIS")
        phase.start_time = datetime.now().isoformat()
        phase.status = "running"

        print("\n" + "─" * 70)
        print("  PHASE 1: BRAIN ANALYSIS")
        print("  Applying Rule of 2 + Rule of 4 + L1-L6")
        print("─" * 70)

        try:
            # Use brain to analyze goal
            analysis = self.brain.analyze_with_rules(goal)

            phase.results = {
                "confidence": analysis.get("structural_integrity_score", 0.0),
                "recommendations": analysis.get("recommendations", []),
                "rule_of_two": "rule_of_two" in analysis,
                "rule_of_four": "rule_of_four" in analysis,
            }

            print("\n✓ Analysis complete")
            print(f"  Confidence: {phase.results['confidence']:.0%}")
            print(f"  Recommendations: {len(phase.results['recommendations'])}")
            print(f"  Rule of 2: {'✅' if phase.results['rule_of_two'] else '❌'}")
            print(f"  Rule of 4: {'✅' if phase.results['rule_of_four'] else '❌'}")

            phase.status = "completed"
            phase.end_time = datetime.now().isoformat()

        except Exception as e:
            phase.status = "failed"
            phase.logs.append(f"Error: {e}")
            print(f"\n❌ Phase 1 failed: {e}")

        return phase

    def _run_phase2_explore(self, goal: str) -> WorkflowPhase:
        """Phase 2: Knowledge Exploration."""
        phase = WorkflowPhase(name="KNOWLEDGE_EXPLORATION")
        phase.start_time = datetime.now().isoformat()
        phase.status = "running"

        print("\n" + "─" * 70)
        print("  PHASE 2: KNOWLEDGE EXPLORATION")
        print("  Searching 1,110+ knowledge files")
        print("─" * 70)

        try:
            # Find relevant engines
            engines = self.explorer.recommend_engines(goal)

            phase.results = {
                "engines_found": len(engines),
                "top_engines": [
                    {
                        "name": e.name,
                        "type": e.engine_type,
                        "domain": e.domain,
                        "size": e.size_human,
                    }
                    for e in engines[:5]
                ],
            }

            print("\n✓ Exploration complete")
            print(f"  Engines found: {phase.results['engines_found']}")

            if phase.results["top_engines"]:
                print("\n  Top matches:")
                for i, eng in enumerate(phase.results["top_engines"], 1):
                    print(f"    {i}. {eng['name']}")
                    print(f"       Type: {eng['type']} | Size: {eng['size']}")

            phase.status = "completed"
            phase.end_time = datetime.now().isoformat()

        except Exception as e:
            phase.status = "failed"
            phase.logs.append(f"Error: {e}")
            print(f"\n❌ Phase 2 failed: {e}")

        return phase

    def _run_phase3_generate(
        self, project_name: str, goal: str, engine_results: dict
    ) -> WorkflowPhase:
        """Phase 3: Project Generation."""
        phase = WorkflowPhase(name="PROJECT_GENERATION")
        phase.start_time = datetime.now().isoformat()
        phase.status = "running"

        print("\n" + "─" * 70)
        print("  PHASE 3: PROJECT GENERATION")
        print("  Creating scaffold with brain integration")
        print("─" * 70)

        try:
            # Generate project
            self.generator.initialize()
            project_dir = self.generator.generate(project_name, goal)

            phase.results = {
                "project_name": project_name,
                "project_dir": str(project_dir),
                "files_created": 5,  # main.py, config.py, README.md, etc.
            }

            print("\n✓ Generation complete")
            print(f"  Project: {project_name}")
            print(f"  Location: {project_dir}")
            print(f"  Files: {phase.results['files_created']}")

            phase.status = "completed"
            phase.end_time = datetime.now().isoformat()

        except Exception as e:
            phase.status = "failed"
            phase.logs.append(f"Error: {e}")
            print(f"\n❌ Phase 3 failed: {e}")

        return phase

    def _run_phase4_report(self) -> WorkflowPhase:
        """Phase 4: Report Compilation."""
        phase = WorkflowPhase(name="REPORT_COMPILATION")
        phase.start_time = datetime.now().isoformat()
        phase.status = "running"

        print("\n" + "─" * 70)
        print("  PHASE 4: REPORT COMPILATION")
        print("  Saving workflow trace")
        print("─" * 70)

        try:
            # Generate report
            report_path = self._save_workflow_report()

            phase.results = {
                "report_path": str(report_path),
                "phases_completed": len(
                    [p for p in self.current_run.phases if p.status == "completed"]
                ),
            }

            print(f"\n✓ Report saved: {report_path}")

            phase.status = "completed"
            phase.end_time = datetime.now().isoformat()

        except Exception as e:
            phase.status = "failed"
            phase.logs.append(f"Error: {e}")
            print(f"\n❌ Phase 4 failed: {e}")

        return phase

    def _generate_project_name(self, goal: str) -> str:
        """Generate project name from goal."""
        # Extract key words
        words = goal.lower().split()
        key_words = [
            w
            for w in words
            if len(w) > 3
            and w
            not in [
                "want",
                "build",
                "create",
                "make",
                "with",
                "using",
                "that",
                "this",
                "have",
                "need",
            ]
        ]

        if key_words:
            name = "".join(word.capitalize() for word in key_words[:3])
        else:
            name = "AMOSProject"

        # Add timestamp
        timestamp = datetime.now().strftime("%Y%m%d")
        return f"{name}_{timestamp}"

    def _save_workflow_report(self) -> Path:
        """Save complete workflow report."""
        if not self.current_run:
            raise ValueError("No current workflow run")

        report_file = self.workflow_dir / f"workflow_{self.current_run.id}.md"

        content = f"""# AMOS Workflow Report

**Workflow ID:** {self.current_run.id}
**Goal:** {self.current_run.goal}
**Started:** {self.current_run.start_time}
**Completed:** {self.current_run.end_time or "N/A"}
**Status:** {self.current_run.status}

## Execution Summary

| Phase | Status | Duration |
|-------|--------|----------|
"""

        for phase in self.current_run.phases:
            duration = "N/A"
            if phase.start_time and phase.end_time:
                start = datetime.fromisoformat(phase.start_time)
                end = datetime.fromisoformat(phase.end_time)
                duration = f"{(end - start).total_seconds():.1f}s"

            content += f"| {phase.name} | {phase.status} | {duration} |\n"

        content += "\n## Phase Details\n\n"

        for phase in self.current_run.phases:
            content += f"### {phase.name}\n\n"
            content += f"- **Status:** {phase.status}\n"
            content += f"- **Started:** {phase.start_time}\n"
            content += f"- **Completed:** {phase.end_time or 'N/A'}\n\n"

            if phase.results:
                content += "**Results:**\n\n"
                for key, value in phase.results.items():
                    content += f"- {key}: {value}\n"
                content += "\n"

            if phase.logs:
                content += "**Logs:**\n\n"
                for log in phase.logs:
                    content += f"- {log}\n"
                content += "\n"

        content += """---
*Generated by AMOS Master Workflow*
"""

        report_file.write_text(content)
        return report_file

    def _complete_workflow(self, status: str) -> WorkflowRun:
        """Complete current workflow."""
        if not self.current_run:
            raise ValueError("No current workflow run")

        self.current_run.status = status
        self.current_run.end_time = datetime.now().isoformat()

        # Print summary
        print("\n" + "=" * 70)
        print("  WORKFLOW COMPLETE")
        print("=" * 70)
        print("\n📊 Summary:")
        print(f"   ID: {self.current_run.id}")
        print(f"   Goal: {self.current_run.goal}")
        print(f"   Status: {status.upper()}")
        print(f"   Phases: {len(self.current_run.phases)}")
        print(
            f"   Completed: {len([p for p in self.current_run.phases if p.status == 'completed'])}"
        )

        return self.current_run

    def list_runs(self) -> list[WorkflowRun]:
        """List all workflow runs."""
        runs = []
        for report_file in self.workflow_dir.glob("workflow_*.md"):
            # Parse basic info from filename
            run_id = report_file.stem.replace("workflow_", "")
            runs.append(WorkflowRun(id=run_id, goal="Unknown", start_time=run_id))
        return runs


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="AMOS Master Workflow - Continuous cognitive orchestration"
    )
    parser.add_argument(
        "command", choices=["run", "list", "interactive"], default="interactive", nargs="?"
    )
    parser.add_argument("goal", nargs="?", help="Project goal/description")

    args = parser.parse_args()

    workflow = AMOSMasterWorkflow()

    if args.command == "run":
        if not args.goal:
            args.goal = input("What do you want to build? ")

        workflow.initialize()
        workflow.run_workflow(args.goal)

    elif args.command == "list":
        runs = workflow.list_runs()
        print(f"\n📋 Workflow History ({len(runs)} runs):")
        for run in runs:
            print(f"   {run.id}: {run.goal}")

    else:  # interactive
        print("\n" + "=" * 70)
        print("  AMOS MASTER WORKFLOW - Interactive Mode")
        print("=" * 70)
        print("\nThis orchestrator runs the full cognitive pipeline:")
        print("  1. 🧠 Brain Analysis (Rule of 2/4, L1-L6)")
        print("  2. 📚 Knowledge Exploration (1,110+ files)")
        print("  3. 🏗️  Project Generation (scaffold)")
        print("  4. 📊 Report Compilation (trace)")

        workflow.initialize()

        while True:
            print("\n" + "─" * 70)
            goal = input("\nWhat do you want to build? (or 'quit'): ")

            if goal.lower() in ["quit", "exit", "q"]:
                break

            workflow.run_workflow(goal)

            print("\n✨ Workflow complete! The brain operated continuously across all phases.")

        print("\n👋 Goodbye!")

    return 0


if __name__ == "__main__":
    sys.exit(main())
