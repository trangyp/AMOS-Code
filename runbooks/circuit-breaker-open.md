# Runbook: Circuit Breaker Open

**Alert**: `CircuitBreakerOpen` / `CircuitBreakerHalfOpen`  
**Severity**: Critical / Warning  
**Condition**: Circuit breaker in OPEN or HALF_OPEN state  
**Runbook Owner**: SRE Team  
**Last Updated**: 2024-01-15

## Summary

The circuit breaker has opened for a downstream service, indicating repeated failures. This protects the system from cascading failures but may degrade functionality.

## Immediate Assessment (First 2 minutes)

### 1. Identify Affected Circuit Breaker
```bash
# Check circuit breaker states
curl http://localhost:8000/metrics | grep circuit_breaker_state

# Check which service is failing
curl http://localhost:8000/metrics | grep circuit_breaker_failures_total
```

### 2. Check Downstream Service Health
```bash
# Identify the failing service from metrics labels
curl http://localhost:8000/metrics | grep circuit_breaker | grep name="..."

# Check if downstream service is reachable
kubectl get pods -l app=<downstream-service>
kubectl logs -l app=<downstream-service> --tail=50
```

## Circuit Breaker States

| State | Value | Meaning | Action |
|-------|-------|---------|--------|
| CLOSED | 0 | Normal operation | None needed |
| HALF_OPEN | 1 | Testing recovery | Monitor closely |
| OPEN | 2 | Failing fast | Investigate downstream |

## Common Causes & Solutions

### Cause 1: Downstream Service Unavailable (50% of cases)

**Symptoms**:
- Circuit breaker opens immediately
- Downstream pods not ready
- Network timeouts

**Diagnosis**:
```bash
# Check downstream service pods
kubectl get pods -l app=<service> -o wide

# Check pod logs
kubectl logs -l app=<service> --tail=100 | grep -E "(ERROR|Exception)"

# Check service endpoints
kubectl get endpoints <service>
```

**Immediate Mitigation**:
```bash
# Restart downstream service if needed
kubectl rollout restart deployment/<service>

# Or scale up if resource constraint
kubectl scale deployment/<service> --replicas=5
```

### Cause 2: Network Connectivity Issues (25% of cases)

**Symptoms**:
- Intermittent timeouts
- DNS resolution failures
- Connection refused errors

**Diagnosis**:
```bash
# Test connectivity from API pod
kubectl exec -it <api-pod> -- \
  curl -v http://<downstream-service>:8080/health

# Check DNS resolution
kubectl exec -it <api-pod> -- \
  nslookup <downstream-service>.default.svc.cluster.local
```

**Resolution**:
- Check CNI/network policies
- Verify service mesh configuration if applicable
- Restart CoreDNS if DNS issues

### Cause 3: Timeout Mismatch (15% of cases)

**Symptoms**:
- Circuit opens before downstream responds
- Slow but eventually successful calls

**Diagnosis**:
```bash
# Check current timeout settings
kubectl get configmap amos-config -o yaml | grep -i timeout

# Check downstream response times
curl http://localhost:8000/metrics | grep http_client_request_duration
```

**Resolution**:
```bash
# Temporarily increase timeout (if appropriate)
kubectl patch configmap amos-config --type merge \
  -p '{"data":{"SERVICE_TIMEOUT":"30s"}}'
kubectl rollout restart deployment/amos-equation-api
```

### Cause 4: Authentication/Authorization Issues (10% of cases)

**Symptoms**:
- 401/403 errors
- TLS/SSL errors
- Token expiry

**Diagnosis**:
```bash
# Check auth-related logs
kubectl logs -l app=amos-equation-api --tail=200 | grep -i auth

# Verify service account tokens
kubectl get serviceaccount <service-account>
```

## Immediate Mitigation Options

### Option 1: Manual Circuit Reset (Use with Caution)

If downstream service is confirmed healthy:

```bash
# Restart API pods to reset circuit breaker state
kubectl rollout restart deployment/amos-equation-api

# Wait for pods to be ready
kubectl rollout status deployment/amos-equation-api
```

### Option 2: Enable Fallback Mode

If your application supports graceful degradation:

```bash
# Enable fallback mode via feature flag
curl -X POST http://localhost:8000/admin/feature-flags \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -d '{"flag": "downstream_fallback", "enabled": true}'
```

### Option 3: Bypass Circuit (Emergency Only)

```bash
# Temporarily disable circuit breaker (NOT RECOMMENDED for production)
kubectl patch configmap amos-config --type merge \
  -p '{"data":{"CIRCUIT_BREAKER_ENABLED":"false"}}'
kubectl rollout restart deployment/amos-equation-api
```

**Warning**: Only use this for debugging, never in production load.

## Monitoring Recovery

```bash
# Watch circuit breaker state
echo "Monitoring circuit breaker state..."
while true; do
  kubectl exec -it <api-pod> -- \
    curl -s http://localhost:8000/metrics | \
    grep circuit_breaker_state | grep <service-name>
  sleep 10
done

# Expected transition: OPEN -> HALF_OPEN -> CLOSED
```

## Prevention

### 1. Proper Timeout Configuration
- Ensure client timeout > server processing time
- Add buffer for network latency
- Consider using adaptive timeouts

### 2. Resource Sizing
- Ensure downstream services have adequate resources
- Monitor resource utilization trends
- Set up capacity alerts

### 3. Health Check Alignment
- Align Kubernetes health checks with circuit breaker thresholds
- Use readiness probes to remove unhealthy pods from service

## Circuit Breaker Configuration

```python
# Recommended settings from equation_circuit_breaker.py
CircuitBreakerConfig(
    failure_threshold=5,        # Open after 5 failures
    recovery_timeout=30,        # Try again after 30s
    half_open_max_calls=3,      # Test with 3 calls in half-open
    success_threshold=2,          # Close after 2 successes
    expected_exception=Exception
)
```

## Escalation Criteria

- [ ] Circuit breaker remains open after 3 reset attempts
- [ ] Multiple downstream services affected simultaneously
- [ ] Data consistency issues suspected
- [ ] No clear cause identified after 20 minutes

## Post-Resolution

1. **Verify circuit closed for 10 minutes**
2. **Monitor for 1 hour** for stability
3. **Document root cause** in incident report
4. **Review timeout configurations** if needed
5. **Update monitoring** to detect earlier

## Related Runbooks

- [API High Error Rate](api-high-error-rate.md)
- [API High Latency](api-high-latency.md)
- [Database Slow Queries](database-slow-queries.md)

## Contacts

- **SRE On-Call**: #sre-oncall
- **Platform Team**: #platform-team
- **Service Owner**: Check service catalog for owner
