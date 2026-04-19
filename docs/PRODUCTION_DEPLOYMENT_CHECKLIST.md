# AMOS SuperBrain Production Deployment Checklist v2.0.0

## Pre-Deployment Checklist

### Infrastructure Prerequisites
- [ ] AWS CLI configured with appropriate credentials
- [ ] Terraform >= 1.5.0 installed
- [ ] Access to `amos-terraform-state` S3 bucket
- [ ] IAM permissions for ECS, RDS, ElastiCache, CloudWatch
- [ ] Route53 hosted zone configured (if using custom domain)

### Code Verification
- [ ] All 12 systems have SuperBrain integration (v2.0.0)
- [ ] Integration guide reviewed: `docs/SUPERBRAIN_INTEGRATION_GUIDE.md`
- [ ] No critical lint errors in modified files
- [ ] All health checks passing locally
- [ ] Unit tests pass: `make test`

### CI/CD Verification
- [ ] GitHub Actions workflow exists: `.github/workflows/superbrain-ci.yml`
- [ ] CI pipeline passes on PR
- [ ] SuperBrain integration verification job passes
- [ ] Terraform validation job passes
- [ ] Health check validation job passes

### Test Suite Verification
- [ ] Integration test file exists: `tests/test_superbrain_integration.py`
- [ ] All SuperBrain tests pass: `pytest tests/test_superbrain_integration.py -v`
- [ ] ActionGate validation tests pass
- [ ] Audit trail recording tests pass
- [ ] Fail-open behavior tests pass
- [ ] Health check validation tests pass

### Environment Configuration
- [ ] `terraform/terraform.tfvars` reviewed for environment
- [ ] KMS key ARN configured for log encryption
- [ ] SNS topic email subscriptions confirmed
- [ ] Environment variables set in AWS Systems Manager Parameter Store

## Deployment Steps

### 1. Pre-Deploy (5 minutes)
```bash
# Verify AWS access
aws sts get-caller-identity

# Check terraform state
make sb-status

# Review deployment plan
make sb-deploy-dev
```

### 2. Infrastructure Deployment (15-20 minutes)
```bash
# Deploy to target environment
make sb-deploy-stg    # or sb-deploy-prod
```

This will:
1. Initialize Terraform with S3 backend
2. Create/Update ECS cluster and services
3. Deploy RDS PostgreSQL instance
4. Deploy ElastiCache Redis cluster
5. Create CloudWatch log groups (KMS encrypted)
6. Create CloudWatch alarms
7. Create CloudWatch dashboard
8. Configure Application Load Balancer

### 3. Post-Deployment Verification (10 minutes)
```bash
# Verify all integrations
make sb-verify
```

Expected output:
```
✓ 1. Liveness probe (/health/live)
✓ 2. Readiness probe (/health/ready)
✓ 3. SuperBrain governance (/health/superbrain)
✓ 4. Full health check (/health)
✓ 5. CloudWatch log groups
✓ 6. CloudWatch dashboard
✓ 7. CloudWatch alarms
✓ 8-17. All 10 systems governed

╔══════════════════════════════════════════════════════════════╗
║           ✓ ALL VERIFICATION TESTS PASSED                    ║
╚══════════════════════════════════════════════════════════════╝
```

### 4. Health Check Validation
```bash
# Check SuperBrain governance status
make sb-health

# Open CloudWatch dashboard
make sb-dashboard
```

## Post-Deployment Monitoring

### First Hour
- [ ] CloudWatch dashboard showing all metrics
- [ ] No alarms triggered
- [ ] `/health/superbrain` returns healthy status
- [ ] Log groups receiving audit entries
- [ ] RDS connections established
- [ ] Redis cache hit ratio > 50%

### First 24 Hours
- [ ] All CloudWatch alarms in OK state
- [ ] No 5xx errors in ALB logs
- [ ] SuperBrain governance check passes consistently
- [ ] Memory usage stable (< 80%)
- [ ] CPU usage stable (< 70%)

### First Week
- [ ] Review CloudWatch logs for errors
- [ ] Verify audit trail completeness
- [ ] Check ActionGate policy effectiveness
- [ ] Review cost estimates vs actual
- [ ] Document any issues for next deployment

## Rollback Procedures

### If Deployment Fails
```bash
# Destroy infrastructure (DESTRUCTIVE)
cd terraform && terraform destroy -var-file="terraform.tfvars"

# Or rollback to previous state
cd terraform && terraform apply -var-file="terraform.tfvars" tfplan.backup
```

### If Health Checks Fail
1. Monitor CloudWatch dashboard for health status
2. Check audit logs in /aws/amossuperbrain/${ENVIRONMENT}/audit
3. Verify SuperBrain governance status in unified dashboard
4. Run: ./scripts/verify-integration.sh ${ENVIRONMENT}
5. Check CI/CD pipeline status in GitHub Actions
6. Redis connectivity: Verify ElastiCache security group

### Emergency Contacts
- **Infrastructure Issues**: DevOps team
- **SuperBrain Issues**: Architecture team
- **CloudWatch Alarms**: On-call engineer

## Architecture Validation

### Governance Coverage
| System | Version | Status |
|--------|---------|--------|
| Production API | 2.3.0 | ✅ |
| GraphQL API | 2.3.0 | ✅ |
| Agent Messaging | 3.1.0 | ✅ |
| Agent Observability | 3.1.0 | ✅ |
| LLM Providers | 2.0.0 | ✅ |
| UBI Engine | 2.0.0 | ✅ |
| Audit Exporter | 2.0.0 | ✅ |
| AMOS Tools | 2.0.0 | ✅ |
| Knowledge Loader | 2.0.0 | ✅ |
| Master Orchestrator | 2.0.0 | ✅ |
| Cognitive Router | 2.0.0 | ✅ |
| Resilience Engine | 2.0.0 | ✅ |

**Total: 12/12 systems verified**

### Monitoring Coverage
| Resource | Alarms | Dashboard |
|----------|--------|-----------|
| SuperBrain Health | ✅ | ✅ |
| Response Time | ✅ | ✅ |
| 5xx Errors | ✅ | ✅ |
| Knowledge Loader | ✅ | ✅ |
| RDS CPU | ✅ | ✅ |
| Redis CPU | ✅ | ✅ |

## Sign-Off

- [ ] Deployment completed successfully
- [ ] All health checks passing
- [ ] Monitoring dashboard accessible
- [ ] Documentation updated
- [ ] Team notified
- [ ] Post-deployment review scheduled

---

**Document Version**: 2.0.0  
**Last Updated**: 2026-04-16  
**Maintainer**: Trang Phan  
**Environment**: Production
