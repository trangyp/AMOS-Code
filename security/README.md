# Security & Compliance

Security scanning and compliance validation for AMOS Equation System.

## Quick Start

```bash
# Run all security scans
python security/scanner.py --all

# Specific scan types
python security/scanner.py --sast
python security/scanner.py --secrets
python security/scanner.py --dependencies
python security/scanner.py --containers

# Compliance checks
python security/compliance.py --framework cis
python security/compliance.py --framework soc2
python security/compliance.py --all
```

## Security Scanner

### Scan Types

| Type | What it finds | Severity |
|------|---------------|----------|
| **Secrets** | Hardcoded API keys, passwords, tokens | Critical |
| **SAST** | Insecure code patterns (eval, shell=True) | High/Medium |
| **Dependencies** | Known CVEs in packages | High |
| **Containers** | Dockerfile security issues | Medium |

### CI/CD Integration

```yaml
# .github/workflows/security.yml
- name: Security Scan
  run: |
    python security/scanner.py --all --fail-on high
  continue-on-error: false
```

### Pre-commit Hook

```bash
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: security-scan
        name: Security Scan
        entry: python security/scanner.py --secrets --sast
        language: system
        pass_filenames: false
```

## Compliance Frameworks

### CIS AWS Foundations Benchmark

AWS security best practices:
- IAM password policies
- MFA enforcement
- CloudTrail logging
- Encryption at rest

### SOC 2

Trust Services Criteria:
- Access controls (RBAC)
- System monitoring
- Backup procedures
- Encryption

### GDPR

Data protection compliance:
- Encryption requirements
- Audit trails
- Data access logging

## Security Runbook

### Critical Finding Response

1. **Immediate** (0-30 min):
   - Assess impact
   - Contain if active exploit
   - Page security on-call

2. **Short-term** (30 min - 4 hours):
   - Rotate exposed credentials
   - Review access logs
   - Patch vulnerable code

3. **Long-term** (1-7 days):
   - Root cause analysis
   - Implement preventive controls
   - Update security training

### Vulnerability Disclosure

Contact: security@amos-project.io

Response times:
- Critical: 24 hours
- High: 72 hours
- Medium: 7 days
- Low: 30 days

## Security Architecture

```
┌─────────────────────────────────────────┐
│           Security Layers               │
├─────────────────────────────────────────┤
│ 1. Application: JWT/OAuth2, RBAC       │
│ 2. Network: Security groups, TLS       │
│ 3. Infrastructure: Encrypted storage   │
│ 4. CI/CD: Automated scanning           │
│ 5. Monitoring: Audit logs, alerts      │
└─────────────────────────────────────────┘
```

## Secrets Management

Required approach:
1. **Development**: `.env` files (never commit)
2. **Staging**: AWS Systems Manager Parameter Store
3. **Production**: AWS Secrets Manager with rotation

## Compliance Score Targets

| Framework | Target | Current |
|-----------|--------|---------|
| CIS AWS   | 90%    | Check with --framework cis |
| SOC 2     | 85%    | Check with --framework soc2 |
| GDPR      | 95%    | Check with --framework gdpr |

---

*Part of AMOS security-first architecture*
