# AMOS-Code Repository Migration Plan

**Objective**: Transform AMOS-Code from a package+platform monorepo into a clean, publishable core library.

**Target State**: 
- `AMOS-Code`: Core library package (`amos_brain`, `amosl`, etc.)
- `AMOS-Platform`: New repo for backend, infra, dashboards, deployment

---

## Phase 0: Pre-Migration Setup (PR #0)

**Branch**: `migration/setup`
**Estimated Files Changed**: 3

### Commit 1: Create migration tracking
```
commit 0a1b2c3
create MIGRATION_TRACKING.md
docs: add migration tracking document
```

### Commit 2: Create repo split checklist
```
commit 1b2c3d4
create .github/MIGRATION_CHECKLIST.yml
chore: add automated migration checklist
```

### Commit 3: Tag current state
```
commit 2c3d4e5
tag: v14.0.0-monorepo-final
git tag -a v14.0.0-monorepo-final -m "Final state before repo split"
```

---

## Phase 1: Core Package Cleanup - CLI/Launcher (PR #1)

**Branch**: `migration/core-cli-cleanup`
**Estimated Files Changed**: 12
**Risk**: Medium (entry points change)
**Rollback**: Revert console script changes in pyproject.toml

### Commit 1: Move CLI to package
```
commit 3d4e5f6
move amos_brain_cli.py → amos_brain/cli.py
refactor: relocate CLI from root to package module

- Move file contents with adjusted imports
- Remove sys.path.insert(0, ...) pattern
- Update relative imports to package imports
```

**Diff Targets**:
- `amos_brain_cli.py` → `amos_brain/cli.py` (moved, imports fixed)
- `amos_brain/cli.py` new file with `def main():` entry point

### Commit 2: Move launcher to package
```
commit 4e5f6g7
move amos_brain_launcher.py → amos_brain/launcher.py
refactor: relocate launcher from root to package

- Replace subprocess filename calls with module imports
- Replace subprocess calls with direct function calls where appropriate
- Keep menu interface unchanged
```

**Diff Targets**:
- `amos_brain_launcher.py` → `amos_brain/launcher.py` (moved)
- Replace `subprocess.run([sys.executable, "amos_brain_tutorial.py"])` with direct calls

### Commit 3: Update tutorial entry point
```
commit 5f6g7h8
move amos_brain_tutorial.py → amos_brain/tutorial.py
refactor: relocate tutorial to package

- Add main() entry point
- Update import paths
```

### Commit 4: Update demo entry points
```
commit 6g7h8i9
move demo_cookbook.py → amos_brain/examples/cookbook.py
refactor: relocate cookbook demo to package examples

- Create amos_brain/examples/ directory
- Move cookbook demo with updated imports
- Add main() entry point
```

### Commit 5: Update pyproject.toml console scripts
```
commit 7h8i9j0
edit pyproject.toml
chore: update console scripts to point to package modules

[project.scripts]
amos-brain = "amos_brain.launcher:main"
amos-tutorial = "amos_brain.tutorial:main"
amos-cli = "amos_brain.cli:main"
amosl = "amosl.cli:main"
```

### Commit 6: Clean up pyproject.toml py-modules list
```
commit 8i9j0k1
edit pyproject.toml
chore: remove relocated modules from py-modules list

- Remove amos_brain_cli, amos_brain_launcher, amos_brain_tutorial
- Keep only modules that stay at root
```

### Commit 7: Create root shim for backward compatibility (optional)
```
commit 9j0k1l2
create amos_brain_cli.py (thin shim)
create amos_brain_launcher.py (thin shim)
create amos_brain_tutorial.py (thin shim)
feat: add backward-compatible shims with deprecation warnings

```python
# amos_brain_cli.py
import warnings
warnings.warn(
    "Running CLI from repo root is deprecated. Use 'amos-cli' instead.",
    DeprecationWarning,
    stacklevel=2
)
from amos_brain.cli import main
if __name__ == "__main__":
    main()
```
```

### Commit 8: Update README install instructions
```
commit 0k1l2m3
edit README.MD
docs: rewrite install/run instructions for package usage

- Replace `python amos_brain_launcher.py` with `amos-brain`
- Replace `python amos_brain_cli.py` with `amos-cli`
- Add pip install instructions
```

---

## Phase 2: Clean Package Discovery (PR #2)

**Branch**: `migration/package-discovery`
**Estimated Files Changed**: 4
**Risk**: Low

### Commit 1: Modernize package discovery
```
commit 1l2m3n4
edit pyproject.toml
chore: use automatic package discovery

[tool.setuptools.packages.find]
where = ["."]
include = ["amos_brain*", "amosl*", "amos_model_fabric*", "memory*", "multi_agent*", "skill*", "search*", "streaming*"]
exclude = ["tests*", "backend*", "dashboard*", "admin-dashboard*", "analytics*", "monitoring*", "k8s*", "helm*", "terraform*"]
```

### Commit 2: Clean up manual py-modules
```
commit 2m3n4o5
edit pyproject.toml
chore: remove redundant py-modules configuration

- Remove all manual py-modules (now handled by package discovery)
- Keep only non-package modules if any
```

### Commit 3: Add optional dependency extras
```
commit 3n4o5p6
edit pyproject.toml
feat: define optional dependency extras

[project.optional-dependencies]
dev = ["pytest>=7.0.0", "pytest-asyncio>=0.21.0", ...]
docs = ["mkdocs>=1.5.0", "mkdocs-material>=9.0.0"]
server = ["fastapi>=0.100.0", "uvicorn>=0.23.0"]  # if keeping server code
cognitive = ["clawspring"]
```

### Commit 4: Verify MANIFEST.in
```
commit 4o5p6q7
edit MANIFEST.in
chore: ensure only library assets are included

include LICENSE
include README.md
include CHANGELOG.md
recursive-include amos_brain *.json *.md
recursive-include amosl *.json *.md
exclude backend/*
exclude dashboard/*
exclude k8s/*
exclude helm/*
exclude terraform/*
```

---

## Phase 3: API Contracts & SDK Validation (PR #3)

**Branch**: `migration/api-contracts`
**Estimated Files Changed**: 8
**Risk**: Low

### Commit 1: Verify OpenAPI spec is current
```
commit 5p6q7r8
edit AMOS_OPENAPI_SPEC.yaml
chore: verify OpenAPI spec matches current API

- Ensure all endpoints are documented
- Version bump if needed
```

### Commit 2: Add SDK drift check to CI
```
commit 6q7r8s9
create .github/workflows/sdk-drift-check.yml
ci: add SDK drift detection workflow

```yaml
name: SDK Drift Check
on: [push, pull_request]
jobs:
  check-sdk:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Generate SDK from spec
        run: |
          openapi-generator-cli generate \
            -i AMOS_OPENAPI_SPEC.yaml \
            -g python \
            -o /tmp/generated-sdk
      - name: Compare with checked-in SDK
        run: diff -r /tmp/generated-sdk/sdk/ sdk/python/ || exit 1
```
```

### Commit 3: Add SDK generation script
```
commit 7r8s9t0
create scripts/generate-sdk.sh
chore: add SDK generation script

#!/bin/bash
set -e
openapi-generator-cli generate \
  -i AMOS_OPENAPI_SPEC.yaml \
  -g python \
  -o sdk/python \
  --additional-properties=packageName=amos_sdk

openapi-generator-cli generate \
  -i AMOS_OPENAPI_SPEC.yaml \
  -g typescript-fetch \
  -o sdk/typescript \
  --additional-properties=npmName=@amos/sdk
```

### Commit 4: Update SDK directory structure
```
commit 8s9t0u1
mkdir -p sdk/python sdk/typescript
move sdk/javascript/* → sdk/typescript/ (if appropriate)
chore: reorganize SDK directory structure

- Create python/ and typescript/ subdirectories
- Move existing SDK files
```

### Commit 5: Update CI to block root script additions
```
commit 9t0u1v2
edit .github/workflows/pr-checks.yml
ci: add check to prevent new root-level scripts

```yaml
- name: Check for new root scripts
  run: |
    NEW_SCRIPTS=$(git diff --name-only origin/main | grep -E '^[a-z_]+\.py$' || true)
    if [ -n "$NEW_SCRIPTS" ]; then
      echo "Error: New root-level scripts detected:"
      echo "$NEW_SCRIPTS"
      echo "Please place scripts in appropriate package directories."
      exit 1
    fi
```
```

---

## Phase 4: Documentation Consolidation (PR #4)

**Branch**: `migration/docs-cleanup`
**Estimated Files Changed**: 25
**Risk**: Low

### Commit 1: Create docs archive directory
```
commit 0u1v2w3
mkdir docs/archive/
chore: create documentation archive directory
```

### Commit 2: Move overlapping planning docs to archive
```
commit 1v2w3x4
move AMOS_5_REPO_AUTOPSY.md → docs/archive/
move AMOS_5_REPO_FIX_PLAN.md → docs/archive/
move AMOS_5_REPO_FULL_ASSESSMENT.md → docs/archive/
move AMOS_5_REPO_INTEGRATION_ARCHITECTURE.md → docs/archive/
move AMOS_5_REPO_INTEGRATION_SUMMARY.md → docs/archive/
move AMOS_6REPO_ARCHITECTURE.md → docs/archive/
move AMOS_6REPO_CONNECTION_DIAGRAM.md → docs/archive/
move AMOS_6_REPO_ARCHITECTURE.md → docs/archive/
move AMOS_6_REPO_AUTOPSY.md → docs/archive/
move AMOS_6_REPO_INTEGRATION_PLAN.md → docs/archive/
move AMOS_REPO_INTEGRATION_PLAN.md → docs/archive/
chore: archive overlapping planning documents

- Consolidate 11 overlapping architecture docs
- Keep only current canonical docs at root
```

### Commit 3: Create docs/README.md index
```
commit 2w3x4y5
create docs/README.md
docs: add documentation index

- Link to active docs
- List archived docs with reason
- Provide navigation guidance
```

### Commit 4: Update main README links
```
commit 3x4y5z6
edit README.MD
docs: update documentation links in main README

- Update architecture doc links
- Add link to docs/README.md
- Remove references to archived docs
```

### Commit 5: Standardize license references
```
commit 4y5z6a7
grep -r "MIT" --include="*.md" --include="*.py" .
edit [files with stale MIT references]
chore: standardize on Apache-2.0 license references

- Remove any remaining MIT license references
- Ensure all docs point to Apache-2.0
```

---

## Phase 5: Root File Cleanup (PR #5)

**Branch**: `migration/root-cleanup`
**Estimated Files Changed**: 30+
**Risk**: High (many deletions)
**Note**: This is preparation for the platform split

### Commit 1: Identify and categorize root files
```
commit 5z6a7b8
create ROOT_FILE_INVENTORY.md
docs: inventory all root-level files for migration

| File | Category | Action | Destination |
|------|----------|--------|-------------|
| amos_api.py | Server | Move | AMOS-Platform |
| amos_mcp_server.py | Server | Move | AMOS-Platform |
| amos_fastapi_gateway.py | Server | Move | AMOS-Platform |
| docker-compose.yml | Infra | Move | AMOS-Platform |
| Dockerfile* | Infra | Move | AMOS-Platform |
| ... | ... | ... | ... |
```

### Commit 2: Mark server entry points
```
commit 6a7b8c9
edit amos_api.py
edit amos_mcp_server.py
edit amos_fastapi_gateway.py
docs: add deprecation notices to server entry points

```python
# Add at top of each file
"""
⚠️  DEPRECATION NOTICE
This server entry point will be moved to AMOS-Platform repository.
Please update your deployments to use the new repository location.
Target migration: PR #6
"""
```
```

### Commit 3: Create migration script for users
```
commit 7b8c9d0
create scripts/migrate-to-platform-repo.sh
feat: add user migration helper script

#!/bin/bash
# Helps users migrate to the new platform repo structure
# - Clones AMOS-Platform repo
# - Migrates configuration
# - Updates docker-compose references
```

---

## Phase 6: Platform Repo Extraction (PR #6)

**Branch**: `migration/platform-extraction` (on new repo)
**Estimated Files Changed**: 100+
**Risk**: High (creates new repo)
**Note**: This creates the new `AMOS-Platform` repository

### Step 1: Create new AMOS-Platform repository
```bash
# Commands to execute (not a commit)
gh repo create AMOS-Platform --private --clone
```

### Commit 1: Initialize platform repo structure
```
commit 0a1b2c3 (in AMOS-Platform repo)
initial commit: platform repository structure

- Add README.md
- Add LICENSE (Apache-2.0)
- Add .gitignore
```

### Commit 2: Move backend directory
```
commit 1b2c3d4 (in AMOS-Platform repo)
copy backend/ → AMOS-Platform/backend/
feat: migrate backend API code

- FastAPI server implementation
- API routes and middleware
- Database models and migrations
```

### Commit 3: Move dashboard directories
```
commit 2c3d4e5 (in AMOS-Platform repo)
copy dashboard/ → AMOS-Platform/dashboard/
copy admin-dashboard/ → AMOS-Platform/admin-dashboard/
feat: migrate dashboard applications

- React/Vue dashboard UIs
- Admin dashboard
- Static assets
```

### Commit 4: Move infrastructure code
```
commit 3d4e5f6 (in AMOS-Platform repo)
copy k8s/ → AMOS-Platform/k8s/
copy helm/ → AMOS-Platform/helm/
copy terraform/ → AMOS-Platform/terraform/
copy argocd/ → AMOS-Platform/argocd/
copy gitops/ → AMOS-Platform/gitops/
copy traefik/ → AMOS-Platform/traefik/
feat: migrate infrastructure and deployment code

- Kubernetes manifests
- Helm charts
- Terraform modules
- GitOps configurations
```

### Commit 5: Move monitoring and observability
```
commit 4e5f6g7 (in AMOS-Platform repo)
copy monitoring/ → AMOS-Platform/monitoring/
copy grafana/ → AMOS-Platform/grafana/
copy analytics/ → AMOS-Platform/analytics/
copy finops/ → AMOS-Platform/finops/
feat: migrate monitoring and analytics stack

- Prometheus/Grafana configs
- Analytics pipelines
- Cost monitoring
```

### Commit 6: Move server entry points
```
commit 5f6g7h8 (in AMOS-Platform repo)
copy amos_api.py → AMOS-Platform/src/amos_api.py
copy amos_mcp_server.py → AMOS-Platform/src/amos_mcp_server.py
copy amos_fastapi_gateway.py → AMOS-Platform/src/amos_fastapi_gateway.py
copy amos_api_gateway.py → AMOS-Platform/src/amos_api_gateway.py
copy amos_api_gateway_enterprise.py → AMOS-Platform/src/amos_api_gateway_enterprise.py
copy amos_grpc_server.py → AMOS-Platform/src/amos_grpc_server.py
copy amos_graphql_api.py → AMOS-Platform/src/amos_graphql_api.py
feat: migrate server entry points

- All API server implementations
- Gateway implementations
- Protocol handlers
```

### Commit 7: Move Docker configurations
```
commit 6g7h8i9 (in AMOS-Platform repo)
copy docker-compose*.yml → AMOS-Platform/docker/
copy Dockerfile* → AMOS-Platform/docker/
copy nginx.conf → AMOS-Platform/docker/
copy docker_entrypoint.py → AMOS-Platform/docker/
feat: migrate Docker and compose configurations

- All docker-compose files
- Dockerfiles for different services
- Nginx configurations
```

### Commit 8: Move security operations
```
commit 7h8i9j0 (in AMOS-Platform repo)
copy security/ → AMOS-Platform/security/
copy policies/ → AMOS-Platform/policies/
copy runbooks/ → AMOS-Platform/runbooks/
feat: migrate security and compliance operations

- Security scanning workflows
- OPA policies
- Operational runbooks
```

### Commit 9: Create platform repo pyproject.toml
```
commit 8i9j0k1 (in AMOS-Platform repo)
create pyproject.toml
create requirements.txt
create requirements-dev.txt
feat: add platform repository packaging

- Define AMOS-Platform package
- Add dependency on amos-brain (core library)
- Server-specific dependencies
```

### Commit 10: Add inter-repo dependency
```
commit 9j0k1l2 (in AMOS-Platform repo)
edit pyproject.toml
deps: add amos-brain core library dependency

[project.dependencies]
amos-brain = ">=14.0.0"
```

---

## Phase 7: Core Repo Cleanup Post-Extraction (PR #7)

**Branch**: `migration/core-cleanup`
**Estimated Files Changed**: 50+
**Risk**: High (deletions)
**Note**: This removes files that were moved to AMOS-Platform

### Commit 1: Remove backend directory
```
commit 0k1l2m3
rm -rf backend/
chore: remove backend (moved to AMOS-Platform)
```

### Commit 2: Remove dashboard directories
```
commit 1l2m3n4
rm -rf dashboard/ admin-dashboard/
chore: remove dashboards (moved to AMOS-Platform)
```

### Commit 3: Remove infrastructure directories
```
commit 2m3n4o5
rm -rf k8s/ helm/ terraform/ argocd/ gitops/ traefik/
chore: remove infrastructure code (moved to AMOS-Platform)
```

### Commit 4: Remove monitoring directories
```
commit 3n4o5p6
rm -rf monitoring/ grafana/ analytics/ finops/
chore: remove monitoring stack (moved to AMOS-Platform)
```

### Commit 5: Remove server entry points
```
commit 4o5p6q7
rm amos_api.py amos_mcp_server.py amos_fastapi_gateway.py
rm amos_api_gateway.py amos_api_gateway_enterprise.py
rm amos_grpc_server.py amos_graphql_api.py amos_api_server.py
rm amos_api_enhanced.py amos_api_simple.py amos_api_v2.py
rm amos_api_hub.py amos_api_integration.py
chore: remove server entry points (moved to AMOS-Platform)
```

### Commit 6: Remove Docker files
```
commit 5p6q7r8
rm docker-compose*.yml Dockerfile* nginx.conf docker_entrypoint.py
chore: remove Docker configurations (moved to AMOS-Platform)
```

### Commit 7: Remove security operations
```
commit 6q7r8s9
rm -rf security/ policies/ runbooks/
chore: remove security operations (moved to AMOS-Platform)
```

### Commit 8: Remove database migration files (platform-specific)
```
commit 7r8s9t0
rm -rf migrations/ alembic/ alembic.ini
chore: remove platform database migrations

- Core library doesn't need migrations
- Platform manages its own database schema
```

### Commit 9: Update .gitignore for cleaner repo
```
commit 8s9t0u1
edit .gitignore
chore: update gitignore for library-only repo

- Remove platform-specific ignores
- Add library-specific patterns
```

---

## Phase 8: CI/CD Updates (PR #8)

**Branch**: `migration/ci-cleanup`
**Estimated Files Changed**: 15
**Risk**: Medium

### Commit 1: Update GitHub workflows for library
```
commit 9t0u1v2
edit .github/workflows/amos-ci.yml
edit .github/workflows/amos-production-stack-ci.yml
ci: update workflows for library-only repository

- Remove Docker build/push for server images
- Remove K8s deployment steps
- Add package build and publish steps
- Keep unit tests, linting
```

### Commit 2: Add package build workflow
```
commit 0v1w2x3
create .github/workflows/build-package.yml
ci: add Python package build workflow

```yaml
name: Build Package
on: [push, pull_request]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: pip install build
      - run: python -m build
      - uses: actions/upload-artifact@v4
        with:
          name: dist
          path: dist/
```
```

### Commit 3: Add import smoke test
```
commit 1w2x3y4
edit .github/workflows/amos-ci.yml
ci: add import smoke test from clean install

```yaml
- name: Smoke test
  run: |
    pip install dist/*.whl
    python -c "import amos_brain; import amosl; print('✓ Imports OK')"
    amos-cli --help
    amos-brain --help
```
```

### Commit 4: Update pre-commit config
```
commit 2x3y4z5
edit .pre-commit-config.yaml
chore: update pre-commit for library repo

- Remove platform-specific hooks if any
- Add package validation hooks
```

### Commit 5: Remove platform-specific workflow files
```
commit 3y4z5a6
rm .github/workflows/amos-production-stack-ci.yml
rm .github/workflows/deploy-*.yml
chore: remove platform deployment workflows
```

---

## Phase 9: Final Verification & Tag (PR #9)

**Branch**: `migration/final-verification`
**Estimated Files Changed**: 5
**Risk**: Low

### Commit 1: Create final structure diagram
```
commit 4z5a6b7
create REPO_STRUCTURE.md
docs: document final repository structure

AMOS-Code/
├── amos_brain/          # Core cognitive library
├── amosl/               # Formal language runtime
├── amos_model_fabric/   # Model management
├── memory/              # Memory subsystem
├── multi_agent/         # Multi-agent orchestration
├── skill/               # Skill system
├── search/              # Search capabilities
├── streaming/           # Streaming support
├── examples/            # Usage examples
├── tests/               # Test suite
├── sdk/                 # Generated SDKs
└── docs/                # Documentation
```

### Commit 2: Verify package install from clean environment
```
commit 5a6b7c8
# No file changes - verification only
ci: verify clean install in CI

- Build package
- Install in fresh venv
- Test all entry points
- Test imports
```

### Commit 3: Update CHANGELOG
```
commit 6b7c8d9
edit CHANGELOG.md
docs: update changelog for v15.0.0 repo restructure

## [15.0.0] - 2024-XX-XX
### Changed
- Repository restructured as pure library package
- Moved server/infra code to AMOS-Platform repo
- CLI entry points now use package modules
- Simplified package discovery

### Removed
- Backend API code (moved to AMOS-Platform)
- Dashboard applications (moved to AMOS-Platform)
- Infrastructure configs (moved to AMOS-Platform)
- Docker compose files (moved to AMOS-Platform)
```

### Commit 4: Tag v15.0.0
```
commit 7c8d9e0
tag: v15.0.0
tag: v15.0.0 - Library restructure complete

Major version bump for breaking structural changes.
```

### Commit 5: Update README with new structure
```
commit 8d9e0f1
edit README.MD
docs: finalize README for library-only repository

- Clear installation instructions
- Clear usage examples
- Link to AMOS-Platform for server deployments
- Updated architecture description
```

---

## Post-Migration: AMOS-Platform Setup

After Phase 6, the AMOS-Platform repository needs these additional steps:

### Step 1: Add submodule reference (optional)
```
cd AMOS-Platform
git submodule add https://github.com/trangyp/AMOS-Code.git vendor/amos-core
```

### Step 2: Create integration tests
```
create tests/test_amos_core_integration.py
# Tests that verify amos-brain library integration
```

### Step 3: Create deployment documentation
```
create DEPLOYMENT.md
# Platform-specific deployment guide
```

---

## Rollback Plan

If any PR needs rollback:

1. **PR #1-5 (before extraction)**: Revert commits, restore files from git
2. **PR #6 (platform extraction)**: Delete AMOS-Platform repo, restore files in AMOS-Code
3. **PR #7 (core cleanup)**: Restore deleted files from git history
4. **PR #8-9**: Revert workflow and doc changes

Emergency rollback command:
```bash
git revert --no-commit HEAD~{N}..HEAD
git checkout HEAD -- [specific files if needed]
```

---

## Summary

| Phase | PR # | Files Changed | Risk | Focus |
|-------|------|---------------|------|-------|
| 0 | #0 | 3 | Low | Setup |
| 1 | #1 | 12 | Medium | CLI/Launcher cleanup |
| 2 | #2 | 4 | Low | Package discovery |
| 3 | #3 | 8 | Low | API/SDK |
| 4 | #4 | 25 | Low | Docs consolidation |
| 5 | #5 | 30+ | Medium | Root inventory |
| 6 | #6 | 100+ | High | **Platform extraction** |
| 7 | #7 | 50+ | High | **Core cleanup** |
| 8 | #8 | 15 | Medium | CI/CD updates |
| 9 | #9 | 5 | Low | Final verification |

**Total estimated commits**: ~60 commits across 10 PRs
**Total files changed**: ~250 files
**Critical PRs**: #6 (extraction), #7 (cleanup)
