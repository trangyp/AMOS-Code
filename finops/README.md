# FinOps - Cost Management

Cloud cost optimization and monitoring for AMOS Equation System.

## Quick Start

```bash
# View current costs
python finops/cost_monitor.py --report monthly

# Check for optimization opportunities
python finops/cost_monitor.py --optimize

# Deploy budget alerts
terraform -chdir=finops/terraform apply
```

## Cost Allocation Tags

All resources must be tagged for accurate cost tracking:

| Tag | Purpose | Example |
|-----|---------|---------|
| Project | Overall project | `AMOS` |
| Environment | Deployment environment | `production` |
| Service | Component name | `api`, `worker`, `database` |
| Team | Owning team | `platform`, `backend` |

## Budgets

### Monthly Budget
- **Limit**: $1000 USD (adjust in variables.tf)
- **Alert at**: 80%
- **Forecast alert**: 100%

### Daily Budget
- **Limit**: $100 USD
- **Alert at**: 100%

## Anomaly Detection

Automatic detection of unusual spending:
- Threshold: $100 per anomaly
- Frequency: Immediate alerts
- Monitored by: Service dimension

## Cost Optimization

### Automated Actions
The cost optimizer Lambda runs daily at 9 AM UTC:

1. **Idle EC2 Detection**: Stop instances with <5% CPU for 7 days
2. **Over-provisioned ECS**: Scale down services with excess capacity
3. **Unused Resources**: Identify and flag for review

### Manual Optimization
```bash
# Generate full report with recommendations
python finops/cost_monitor.py --report monthly --optimize
```

## CI/CD Integration

```yaml
# .github/workflows/finops.yml
- name: Cost Check
  run: |
    python finops/cost_monitor.py --alert-threshold 150
```

## Cost Dashboard

Access AWS Cost Explorer:
1. Filter by tags: `Project:AMOS`
2. Group by: Service
3. Time range: Last 30 days

## Alerts

| Alert Type | Threshold | Channel |
|------------|-----------|---------|
| Budget 80% | 80% of monthly | Email + SNS |
| Forecast 100% | 100% forecasted | Email + SNS |
| Daily exceeded | Daily limit | Email + SNS |
| Anomaly detected | $100+ | Email + SNS |

## Responsibilities

- **Engineering**: Tag all resources, review weekly reports
- **Finance**: Set budgets, review monthly spend
- **SRE**: Respond to alerts, implement optimizations

---

*Part of AMOS operational excellence practices*
