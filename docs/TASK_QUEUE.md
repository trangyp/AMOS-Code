# AMOS SuperBrain Task Queue v2.0.0

## Overview

Distributed task queue with background workers for all 12 systems. Supports scheduled tasks, job retries with exponential backoff, and SuperBrain governance.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    TASK QUEUE LAYER                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐   │
│  │   Redis      │  │   Worker     │  │   Scheduled        │   │
│  │   Queue      │  │   Pool       │  │   Tasks            │   │
│  └──────────────┘  └──────────────┘  └──────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
   ┌────▼────┐           ┌────▼────┐           ┌────▼────┐
   │Priority │           │Retry    │           │Governance│
   │Queues   │           │Logic    │           │Check    │
   │(4 levels)│          │(Backoff)│           │         │
   └─────────┘           └─────────┘           └─────────┘
```

---

## Job Priorities

| Priority | Level | Use Case |
|----------|-------|----------|
| CRITICAL | 20 | Emergency tasks |
| HIGH | 10 | Urgent processing |
| MEDIUM | 5 | Standard tasks |
| LOW | 1 | Background jobs |

---

## Task Registry

### Pre-configured Tasks (12 Systems)

| System | Task | Timeout | Governance |
|--------|------|---------|------------|
| **Cognitive Router** | `analyze_task` | 300s | ✅ |
| **Cognitive Router** | `batch_process` | 600s | ✅ |
| **Resilience Engine** | `health_check` | 60s | ❌ |
| **Resilience Engine** | `circuit_reset` | 30s | ✅ |
| **Knowledge Loader** | `sync_files` | 300s | ✅ |
| **Knowledge Loader** | `index_update` | 600s | ✅ |
| **Master Orchestrator** | `process_workflow` | 300s | ✅ |
| **Master Orchestrator** | `batch_tasks` | 900s | ✅ |
| **Agent Messaging** | `broadcast` | 120s | ✅ |
| **Agent Observability** | `collect_metrics` | 60s | ❌ |
| **UBI Engine** | `batch_analysis` | 300s | ✅ |
| **AMOS Tools** | `execute_batch` | 600s | ✅ |
| **Audit Exporter** | `generate_report` | 300s | ✅ |
| **Audit Exporter** | `cleanup_old_logs` | 1800s | ❌ |
| **SuperBrain** | `governance_audit` | 300s | ✅ |

---

## Scheduled Tasks

| Task | Schedule | Priority |
|------|----------|----------|
| `health_check` | Every 5 minutes | HIGH |
| `collect_metrics` | Every minute | MEDIUM |
| `sync_files` | Every 6 hours | LOW |
| `cleanup_old_logs` | Daily at midnight | LOW |

---

## Usage

### Submitting Jobs

```python
from backend.workers.task_queue import submit_task, JobPriority

# Submit immediate job
job_id = submit_task(
    task_name="cognitive_router.analyze_task",
    payload={"task": "analyze_data", "input": "raw_text"},
    priority=JobPriority.HIGH
)

# Submit scheduled job
from datetime import datetime, timedelta

job_id = submit_task(
    task_name="knowledge_loader.sync_files",
    payload={"directory": "/data/knowledge"},
    priority=JobPriority.LOW,
    scheduled_for=datetime.utcnow() + timedelta(hours=1)
)
```

### Registering Task Handlers

```python
from backend.workers.task_queue import register_task_handler

def analyze_task_handler(payload):
    # Process task
    result = process_data(payload["input"])
    return result

register_task_handler("cognitive_router.analyze_task", analyze_task_handler)
```

### Checking Job Status

```python
from backend.workers.task_queue import get_job_status, JobStatus

status = get_job_status(job_id)
if status == JobStatus.COMPLETED:
    print("Job done!")
elif status == JobStatus.FAILED:
    print("Job failed!")
```

### Starting Workers

```python
from backend.workers.task_queue import task_queue

# Start worker pool
task_queue.start_workers()

# Stop workers
task_queue.stop_workers()
```

---

## Job Retry Logic

### Exponential Backoff

| Retry | Delay |
|-------|-------|
| 1st | 60s |
| 2nd | 120s |
| 3rd | 240s |

Formula: `delay * (2 ^ (retry_count - 1))`

Default max retries: 3

---

## Job Status Flow

```
PENDING → RUNNING → COMPLETED
    ↓
RETRYING → (backoff) → RUNNING → FAILED (after max retries)
    ↓
CANCELLED (manual)
```

---

## Statistics

```python
from backend.workers.task_queue import get_worker_stats

stats = get_worker_stats()
print(f"Total jobs: {stats.total_jobs}")
print(f"Completed: {stats.completed_jobs}")
print(f"Failed: {stats.failed_jobs}")
print(f"Queue depth: {stats.queue_depth}")
print(f"Avg processing: {stats.avg_processing_time}s")
```

---

## Integration with Other Systems

### Data Pipeline

All job events are published to the streaming pipeline:
- `job_submitted`
- `job_completed`
- `job_failed`

### SuperBrain Governance

Jobs marked with `requires_governance=True` are validated via SuperBrain ActionGate before execution.

---

**Maintainer:** Trang Phan  
**Last Updated:** 2026-04-16  
**Version:** 2.0.0
