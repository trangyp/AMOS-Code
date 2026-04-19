# AMOS Unified Observability Platform - Phase 27

## Overview

Phase 27 implements a comprehensive unified observability platform for the 26-Phase AMOS Architecture. It integrates metrics, logs, and traces from all phases with real-time WebSocket streaming and alerting.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                    AMOS Unified Observability                         │
├─────────────────────────────────────────────────────────────────────┤
│ Telemetry Sources (26 Phases)                                       │
│ ├── Phase 24-26: Event Streaming, Testing, Deployment               │
│ ├── Phase 20-23: AI/ML, Gateway, Security, Service Mesh             │
│ ├── Phase 16-19: Database, Tenancy, Async, Caching                  │
│ ├── Phase 10-15: K8s, Monitoring, CI/CD, Containers                │
│ └── Phase 00-09: Core System, Runtime, Security                     │
│                                                                     │
│ Components                                                          │
│ ├── AMOSTelemetryCollector: Aggregates metrics, logs, traces      │
│ ├── AMOSAlertManager: Evaluates alert rules and notifications     │
│ ├── AMOSDashboard: WebSocket streaming and real-time updates        │
│ └── AMOSObservabilityPlatform: Main orchestrator                  │
└─────────────────────────────────────────────────────────────────────┘
```

## Features

- **26-Phase Telemetry**: Collect metrics from all architectural phases
- **Real-time Streaming**: WebSocket-based live dashboard updates
- **Alert Management**: Configurable alerts with severity levels
- **Metrics Storage**: Time-series data with phase/component filtering
- **OpenTelemetry Ready**: Compatible with OTel standards

## Usage

### Basic Usage
```python
from amos_unified_observability_platform import get_observability_platform

platform = get_observability_platform()
await platform.start()

# Collect metrics from any phase
await platform.collector.collect_metric(
    phase=16, component="database", metric="latency_ms", value=50.0
)
```

### Creating Alerts
```python
from amos_unified_observability_platform import AlertSeverity

platform.alert_manager.create_alert(
    name="High Latency",
    severity=AlertSeverity.WARNING,
    query="16:database:latency_ms",
    threshold=100.0
)
```

### Running Demo
```bash
python amos_unified_observability_platform.py
```

## Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `OTEL_ENDPOINT` | OpenTelemetry collector endpoint | http://localhost:4317 |
| `REDIS_URL` | Redis connection for persistence | redis://localhost:6379/0 |
| `ALERT_INTERVAL` | Alert evaluation interval (seconds) | 60 |

## Phase 27 Complete

Status: Unified Observability Platform operational
- 26-phase telemetry collection
- Real-time WebSocket streaming
- Alert management system
- Demo included

**27 Phases Complete**
