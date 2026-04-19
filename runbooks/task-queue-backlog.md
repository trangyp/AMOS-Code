# Runbook: Task Queue Backlog

**Alert**: `TaskQueueBacklog` / `CriticalTaskQueueBacklog`  
**Severity**: Warning / Critical  
**Threshold**: > 1000 / > 5000 pending tasks  
**Runbook Owner**: SRE Team  
**Last Updated**: 2024-01-15

## Summary

Tasks are accumulating in the queue faster than they can be processed, indicating either insufficient worker capacity or tasks that are stuck/failing.

## Immediate Assessment (First 2 minutes)

### 1. Check Queue Depth
```bash
# Check pending tasks count
kubectl exec -it <redis-pod> -- redis-cli llen celery

# Or via metrics
curl http://localhost:8000/metrics | grep celery_tasks_pending
```

### 2. Check Worker Status
```bash
# Check Celery worker pods
kubectl get pods -l app=amos-celery-worker

# Check worker logs
kubectl logs -l app=amos-celery-worker --tail=100
```

### 3. Check Active Tasks
```bash
# From any API pod
kubectl exec -it <api-pod> -- \
  celery -A equation_tasks inspect active --timeout=10

# Check reserved tasks
kubectl exec -it <api-pod> -- \
  celery -A equation_tasks inspect reserved --timeout=10
```

## Common Causes & Solutions

### Cause 1: Insufficient Workers (40% of cases)

**Symptoms**:
- All workers busy (100% CPU)
- Queue depth steadily increasing
- No failed tasks

**Diagnosis**:
```bash
# Check worker CPU usage
kubectl top pods -l app=amos-celery-worker

# Check worker count
kubectl get pods -l app=amos-celery-worker | wc -l

# Check task processing rate
curl http://localhost:8000/metrics | grep celery_tasks_succeeded_total
```

**Immediate Mitigation**:
```bash
# Scale workers horizontally
kubectl scale deployment/amos-celery-worker --replicas=10

# Verify new workers are processing
kubectl logs -l app=amos-celery-worker --tail=50 | grep "Task accepted"
```

### Cause 2: Long-Running/Stuck Tasks (30% of cases)

**Symptoms**:
- Workers appear busy but queue not decreasing
- Tasks with long execution times
- Tasks stuck in active state

**Diagnosis**:
```bash
# Check for long-running tasks
kubectl exec -it <api-pod> -- \
  celery -A equation_tasks inspect active --timeout=10

# Check task execution times
curl http://localhost:8000/metrics | grep celery_task_duration

# Look for specific slow tasks
kubectl logs -l app=amos-celery-worker --tail=200 | grep -E "(succeeded|failed|retry)"
```

**Immediate Mitigation**:
```bash
# Revoke stuck tasks (get task IDs from inspect active)
kubectl exec -it <api-pod> -- \
  celery -A equation_tasks control revoke <task-id> terminate

# Or revoke all tasks on a specific worker
kubectl exec -it <api-pod> -- \
  celery -A equation_tasks control revoke_all
```

**Resolution**:
- Implement task timeouts in code
- Break large tasks into smaller chunks
- Add progress tracking for long tasks

### Cause 3: Task Failures/Retries (20% of cases)

**Symptoms**:
- High failure rate
- Tasks repeatedly retrying
- Error logs show exceptions

**Diagnosis**:
```bash
# Check failure rate
curl http://localhost:8000/metrics | grep celery_tasks_failed_total

# Check recent failures
kubectl logs -l app=amos-celery-worker --tail=500 | grep -E "(ERROR|Traceback)" | tail -20

# Check specific task failures
kubectl exec -it <api-pod> -- \
  celery -A equation_tasks inspect failed --timeout=10
```

**Immediate Mitigation**:
```bash
# Disable problematic task type (if identified)
# Requires code change and redeploy

# Or purge failed tasks if they're blocking
kubectl exec -it <redis-pod> -- \
  redis-cli --raw lrange celery 0 -1 | \
  jq -r 'select(.headers.task == "problematic.task") | .headers.id' | \
  xargs -I {} celery -A equation_tasks control revoke {}
```

### Cause 4: Redis/Memory Issues (10% of cases)

**Symptoms**:
- Redis memory high
- Slow queue operations
- Connection errors

**Diagnosis**:
```bash
# Check Redis memory
kubectl exec -it <redis-pod> -- redis-cli info memory | grep used_memory

# Check Redis slow log
kubectl exec -it <redis-pod> -- redis-cli slowlog get 10

# Check queue length
kubectl exec -it <redis-pod> -- redis-cli llen celery
```

**Resolution**:
```bash
# Scale Redis if needed
kubectl patch statefulset redis --patch '{"spec":{"replicas":3}}'

# Or clear old completed task results
kubectl exec -it <redis-pod> -- \
  redis-cli --eval "
    local cursor = '0'
    repeat
      local result = redis.call('scan', cursor, 'MATCH', 'celery-task-meta-*')
      cursor = result[1]
      for _,key in ipairs(result[2]) do
        redis.call('del', key)
      end
    until cursor == '0'
  "
```

## Queue Management Commands

### Inspect Queue
```bash
# List all queues
kubectl exec -it <api-pod> -- \
  celery -A equation_tasks inspect active_queues

# Queue statistics
kubectl exec -it <redis-pod> -- redis-cli llen celery
kubectl exec -it <redis-pod> -- redis-cli llen celery:priority
```

### Purge Queue (Emergency)
```bash
# WARNING: This deletes all pending tasks
kubectl exec -it <api-pod> -- \
  celery -A equation_tasks purge -f

# Or clear Redis queue directly
kubectl exec -it <redis-pod> -- redis-cli del celery
```

**Only use if tasks are non-critical and can be lost!**

### Reprioritize Tasks
```bash
# Move tasks between queues (custom implementation needed)
# See equation_tasks.py for priority queue configuration
```

## Scaling Strategy

### Horizontal Scaling
```bash
# Gradual scaling based on queue depth
QUEUE_DEPTH=$(kubectl exec -it <redis-pod> -- redis-cli llen celery)

if [ $QUEUE_DEPTH -gt 5000 ]; then
  kubectl scale deployment/amos-celery-worker --replicas=20
elif [ $QUEUE_DEPTH -gt 2000 ]; then
  kubectl scale deployment/amos-celery-worker --replicas=10
else
  kubectl scale deployment/amos-celery-worker --replicas=5
fi
```

### Autoscaling (if configured)
```yaml
# Example HPA configuration for Celery workers
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: celery-worker-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: amos-celery-worker
  minReplicas: 3
  maxReplicas: 50
  metrics:
  - type: External
    external:
      metric:
        name: celery_queue_length
      target:
        type: AverageValue
        averageValue: "100"
```

## Prevention

### 1. Worker Sizing
- Maintain baseline workers for normal load
- Enable autoscaling for burst traffic
- Set max tasks per child to prevent memory leaks

### 2. Task Design
```python
# equation_tasks.py - Best practices
@celery_app.task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    time_limit=300,  # 5 minute hard limit
    soft_time_limit=240  # 4 minute soft limit
)
def process_equation(self, equation_id: int):
    try:
        # Task implementation
        pass
    except SoftTimeLimitExceeded:
        # Save progress and retry
        self.retry(countdown=60)
```

### 3. Monitoring
- Set up queue depth alerts at multiple thresholds
- Monitor task execution time trends
- Alert on high failure rates

## Escalation Criteria

- [ ] Queue depth > 10000
- [ ] Workers unable to process any tasks
- [ ] Suspected data corruption in queue
- [ ] Task loss detected
- [ ] Incident duration > 30 minutes

## Post-Resolution

1. **Monitor queue until back to normal** (< 100 pending)
2. **Scale workers back to baseline** after recovery
3. **Analyze failed tasks** for patterns
4. **Review task design** if timeouts recurring
5. **Document lessons learned** in post-mortem

## Related Runbooks

- [High Task Failure Rate](high-task-failure-rate.md)
- [Redis Slow Operations](redis-slow-operations.md)
- [High CPU Usage](high-cpu-usage.md)

## Contacts

- **SRE On-Call**: #sre-oncall
- **Backend Team**: #backend-team
- **Data Team**: #data-team (for data processing issues)
