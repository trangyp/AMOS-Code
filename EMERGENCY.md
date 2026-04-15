# AMOS Brain Emergency Constitution

This document defines emergency operating modes for the AMOS Brain and Repo Doctor Ω∞∞∞ systems.

## Emergency Levels

### Level 1: Automated Response (No Human Required)
**Duration**: Automatic  
**Trigger**: Detected invariant violations below critical threshold  
**Actions**:
- Run automated repair optimizer
- Apply safe batch repairs only
- Log all actions to audit trail
- Notify maintainers

**Law Changes**:
- `I_repair_safe`: Temporarily relaxed for auto-approved repairs
- `I_blast`: Standard blast radius checks apply
- `I_audit`: Enhanced logging active

**Restoration Conditions**:
- All violations resolved OR
- 24 hours elapsed (whichever first)
- Automatic return to normal mode

---

### Level 2: Human-Reviewed Emergency
**Duration**: Up to 72 hours  
**Trigger**: Critical invariant failures, security breach, data loss risk  
**Authorization Required**: Team lead approval  

**Actions**:
- Execute risky batch repairs (human-reviewed)
- Temporarily disable non-critical invariants
- Activate degraded mode operations
- Hourly status reports

**Law Changes**:
- `I_repair_safe`: Requires human sign-off
- `I_test`: Reduced test coverage acceptable
- `I_security`: Enhanced monitoring (cannot disable)
- `I_law_hierarchy`: Precedence rules still apply

**Bounded Duration**: 72 hours maximum  
**Audit Requirements**: All actions logged with approver identity  
**Restoration Conditions**:
- Critical issues resolved AND
- 24-hour stability period AND
- Explicit deactivation by authorized personnel

---

### Level 3: Full Incident Response
**Duration**: Until incident commander declares resolution  
**Trigger**: Catastrophic failure, security incident, data corruption  
**Authorization Required**: Incident commander (rotating role)  

**Actions**:
- Full emergency powers activated
- Direct production access for recovery
- Override normal approval workflows
- External vendor engagement authorized

**Law Changes**:
- `I_repair_safe`: Bypassed for incident recovery (logged)
- `I_test`: Post-hoc validation acceptable
- `I_security`: Cannot be overridden (monitored only)
- `I_audit`: Full forensic logging
- `I_emergency_truth`: Proof requirements temporarily reduced (explicitly declared)

**Bounded Duration**: Review every 24 hours by incident commander  
**Audit Requirements**:
- All decisions require incident commander signature
- Hourly activity logs to stakeholders
- Post-incident review mandatory within 48 hours

**Restoration Conditions**:
- Service restored to normal operation
- Forensic analysis complete
- Lessons learned documented
- Explicit constitutional restoration vote

---

## Temporary Law Changes by Regime

### Normal Operation
All invariants active with standard weights.

### Degraded Mode (Level 1)
```
Active:    I_security, I_parse, I_import, I_law_hierarchy
Relaxed:   I_test (critical only), I_docs
Monitored: I_api, I_entrypoint
```

### Incident Response (Level 2)
```
Active:    I_security, I_law_hierarchy, I_audit
Relaxed:   I_test, I_docs, I_packaging
Bypassed:  I_repair_safe (with sign-off)
Monitored: All meta-architecture invariants
```

### Catastrophic Recovery (Level 3)
```
Active:    I_security (monitoring only), I_audit (full), I_emergency_truth
Bypassed:  I_repair_safe, I_test, I_blast_radius
Emergency: I_recovery_idempotent (relaxed for recovery)
```

---

## Emergency Truth Provenance

During incident response, proof requirements may be reduced. This must be:
1. **Explicit**: Clearly declared in incident log
2. **Bounded**: Automatic return to normal after duration
3. **Attributable**: Every decision linked to incident commander
4. **Reversible**: Can be reverted without permanent damage

Example declaration:
```
[INCIDENT-2026-0415-001] Level 3 activated by: alice@example.com
Temporary reduction: I_test (post-hoc validation acceptable)
Duration: 24 hours (review at: 2026-04-16T15:00Z)
Justification: Production data corruption requires immediate rollback
```

---

## Automatic Decay and Restoration

All emergency modes have automatic decay:
- **Level 1**: Auto-decay after 24 hours
- **Level 2**: Requires renewal every 72 hours
- **Level 3**: Requires daily incident commander confirmation

Failure to renew automatically triggers:
1. Restoration to previous level
2. Alert to all stakeholders
3. Audit log entry
4. Safety shutdown if unresolved

---

## Constitutional Override Procedures

In extreme cases, constitutional rules may be overridden:

1. **Request**: Incident commander submits override request
2. **Justification**: Must cite specific harm being prevented
3. **Time-bound**: Maximum 4 hours per override
4. **Audit**: All overrides recorded in permanent log
5. **Review**: Mandatory post-hoc review within 24 hours

**Cannot Override**:
- `I_security` (security monitoring)
- `I_audit` (audit logging)
- `I_law_hierarchy` (precedence rules)

---

## Emergency Contact Information

| Role | Contact | Backup |
|------|---------|--------|
| Incident Commander | On-call rotation | See PAGERDUTY |
| Security Lead | security@example.com | security-lead@example.com |
| Architecture Team | arch@example.com | arch-lead@example.com |
| Repo Doctor Maintainer | repo-doctor@example.com | Backup maintainer |

---

## Training and Drills

- **Quarterly**: Level 1 drill (automated response)
- **Semi-annual**: Level 2 drill (human-reviewed)
- **Annual**: Level 3 tabletop exercise

All drills logged and reviewed for constitution compliance.

---

**Last Updated**: 2026-04-15  
**Version**: 1.0  
**Next Review**: 2026-07-15
