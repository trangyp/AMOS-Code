#!/usr/bin/env python3
"""
AMOS Unified CLI (14_INTERFACES)
===============================

Command-line interface for the complete AMOS system:
- Brain (cognition)
- Organism (execution)
- Bridge (coordination)

Owner: Trang
Version: 2.0.0 - Now with standalone amos_brain
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import List, Optional

# Add paths for standalone brain
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent))


def get_organism_root() -> Path:
    """Get the organism root directory."""
    return Path(__file__).parent.parent


def cmd_status(args) -> int:
    """Show organism status."""
    root = get_organism_root()

    print("AMOS Organism Status")
    print("=" * 50)

    # Load world state
    state_path = root / "world_state.json"
    if state_path.exists():
        with open(state_path, 'r', encoding='utf-8') as f:
            state = json.load(f)

        health = state.get("system_health", {})
        print(f"Overall Status: {health.get('overall_status', 'unknown')}")
        print(f"Last Check: {health.get('last_check', 'unknown')}")

        print("\nSubsystems:")
        for code, status in health.get("subsystems", {}).items():
            indicator = "●" if status == "active" else "○"
            print(f"  {indicator} {code}: {status}")

    # Load pipeline state
    pipeline_path = root / "memory" / "pipeline_state.json"
    if pipeline_path.exists():
        with open(pipeline_path, 'r', encoding='utf-8') as f:
            pipeline = json.load(f)

        print("\nPipeline:")
        print(f"  Cycles: {pipeline.get('status', {}).get('cycle_count', 0)}")
        print(f"  Errors: {pipeline.get('status', {}).get('error_count', 0)}")

    return 0


def cmd_run(args) -> int:
    """Run the orchestrator."""
    root = get_organism_root()
    orchestrator = root / "AMOS_ONECLICK_ORCHESTRATOR.py"

    if not orchestrator.exists():
        print("[ERROR] Orchestrator not found")
        return 1

    import subprocess
    result = subprocess.run([sys.executable, str(orchestrator)])
    return result.returncode


def cmd_agents(args) -> int:
    """List or manage agents."""
    root = get_organism_root()
    factory_dir = root / "13_FACTORY"

    if args.action == "list":
        agents_dir = factory_dir / "agents"
        if not agents_dir.exists():
            print("No agents created yet")
            return 0

        registry = agents_dir / "registry.json"
        if registry.exists():
            with open(registry, 'r', encoding='utf-8') as f:
                data = json.load(f)

            print(f"Agents ({data.get('agent_count', 0)} total):")
            for agent in data.get("agents", []):
                print(f"  - {agent['id']}: {agent['spec']['name']} ({agent['status']})")
        else:
            print("No agent registry found")

    elif args.action == "create":
        # Create standard agents
        sys.path.insert(0, str(factory_dir))
        from agent_factory import AgentFactory

        factory = AgentFactory(root)
        agents = factory.create_standard_agents()
        print(f"Created {len(agents)} agents")

    return 0


def cmd_workers(args) -> int:
    """Execute worker tasks."""
    root = get_organism_root()
    muscle_dir = root / "06_MUSCLE"

    sys.path.insert(0, str(muscle_dir))
    from amos_worker_engine import get_worker_engine

    engine = get_worker_engine(root)

    if args.task == "write":
        plan = {
            "steps": [
                {
                    "action": "write_file",
                    "content": args.content,
                    "target_file": args.file
                }
            ]
        }
        result = engine.execute_plan(plan)
        print(f"Success: {result.success}")
        if result.artifacts:
            print(f"Created: {result.artifacts}")

    elif args.task == "analyze":
        plan = {
            "steps": [
                {
                    "action": "analyze",
                    "topic": args.topic
                }
            ]
        }
        result = engine.execute_plan(plan)
        print(result.output)

    return 0


def cmd_brain(args) -> int:
    """Interact with standalone AMOS brain package."""
    try:
        from amos_brain import get_amos_integration
        from amos_brain.memory import get_brain_memory
        from amos_brain.dashboard import print_dashboard
        from amos_brain.cookbook import ArchitectureDecision

        amos = get_amos_integration()

        if args.action == "status":
            status = amos.get_status()
            print("AMOS Brain Status (Standalone Package)")
            print("=" * 50)
            print(f"Initialized: {status.get('initialized')}")
            print(f"Engines: {status.get('engines_count')} domain engines")
            print(f"Laws: {len(status.get('laws_active', []))} global laws")
            print("\nActive Laws:")
            for law in status.get('laws_active', []):
                print(f"  • {law}")

        elif args.action == "think":
            if not args.question:
                print("[ERROR] --question required for think action")
                return 1
            print(f"Analyzing: {args.question}")
            print("-" * 50)
            analysis = amos.analyze_with_rules(args.question)
            print(f"\nRule of 2 Confidence: {analysis.get('rule_of_two', {}).get('confidence', 0):.0%}")
            print(f"Rule of 4 Coverage: {analysis.get('rule_of_four', {}).get('completeness_score', 0):.0%}")
            print("\nRecommendations:")
            for rec in analysis.get('recommendations', []):
                print(f"  • {rec}")

        elif args.action == "engines":
            status = amos.get_status()
            print(f"Domain Engines ({status.get('engines_count', 0)}):")
            for domain in status.get('domains_covered', []):
                print(f"  • {domain}")

        elif args.action == "dashboard":
            days = int(args.days) if hasattr(args, 'days') else 30
            print_dashboard(days)

        elif args.action == "memory":
            memory = get_brain_memory()
            if args.subaction == "history":
                history = memory.get_reasoning_history(limit=args.limit or 5)
                print(f"Reasoning History (last {len(history)}):")
                for entry in history:
                    print(f"  [{entry.get('timestamp', 'unknown')[:10]}] {entry.get('problem_preview', 'N/A')[:50]}...")
            elif args.subaction == "recall":
                if not args.query:
                    print("[ERROR] --query required for recall")
                    return 1
                recall = memory.recall_for_problem(args.query)
                if recall.get("has_prior_reasoning"):
                    print(f"Found {len(recall.get('similar_entries', []))} similar past analyses")
                else:
                    print("No similar past reasoning found")

    except Exception as e:
        print(f"[ERROR] Brain error: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


def cmd_bridge(args) -> int:
    """Execute tasks through brain-organism bridge."""
    try:
        from amos_brain_organism_bridge import BrainOrganismBridge

        bridge = BrainOrganismBridge()

        if args.action == "status":
            status = bridge.get_system_status()
            print("Brain-Organism Bridge Status")
            print("=" * 50)
            print(f"Brain: {status['brain']['engines']} engines, {status['brain']['laws']} laws")
            print(f"Organism: {'Connected' if status['organism']['connected'] else 'Stub mode'}")
            print(f"Bridge: {status['bridge']['status']} (v{status['bridge']['version']})")

        elif args.action == "execute":
            if not args.task:
                print("[ERROR] --task required")
                return 1

            print(f"Executing: {args.task}")
            print("-" * 50)

            context = {}
            if args.context:
                context = json.loads(args.context)

            result = bridge.analyze_and_execute(args.task, context)

            print(f"\nStatus: {result.status.upper()}")
            print(f"Action: {result.organism_action}")
            print(f"Resources: {result.resources_used}")
            print(f"\nOutput:\n{result.output}")

    except Exception as e:
        print(f"[ERROR] Bridge error: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


def cmd_blood(args) -> int:
    """Interact with BLOOD financial engine."""
    root = get_organism_root()
    blood_dir = root / "04_BLOOD"

    sys.path.insert(0, str(blood_dir))
    from financial_engine import FinancialEngine

    engine = FinancialEngine(root)

    if args.action == "status":
        status = engine.get_status()
        print("BLOOD Financial Status")
        print("=" * 40)
        print(f"Status: {status['status']}")
        print(f"Budget categories: {status['budget_categories']}")
        print(f"Active allocations: {status['active_allocations']}")
        print(f"Total transactions: {status['total_transactions']}")

        print("\nBudget Status:")
        for cat, budget in status['budget_status'].items():
            if budget:
                print(f"  {cat}: ${budget['remaining']:.2f} remaining")

    elif args.action == "budget":
        if args.category and args.amount:
            engine.set_budget(args.category, args.amount, args.period)
            print(f"Set budget for {args.category}: ${args.amount}")
        else:
            print("Usage: amos blood budget --category compute --amount 100")

    return 0


def cmd_knowledge(args) -> int:
    """Manage knowledge packs (15_KNOWLEDGE_CORE)."""
    root = get_organism_root()
    knowledge_dir = root / "15_KNOWLEDGE_CORE"

    sys.path.insert(0, str(knowledge_dir))
    from knowledge_pack_loader import KnowledgePackLoader

    loader = KnowledgePackLoader()

    if args.action == "status":
        status = loader.get_status()
        print("Knowledge Pack Status (15_KNOWLEDGE_CORE)")
        print("=" * 50)
        print(f"Total packs: {status['total_packs']}")
        print(f"Total size: {status['total_size_mb']} MB")
        print(f"Loader ready: {status['loaded']}")
        print("\nPack Distribution:")
        for pack_type, count in status['stats'].items():
            if count > 0:
                print(f"  - {pack_type}: {count}")

    elif args.action == "list":
        status = loader.get_status()
        print("Knowledge Packs")
        print("=" * 50)
        for name in status['pack_names']:
            pack = loader.get_pack(name)
            if pack:
                size_kb = round(pack.size_bytes / 1024, 1)
                print(f"  ✓ {name}")
                print(f"    Type: {pack.pack_type}")
                print(f"    Size: {size_kb} KB")
                print()

    elif args.action == "query":
        if args.type:
            packs = loader.query_packs_by_type(args.type)
            print(f"Query: type='{args.type}'")
            print("=" * 50)
            print(f"Found {len(packs)} packs")
            for pack in packs[:5]:
                print(f"  - {pack.name} ({pack.pack_type})")
        else:
            print("Usage: amos knowledge query --type country")

    return 0


def cmd_api(args) -> int:
    """Manage API server."""
    import subprocess
    import signal
    import time

    root = get_organism_root()
    repo_root = root.parent
    pid_file = root / ".api_server.pid"

    if args.action == "start":
        if pid_file.exists():
            print("API server already running")
            return 1

        print(f"Starting API server on {args.host}:{args.port}")
        print(f"  Repository: {repo_root}")

        # Start server in background
        env = os.environ.copy()
        env['FLASK_APP'] = str(repo_root / 'amos_api_server.py')
        env['AMOS_ROOT'] = str(root)

        cmd = [
            sys.executable, "-m", "flask", "run",
            "--host", args.host,
            "--port", str(args.port)
        ]
        if args.debug:
            cmd.append("--debug")

        try:
            proc = subprocess.Popen(
                cmd, cwd=str(repo_root), env=env,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            pid_file.write_text(str(proc.pid))
            time.sleep(2)  # Wait for startup

            print(f"✓ API server started (PID: {proc.pid})")
            print(f"  URL: http://{args.host}:{args.port}")
            print(f"  Health: http://{args.host}:{args.port}/health")
            print(f"  API Docs: http://{args.host}:{args.port}/")
        except Exception as e:
            print(f"Failed to start: {e}")
            return 1

    elif args.action == "stop":
        if not pid_file.exists():
            print("API server not running")
            return 1

        pid = int(pid_file.read_text())
        try:
            os.kill(pid, signal.SIGTERM)
            pid_file.unlink()
            print(f"✓ API server stopped (PID: {pid})")
        except ProcessLookupError:
            pid_file.unlink()
            print("API server not running (stale PID file)")
        except Exception as e:
            print(f"Error stopping: {e}")
            return 1

    elif args.action == "status":
        if pid_file.exists():
            pid = pid_file.read_text().strip()
            print(f"API server: running (PID: {pid})")
            print(f"  PID file: {pid_file}")
        else:
            print("API server: not running")
        print(f"  Default URL: http://127.0.0.1:5000")
        print(f"  API endpoints:")
        print(f"    GET  /api/workflows      - List workflows")
        print(f"    POST /api/workflows/<id>/run - Run workflow")
        print(f"    GET  /api/pipelines      - List pipelines")
        print(f"    POST /api/pipelines/<id>/run - Run pipeline")
        print(f"    GET  /api/alerts/active  - Active alerts")
        print(f"    POST /api/alerts/evaluate - Evaluate metrics")
        print(f"    POST /api/orchestrator/cycle - Trigger cycle")

    return 0

def cmd_cognitive(args) -> int:
    """Manage cognitive engines (01_BRAIN)."""
    root = get_organism_root()
    brain_dir = root / "01_BRAIN"

    sys.path.insert(0, str(brain_dir))
    from cognitive_engine_activator import CognitiveEngineActivator

    activator = CognitiveEngineActivator()

    if args.action == "status":
        status = activator.get_status()
        print("Cognitive Engine Status")
        print("=" * 50)
        print(f"Engines loaded: {status['engines_count']}")
        print(f"Total size: {status['total_size_mb']} MB")
        print(f"Domains covered: {len(status['domains'])}")
        print("\nDomain Distribution:")
        for domain, count in sorted(status['domains'].items()):
            print(f"  - {domain}: {count} engines")

    elif args.action == "list":
        status = activator.get_status()
        print("Active Cognitive Engines")
        print("=" * 50)
        for name in status['engine_names']:
            engine = activator.get_engine(name)
            if engine:
                size_kb = round(engine.size_bytes / 1024, 1)
                print(f"  ✓ {engine.name}")
                print(f"    Domain: {engine.domain}")
                print(f"    Size: {size_kb} KB")
                print()

    elif args.action == "query":
        domain = args.domain or "Design"
        query = args.engine or "general"
        result = activator.query_domain(domain, query)
        print(f"Query: '{query}' in domain '{domain}'")
        print("=" * 50)
        print(f"Matching engines: {result['matching_engines']}")
        for eng in result['engines']:
            print(f"  - {eng['engine']}")
            print(f"    {eng['description']}")

    return 0


def cmd_alert(args) -> int:
    """Manage alerts and notifications."""
    root = get_organism_root()
    immune_dir = root / "03_IMMUNE"

    sys.path.insert(0, str(immune_dir))
    from alert_manager import AlertManager

    manager = AlertManager(root)

    if args.action == "status":
        status = manager.get_status()
        print("Alert System Status")
        print("=" * 40)
        print(f"Rules configured: {status['rules_configured']}")
        print(f"Channels configured: {status['channels_configured']}")
        print(f"Active alerts: {status['active_alerts']}")
        print(f"Total alerts (all time): {status['total_alerts_ever']}")

    elif args.action == "list":
        active = manager.get_active_alerts()
        history = manager.get_alert_history(limit=10)
        print("Active Alerts")
        print("=" * 40)
        if active:
            for alert in active:
                icon = "🔴" if alert['severity'] == "critical" else "⚠️" if alert['severity'] == "warning" else "ℹ️"
                print(f"{icon} {alert['id']}: {alert['rule_name']}")
                print(f"   {alert['message']}")
        else:
            print("  No active alerts")

        print("\nRecent Alert History (last 10)")
        print("=" * 40)
        if history:
            for alert in history:
                print(f"  {alert['id']}: {alert['rule_name']} ({alert['status']})")
        else:
            print("  No alert history")

    elif args.action == "test":
        metric = args.metric or "subsystem_load"
        value = args.value
        print(f"Testing alert rule for {metric} = {value}")
        print("=" * 40)

        metrics = {metric: value}
        alerts = manager.evaluate_and_alert(metrics)

        if alerts:
            print(f"\n✓ Generated {len(alerts)} alerts:")
            for alert in alerts:
                print(f"  - {alert['rule_name']} ({alert['severity']})")
                print(f"    {alert['message']}")
        else:
            print("\n✓ No alerts triggered (metric within threshold)")

    return 0


def cmd_pipeline(args) -> int:
    """Manage data pipelines."""
    root = get_organism_root()
    metabolism_dir = root / "07_METABOLISM"

    sys.path.insert(0, str(metabolism_dir))
    from pipeline_engine import PipelineEngine, Pipeline, PipelineStage

    engine = PipelineEngine()

    if args.action == "list":
        pipelines = list(engine.pipelines.values())
        print("Data Pipelines")
        print("=" * 40)
        if pipelines:
            for pipe in pipelines:
                print(f"  {pipe.id}: {pipe.name} ({pipe.status})")
        else:
            print("  No pipelines found")
            print("\nCreate one with: amos pipeline create --name 'My Pipeline'")

    elif args.action == "create":
        name = args.name or "New Pipeline"
        pipe = engine.create_pipeline(name, "Created via CLI")
        # Add demo stages
        pipe.add_stage(PipelineStage(name="Transform", stage_type="transform", config={"transform": "uppercase"}))
        pipe.add_stage(PipelineStage(name="Validate", stage_type="validate", config={"required_fields": ["data"]}))
        pipe.add_stage(PipelineStage(name="Log", stage_type="log", config={"message": "Pipeline complete"}))
        engine.save()
        print(f"Created pipeline: {pipe.id}")
        print(f"Name: {pipe.name}")
        print(f"Stages: {len(pipe.stages)}")

    elif args.action == "run":
        if not args.pipeline_id:
            print("Error: --pipeline-id required")
            return 1
        pipe = engine.pipelines.get(args.pipeline_id)
        if not pipe:
            print(f"Pipeline not found: {args.pipeline_id}")
            return 1
        print(f"Running pipeline: {pipe.name}")
        result = engine.execute_pipeline(args.pipeline_id, initial_data="Hello World")
        print(f"Success: {result['success']}")
        print(f"Stages executed: {len(result['results'])}")
        for stage_id, res in result['results'].items():
            status = res.get('status', 'unknown')
            icon = "✓" if status == "completed" else "✗" if status == "failed" else "○"
            print(f"  {icon} {stage_id}: {status}")

    elif args.action == "status":
        pipelines = list(engine.pipelines.values())
        print("Pipeline Status")
        print("=" * 40)
        for pipe in pipelines:
            stage_count = len(pipe.stages)
            completed = sum(1 for s in pipe.stages if s.status.value == "completed")
            print(f"{pipe.id}: {pipe.name}")
            print(f"  Status: {pipe.status} | Stages: {completed}/{stage_count}")

    return 0


def cmd_workflow(args) -> int:
    """Manage workflows."""
    root = get_organism_root()
    muscle_dir = root / "06_MUSCLE"

    sys.path.insert(0, str(muscle_dir))
    from workflow_engine import WorkflowEngine, Workflow, WorkflowStep

    engine = WorkflowEngine()

    if args.action == "list":
        workflows = engine.list_workflows()
        print("Workflows")
        print("=" * 40)
        if workflows:
            for wf in workflows:
                print(f"  {wf.id}: {wf.name} ({wf.status})")
        else:
            # Create a demo workflow if none exist
            print("No workflows found. Creating demo workflow...")
            wf = engine.create_workflow("Demo Workflow", "Sample workflow")
            wf.add_step("Step 1: Analyze", "analyze", {"target": "code"})
            wf.add_step("Step 2: Transform", "transform", {"type": "refactor"})
            wf.add_step("Step 3: Validate", "validate", {}, depends_on=[wf.steps[1].id])
            engine._save_workflow(wf)
            print(f"Created demo workflow: {wf.id}")

    elif args.action == "create":
        name = args.name or "New Workflow"
        wf = engine.create_workflow(name, "Created via CLI")
        print(f"Created workflow: {wf.id}")
        print(f"Name: {wf.name}")
        print("\nUse --workflow-id to add steps and run")

    elif args.action == "run":
        if not args.workflow_id:
            print("Error: --workflow-id required")
            return 1
        wf = engine.load_workflow(args.workflow_id)
        if not wf:
            print(f"Workflow not found: {args.workflow_id}")
            return 1
        print(f"Running workflow: {wf.name}")
        result = engine.run_workflow(args.workflow_id)
        print(f"Status: {result.status}")
        print(f"Steps: {len(result.steps)}")
        for step in result.steps:
            status_icon = "✓" if step.status.value == "success" else "✗" if step.status.value == "failed" else "○"
            print(f"  {status_icon} {step.name}: {step.status.value}")

    elif args.action == "status":
        workflows = engine.list_workflows()
        print("Workflow Status")
        print("=" * 40)
        for wf in workflows:
            step_count = len(wf.steps)
            completed = sum(1 for s in wf.steps if s.status.value == "success")
            print(f"{wf.id}: {wf.name}")
            print(f"  Status: {wf.status} | Steps: {completed}/{step_count}")

    return 0


def cmd_predict(args) -> int:
    """Show predictive analytics forecast."""
    root = get_organism_root()
    quantum_dir = root / "12_QUANTUM_LAYER"

    sys.path.insert(0, str(quantum_dir))
    from predictive_engine import PredictiveEngine

    engine = PredictiveEngine(root)

    if args.target == "all":
        print(engine.get_forecast_summary())
    elif args.target == "queue":
        print("Queue Forecast")
        print("=" * 40)
        try:
            sys.path.insert(0, str(root / "07_METABOLISM"))
            from task_queue import TaskQueue
            queue = TaskQueue(root)
            status = queue.get_status()
            pred = engine.predict_queue_clearance(status.get("pending", 0))
            print(f"Pending tasks: {status.get('pending', 0)}")
            print(f"Estimated clearance: {pred.horizon}")
            print(f"Confidence: {pred.confidence*100:.0f}%")
        except Exception as e:
            print(f"Error: {e}")
    elif args.target == "resources":
        print("Resource Forecast (24h)")
        print("=" * 40)
        for resource in ["compute", "storage", "budget"]:
            pred = engine.predict_resource_usage(resource, 24)
            print(f"{resource}: {pred.predicted_value:.1f}%")

    return 0


def cmd_execute(args) -> int:
    """Execute pending tasks via Task Executor."""
    root = get_organism_root()
    muscle_dir = root / "06_MUSCLE"

    sys.path.insert(0, str(muscle_dir))
    from task_executor import AgentTaskRouter

    router = AgentTaskRouter(root)

    print("Executing pending tasks...")
    print("=" * 40)

    results = router.process_pending_tasks(max_tasks=args.count)

    if results:
        print(f"\nExecuted {len(results)} tasks:")
        for r in results:
            status = "✓" if r["success"] else "✗"
            print(f"  {status} Task {r['task_id']} by {r['agent_id']}")
    else:
        print("\nNo pending tasks to execute")

    # Show status
    status = router.get_status()
    print(f"\nRemaining: {status['tasks_pending']} pending")

    return 0


def cmd_task(args) -> int:
    """Interact with Task Queue."""
    root = get_organism_root()
    metabolism_dir = root / "07_METABOLISM"

    sys.path.insert(0, str(metabolism_dir))
    from task_queue import TaskQueue, TaskPriority

    queue = TaskQueue(root)

    if args.action == "status":
        status = queue.get_status()
        print("Task Queue Status")
        print("=" * 40)
        print(f"Status: {status['status']}")
        print(f"Total tasks: {status['total_tasks']}")
        print(f"Pending: {status['pending']}")
        print(f"Running: {status['running']}")
        print(f"Completed: {status['completed']}")

    elif args.action == "list":
        print("\nPending Tasks:")
        for task in queue.get_pending_tasks():
            print(f"  [{task.priority.name}] {task.title}")

    elif args.action == "submit":
        if args.title:
            priority = getattr(TaskPriority, args.priority.upper())
            queue.submit_task(
                title=args.title,
                description=args.description or "",
                task_type=args.type,
                source_subsystem="CLI",
                priority=priority
            )
            print(f"Task submitted: {args.title}")
        else:
            print("Usage: amos task submit -t 'Task title' -d 'Description'")

    return 0


def cmd_factory(args) -> int:
    """Interact with Agent Factory."""
    root = get_organism_root()
    factory_dir = root / "13_FACTORY"

    sys.path.insert(0, str(factory_dir))
    from agent_factory import AgentFactory

    factory = AgentFactory(root)

    if args.action == "status":
        report = factory.get_quality_report()
        print("Agent Factory Status")
        print("=" * 40)
        print(f"Total agents: {report['total_agents']}")
        print(f"Active: {report['active_agents']}")
        print(f"By type: {report['agents_by_type']}")

    return 0


def cmd_life(args) -> int:
    """Interact with LIFE engine."""
    root = get_organism_root()
    life_dir = root / "10_LIFE_ENGINE"

    sys.path.insert(0, str(life_dir))
    from life_engine import LifeEngine

    engine = LifeEngine(root)

    if args.action == "status":
        status = engine.get_status()
        print("LIFE Engine Status")
        print("=" * 40)
        print(f"Status: {status['status']}")
        print(f"Routines: {status['routines']['completed_today']}/"
              f"{status['routines']['total']} completed")
        print(f"Habits tracked: {status['habits']['total']}")
        print(f"Active goals: {status['goals']['active']}")

    elif args.action == "schedule":
        schedule = engine.get_today_schedule()
        print("\nToday's Schedule:")
        for item in schedule:
            status = "✓" if item["completed"] else "○"
            print(f"  {status} [{item['time']}] {item['activity']}")

    return 0


def cmd_immune(args) -> int:
    """Interact with IMMUNE security system."""
    root = get_organism_root()
    immune_dir = root / "03_IMMUNE"

    sys.path.insert(0, str(immune_dir))
    from immune_system import ImmuneSystem, ActionType

    immune = ImmuneSystem()

    if args.action == "status":
        status = immune.status()
        print("IMMUNE System Status")
        print("=" * 40)
        print(f"Active policies: {status['total_policies']}")
        print(f"Audit logs: {status['total_audit_logs']}")
        print(f"Policies: {', '.join(status['policies'])}")

    elif args.action == "validate" and args.action_type:
        action_type = getattr(ActionType, args.action_type.upper(), ActionType.READ)
        result = immune.validate(
            action="cli_test",
            action_type=action_type,
            target=args.target or "test_target"
        )
        print(f"Validation Result:")
        print(f"  Approved: {result.approved}")
        print(f"  Risk Level: {result.risk_level.value}")
        print(f"  Reason: {result.reason}")

    return 0


def cmd_legal(args) -> int:
    """Interact with LEGAL engine."""
    root = get_organism_root()
    legal_dir = root / "11_LEGAL_BRAIN"

    sys.path.insert(0, str(legal_dir))
    from legal_engine import LegalEngine

    engine = LegalEngine(root)

    if args.action == "status":
        status = engine.get_status()
        print("LEGAL Engine Status")
        print("=" * 40)
        print(f"Status: {status['status']}")
        print(f"Active rules: {status['active_rules']}")
        print(f"Total checks: {status['total_checks_performed']}")
        print(f"Pass rate: {status['recent_pass_rate']:.1%}")

    elif args.action == "check" and args.content:
        results = engine.check_compliance(args.content, "cli_check")
        print(f"\nCompliance Check Results:")
        for r in results:
            status = "✓" if r.passed else "✗"
            print(f"  {status} [{r.rule_id}] {r.message}")

    return 0


def cmd_social(args) -> int:
    """Interact with SOCIAL engine."""
    root = get_organism_root()
    social_dir = root / "09_SOCIAL_ENGINE"

    sys.path.insert(0, str(social_dir))
    from social_engine import SocialEngine

    engine = SocialEngine(root)

    if args.action == "status":
        status = engine.get_status()
        print("SOCIAL Engine Status")
        print("=" * 40)
        print(f"Status: {status['status']}")
        print(f"Registered agents: {status['registered_agents']}")
        print(f"Total messages: {status['total_messages']}")
        print(f"Total connections: {status['total_connections']}")
        print(f"Knowledge shares: {status['knowledge_shares']}")

    elif args.action == "graph" and args.agent:
        graph = engine.get_social_graph(args.agent)
        print(f"\nSocial Graph for {args.agent}:")
        print(f"  Connections: {graph['connection_count']}")
        print(f"  Messages sent: {graph['messages_sent']}")
        print(f"  Messages received: {graph['messages_received']}")
        print(f"  Unread: {graph['unread_messages']}")

    return 0


def cmd_orchestrator(args) -> int:
    """Orchestrator management (00_ROOT)."""
    organism_root = get_organism_root()

    if args.action == "cycle":
        # Trigger orchestrator cycle
        sys.path.insert(0, str(organism_root))
        try:
            from AMOS_MASTER_ORCHESTRATOR import AmosMasterOrchestrator
            orch = AmosMasterOrchestrator()
            if not orch.initialize():
                print("✗ Orchestrator initialization failed")
                return 1
            results = orch.run_cycle()
            print("✓ Orchestrator cycle completed")
            print(f"  Subsystems processed: {len(results)}")
            for result in results:
                print(f"    - {result.subsystem}: {result.status}")
        except Exception as e:
            print(f"✗ Cycle failed: {e}")
            return 1

    elif args.action == "status":
        # Check orchestrator status
        sys.path.insert(0, str(organism_root))
        try:
            from AMOS_MASTER_ORCHESTRATOR import AmosMasterOrchestrator
            orch = AmosMasterOrchestrator()
            status = orch.get_status()
            print("Orchestrator Status")
            print("=" * 40)
            print(f"Cycle count: {status['cycle_count']}")
            print(f"Current position: {status['current_position']}")
            print(f"Active subsystems: {len(status['active_subsystems'])}")
            print(f"Last cycle time: {status['last_cycle_time']:.3f}s" if status['last_cycle_time'] else "N/A")
            print(f"Error count: {status['error_count']}")
        except Exception as e:
            print(f"✗ Status check failed: {e}")
            return 1

    return 0


def main(argv: Optional[List[str]] = None) -> int:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="amos",
        description="AMOS 7-System Organism CLI"
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Status command
    status_parser = subparsers.add_parser("status", help="Show organism status")
    status_parser.set_defaults(func=cmd_status)

    # Run command
    run_parser = subparsers.add_parser("run", help="Run orchestrator")
    run_parser.set_defaults(func=cmd_run)

    # Agents command
    agent_parser = subparsers.add_parser("agents", help="Manage agents")
    agent_parser.add_argument("action", choices=["list", "create"], nargs="?",
                              default="list")
    agent_parser.set_defaults(func=cmd_agents)

    # Workers command
    worker_parser = subparsers.add_parser("workers", help="Execute workers")
    worker_parser.add_argument("task", choices=["write", "analyze"])
    worker_parser.add_argument("--file", "-f", help="Target file")
    worker_parser.add_argument("--content", "-c", help="Content to write")
    worker_parser.add_argument("--topic", "-t", help="Analysis topic")
    worker_parser.set_defaults(func=cmd_workers)

    # Brain command (standalone package)
    brain_parser = subparsers.add_parser("brain", help="AMOS brain (standalone)")
    brain_parser.add_argument("action", choices=["status", "think", "engines", "dashboard", "memory"])
    brain_parser.add_argument("--question", "-q", help="Question for think")
    brain_parser.add_argument("--days", "-d", type=int, default=30, help="Dashboard days")
    brain_parser.add_argument("--subaction", choices=["history", "recall"], help="Memory subaction")
    brain_parser.add_argument("--limit", "-l", type=int, default=5, help="History limit")
    brain_parser.add_argument("--query", help="Recall query")
    brain_parser.set_defaults(func=cmd_brain)

    # Bridge command (unified execution)
    bridge_parser = subparsers.add_parser("bridge", help="Brain-Organism bridge")
    bridge_parser.add_argument("action", choices=["status", "execute"])
    bridge_parser.add_argument("--task", "-t", help="Task to execute")
    bridge_parser.add_argument("--context", "-c", help="JSON context")
    bridge_parser.set_defaults(func=cmd_bridge)

    # Blood command
    blood_parser = subparsers.add_parser(
        "blood", help="Financial engine (BLOOD)"
    )
    blood_parser.add_argument(
        "action", choices=["status", "budget"], nargs="?",
        default="status"
    )
    blood_parser.add_argument(
        "--category", "-c", help="Budget category"
    )
    blood_parser.add_argument(
        "--amount", "-a", type=float, help="Budget amount"
    )
    blood_parser.add_argument(
        "--period", "-p", default="monthly",
        help="Budget period"
    )
    blood_parser.set_defaults(func=cmd_blood)

    # Social command
    social_parser = subparsers.add_parser(
        "social", help="Agent communication (SOCIAL)"
    )
    social_parser.add_argument(
        "action", choices=["status", "graph"], nargs="?",
        default="status"
    )
    social_parser.add_argument(
        "--agent", "-a", help="Agent ID for graph view"
    )
    social_parser.set_defaults(func=cmd_social)

    # Legal command
    legal_parser = subparsers.add_parser(
        "legal", help="Legal compliance (LEGAL)"
    )
    legal_parser.add_argument(
        "action", choices=["status", "check"], nargs="?",
        default="status"
    )
    legal_parser.add_argument(
        "--content", "-c", help="Content to check"
    )
    legal_parser.set_defaults(func=cmd_legal)

    # Immune command
    immune_parser = subparsers.add_parser(
        "immune", help="Security system (IMMUNE)"
    )
    immune_parser.add_argument(
        "action", choices=["status", "validate"], nargs="?",
        default="status"
    )
    immune_parser.add_argument(
        "--action-type", "-t", help="Action type to validate"
    )
    immune_parser.add_argument(
        "--target", "-g", help="Target for validation"
    )
    immune_parser.set_defaults(func=cmd_immune)

    # Life command
    life_parser = subparsers.add_parser(
        "life", help="Personal life management (LIFE)"
    )
    life_parser.add_argument(
        "action", choices=["status", "schedule"], nargs="?",
        default="status"
    )
    life_parser.set_defaults(func=cmd_life)

    # Factory command
    factory_parser = subparsers.add_parser(
        "factory", help="Agent factory (FACTORY)"
    )
    factory_parser.add_argument(
        "action", choices=["status", "create"], nargs="?",
        default="status"
    )
    factory_parser.set_defaults(func=cmd_factory)

    # Task command
    task_parser = subparsers.add_parser(
        "task", help="Task queue (METABOLISM)"
    )
    task_parser.add_argument(
        "action", choices=["status", "submit", "list"], nargs="?",
        default="status"
    )
    task_parser.add_argument(
        "--title", "-t", help="Task title"
    )
    task_parser.add_argument(
        "--description", "-d", help="Task description"
    )
    task_parser.add_argument(
        "--type", choices=["analysis", "code", "documentation", "security"],
        default="analysis", help="Task type"
    )
    task_parser.add_argument(
        "--priority", "-p", choices=["low", "medium", "high", "critical"],
        default="medium", help="Task priority"
    )
    task_parser.set_defaults(func=cmd_task)

    # Execute command
    execute_parser = subparsers.add_parser(
        "execute", help="Execute pending tasks (MUSCLE)"
    )
    execute_parser.add_argument(
        "--count", "-c", type=int, default=5,
        help="Maximum tasks to execute"
    )
    execute_parser.set_defaults(func=cmd_execute)

    # Predict command
    predict_parser = subparsers.add_parser(
        "predict", help="Predictive analytics (QUANTUM_LAYER)"
    )
    predict_parser.add_argument(
        "target", choices=["all", "queue", "resources"], nargs="?",
        default="all", help="What to predict"
    )
    predict_parser.set_defaults(func=cmd_predict)

    # Workflow command
    workflow_parser = subparsers.add_parser(
        "workflow", help="Workflow management (MUSCLE)"
    )
    workflow_parser.add_argument(
        "action", choices=["list", "create", "run", "status"], nargs="?",
        default="list", help="Workflow action"
    )
    workflow_parser.add_argument(
        "--name", "-n", help="Workflow name"
    )
    workflow_parser.add_argument(
        "--workflow-id", "-w", help="Workflow ID for run/status"
    )
    workflow_parser.set_defaults(func=cmd_workflow)

    # Pipeline command
    pipeline_parser = subparsers.add_parser(
        "pipeline", help="Pipeline management (METABOLISM)"
    )
    pipeline_parser.add_argument(
        "action", choices=["list", "create", "run", "status"], nargs="?",
        default="list", help="Pipeline action"
    )
    pipeline_parser.add_argument(
        "--name", "-n", help="Pipeline name"
    )
    pipeline_parser.add_argument(
        "--pipeline-id", "-p", help="Pipeline ID for run/status"
    )
    pipeline_parser.set_defaults(func=cmd_pipeline)

    # Alert command
    alert_parser = subparsers.add_parser(
        "alert", help="Alert management (IMMUNE)"
    )
    alert_parser.add_argument(
        "action", choices=["status", "list", "test"], nargs="?",
        default="status", help="Alert action"
    )
    alert_parser.add_argument(
        "--metric", "-m", help="Metric to test (for test action)"
    )
    alert_parser.add_argument(
        "--value", "-v", type=float, default=85.0, help="Metric value"
    )
    alert_parser.set_defaults(func=cmd_alert)

    # Orchestrator command
    orchestrator_parser = subparsers.add_parser(
        "orchestrator", help="Orchestrator control (00_ROOT)"
    )
    orchestrator_parser.add_argument(
        "action", choices=["cycle", "status"], nargs="?",
        default="status", help="Orchestrator action"
    )
    orchestrator_parser.set_defaults(func=cmd_orchestrator)

    # Cognitive engine command
    cognitive_parser = subparsers.add_parser(
        "cognitive", help="Cognitive engine management (01_BRAIN)"
    )
    cognitive_parser.add_argument(
        "action", choices=["list", "status", "query"], nargs="?",
        default="status", help="Cognitive engine action"
    )
    cognitive_parser.add_argument(
        "--domain", "-d", help="Domain to query (for query action)"
    )
    cognitive_parser.add_argument(
        "--engine", "-e", help="Specific engine name"
    )
    cognitive_parser.set_defaults(func=cmd_cognitive)

    # API server command
    api_parser = subparsers.add_parser(
        "api", help="API server management (14_INTERFACES)"
    )
    api_parser.add_argument(
        "action", choices=["start", "stop", "status"], nargs="?",
        default="status", help="API server action"
    )
    api_parser.add_argument(
        "--port", "-p", type=int, default=5000, help="Server port"
    )
    api_parser.add_argument(
        "--host", default="127.0.0.1", help="Server host"
    )
    api_parser.add_argument(
        "--debug", action="store_true", help="Enable debug mode"
    )
    api_parser.set_defaults(func=cmd_api)

    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        return 0

    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
