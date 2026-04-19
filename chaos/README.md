# Chaos Engineering

Resilience testing for the AMOS Equation System.

## Principles

- **Steady State**: System must be healthy before testing
- **Hypothesis**: Define expected behavior under failure
- **Real World**: Test production-like scenarios
- **Minimize Blast Radius**: Contain experiment impact
- **Automate**: Run tests in CI/CD pipeline

## Quick Start

```bash
# Run full chaos suite
python chaos/experiments.py --suite

# Single experiment
python chaos/experiments.py --experiment cpu_stress --duration 300

# Pod failure test
python chaos/experiments.py --experiment pod_failure --target api
```

## Experiments

| Experiment | Failure Mode | Validates |
|------------|-------------|-----------|
| CPU Stress | Resource exhaustion | Auto-scaling, circuit breakers |
| Pod Failure | Container crash | Kubernetes rescheduling, health checks |
| DB Slowdown | Latency injection | Connection pooling, timeouts |
| Cache Failure | Redis unavailable | Graceful degradation |
| Network Latency | Slow connections | Retry logic, async handling |

## Safety Controls

- Automatic rollback on critical failures
- Namespace isolation for experiments
- Max blast radius: single pod/component
- Always validate steady state first

## CI Integration

```yaml
# .github/workflows/chaos.yml
- name: Chaos Tests
  run: |
    python chaos/experiments.py --suite
  timeout-minutes: 30
```

## Game Days

Monthly exercises with full team:
1. Pick scenario from runbooks
2. Inject failure during business hours
3. Measure MTTR (Mean Time To Recovery)
4. Document learnings

---

*Part of AMOS SRE practices*
