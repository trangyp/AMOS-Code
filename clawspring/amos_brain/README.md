# AMOS Brain Cognitive Integration

Complete AMOS cognitive architecture integration for ClawSpring.

## Overview

This module provides a production-ready cognitive routing system that analyzes tasks, selects appropriate cognitive engines, executes with global law enforcement, and continuously improves through feedback loops.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    AMOS COGNITIVE PIPELINE                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│   Task Input → Router → Executor → Orchestrator → Output          │
│                  ↓         ↓           ↓                            │
│              Feedback   Laws      Consensus                       │
│                  ↓         ↓           ↓                          │
│              Audit Trail (persistent .jsonl)                      │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

## Components

### 1. Cognitive Router (`amos_cognitive_router.py`)
- Domain detection (software, design, security, analysis, ubi, organism)
- Risk assessment (LOW/MEDIUM/HIGH/CRITICAL)
- Engine suggestion with feedback enhancement
- Global law application (Rule of 2, Rule of 4, Structural Integrity)

### 2. Engine Executor (`engine_executor.py`)
6 cognitive engines:
- `AMOS_Deterministic_Logic_And_Law_Engine` - Formal logic analysis
- `AMOS_Engineering_And_Mathematics_Engine` - Technical feasibility
- `AMOS_Design_Language_Engine` - Structural clarity
- `AMOS_Biology_And_Cognition_Engine` - UBI alignment
- `AMOS_Strategy_Game_Engine` - Long-term trajectories
- `AMOS_Society_Culture_Engine` - Stakeholder impact

### 3. Multi-Agent Orchestrator (`multi_agent_orchestrator.py`)
- Parallel engine execution (ThreadPoolExecutor)
- Consensus synthesis with agreement scoring
- Dissent detection and reporting
- Law enforcement across all perspectives

### 4. Cognitive Audit (`cognitive_audit.py`)
- Persistent audit trail (`.amos_cognitive_audit.jsonl`)
- Query by domain, recent, violations
- Statistics and reporting
- Similar task lookup

### 5. Feedback Loop (`feedback_loop.py`)
- Pattern analysis from audit history
- Domain-specific engine recommendations
- Consensus quality estimation
- Task advice based on historical data

### 6. Audit Exporter (`audit_exporter.py`)
- JSON export (full structured data)
- CSV export (spreadsheet analysis)
- Markdown report (human-readable)
- Domain-filtered exports

### 7. Brain Loader (`loader.py`)
- JSON brain spec loading
- Kernel configuration extraction
- Global laws parsing

### 8. Laws (`laws.py`)
- Rule of 2 enforcement (dual perspectives)
- Rule of 4 enforcement (quadrant thinking)
- Structural integrity checks
- UBI alignment validation

### 9. Prompt Builder (`prompt_builder.py`)
- AMOS context injection
- System prompt enhancement
- Cognitive routing information

### 10. Visual Dashboard (`dashboard.html` + `dashboard_server.py`)
- Real-time web-based visualization
- Live statistics and metrics
- Decision history with filtering
- Domain insights display
- Auto-refresh every 30 seconds

### 11. System Status (`system_status.py`)
- Complete ecosystem health check
- Module verification
- Import validation
- Runtime status reporting

## REPL Commands

```bash
/amos                    # Show status and toggle help
/amos on                 # Enable cognitive mode
/amos off                # Disable cognitive mode
/amos status             # Full system health check
/amos audit              # View decision analytics
/amos export             # Export audit as JSON
/amos export csv         # Export audit as CSV
/amos export markdown    # Export audit as Markdown
/amos dashboard          # Launch web dashboard
/brainstorm [topic]      # AMOS-powered multi-agent session
```

## API Usage

```python
from amos_brain import (
    get_router,
    execute_cognitive_task,
    run_cognitive_consensus,
    record_cognitive_decision,
    export_audit
)

# Simple routing
router = get_router()
analysis = router.analyze("Design a secure API")
prompt = router.build_cognitive_prompt("Design a secure API", execute=True)

# Direct execution
result = execute_cognitive_task("Task description", ["AMOS_Strategy_Game_Engine"])

# Multi-agent consensus
consensus = run_cognitive_consensus("Complex task", [
    "AMOS_Deterministic_Logic_And_Law_Engine",
    "AMOS_Strategy_Game_Engine",
    "AMOS_Design_Language_Engine"
])

# Record decision
record_cognitive_decision(
    task="Task description",
    domain="security",
    risk_level="high",
    engines=["AMOS_Strategy_Game_Engine"],
    consensus_score=0.85,
    laws=["RULE_OF_2"],
    violations=[],
    exec_time_ms=12.5,
    recommendation="Proceed with caution"
)

# Export data
path = export_audit(format="json")  # or "csv", "markdown"
```

## Configuration

The cognitive system is automatically enabled when the AMOS brain JSON specs are available. No additional configuration required.

## Files Generated

- `.amos_cognitive_audit.jsonl` - Persistent audit trail (auto-created)
- `amos_audit_export_*.json` - JSON exports
- `amos_audit_export_*.csv` - CSV exports
- `amos_audit_report_*.md` - Markdown reports

## Statistics Available

```python
from amos_brain.cognitive_audit import get_audit_trail

audit = get_audit_trail()
stats = audit.get_statistics()
# {
#     "total_entries": 42,
#     "violation_rate": 0.02,
#     "avg_execution_time_ms": 15.3,
#     "domains": {"security": 15, "software": 20, ...}
# }
```

## Self-Improvement

The system automatically improves routing decisions over time:

1. Every decision is recorded to audit trail
2. Feedback loop analyzes historical patterns
3. Domain-specific engine preferences are learned
4. Future routing incorporates learned insights

## Status

✅ **Production Ready**
- 9 core modules operational
- Full REPL integration
- Persistent audit logging
- Self-improving feedback loop
- Data export capabilities
- Multi-agent orchestration
- Global law enforcement

## Integration Complete

The AMOS cognitive architecture is fully integrated with ClawSpring and ready for production use.
