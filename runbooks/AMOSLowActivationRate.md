# Runbook: AMOS Low Activation Rate

## Alert: AMOSLowActivationRate

**Severity:** Critical  
**Trigger:** `amos_activation_rate < 0.5` for 5 minutes  
**Service:** amos-orchestrator

---

## Summary

The AMOS orchestrator has activated less than 50% of discovered modules. This indicates a serious problem with the system initialization or module dependencies.

---

## Initial Assessment (2 minutes)

1. **Check orchestrator status:**
   ```bash
   curl http://localhost:8000/status
   ```

2. **Check module list:**
   ```bash
   python amos_cli_orchestrator.py modules --tier CRITICAL
   ```

3. **View recent logs:**
   ```bash
   docker logs amos-prod-orchestrator --tail 100
   ```

---

## Common Causes

### 1. Dependency Resolution Failure
- **Symptoms:** Many modules show `activated: false`
- **Diagnosis:** Check dependency graph health
  ```bash
  curl http://localhost:8000/modules | grep -c "activated: false"
  ```
- **Resolution:** 
  1. Re-run initialization: `python amos_cli_orchestrator.py init`
  2. Check for circular dependencies in logs
  3. Verify critical modules are loading first

### 2. Memory Bridge Connection Issues
- **Symptoms:** Memory bridges showing as inactive
- **Diagnosis:**
  ```bash
  curl http://localhost:8000/bridges
  ```
- **Resolution:**
  1. Check Redis connection: `docker exec amos-redis redis-cli ping`
  2. Restart orchestrator: `docker restart amos-prod-orchestrator`

### 3. Critical Module Failure
- **Symptoms:** One or more CRITICAL tier modules failed
- **Diagnosis:**
  ```bash
  python amos_cli_orchestrator.py modules --tier CRITICAL
  ```
- **Resolution:**
  1. Identify failed critical module
  2. Check module-specific logs
  3. Fix root cause and restart

### 4. Resource Exhaustion
- **Symptoms:** High CPU/memory usage during initialization
- **Diagnosis:**
  ```bash
  docker stats amos-prod-orchestrator
  ```
- **Resolution:**
  1. Increase container resources in docker-compose.yml
  2. Restart with higher limits: `docker-compose up -d --force-recreate`

---

## Escalation Path

1. **If activation rate < 20%:** Page on-call engineer immediately
2. **If activation rate 20-50%:** Create incident ticket, monitor for 15 minutes
3. **If activation rate improving:** Monitor and document in incident log

---

## Verification

After applying fix, verify resolution:

```bash
# Check activation rate
curl -s http://localhost:8000/status | grep activation_rate

# Verify all critical modules
python amos_cli_orchestrator.py validate

# Check Grafana dashboard
open http://localhost:3000/d/amos-orchestrator
```

**Resolution Criteria:**
- Activation rate > 80%
- All CRITICAL modules activated
- No new errors in logs for 5 minutes

---

## Prevention

- Enable proactive monitoring of module activation during deployments
- Set up canary deployments to catch activation issues early
- Regular dependency graph audits to identify circular dependencies
- Pre-production testing with full module activation

---

## Related Alerts

- `AMOSCriticalModulesFailing` - Subset of this alert for critical tier only
- `AMOSModuleActivationFailed` - Individual module failures
- `AMOSNotInitialized` - Complete initialization failure
