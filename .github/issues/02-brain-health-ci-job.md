---
title: "P0-2: Create required brain-health CI job"
labels: ["stabilization", "phase-0", "critical", "ci-cd"]
assignees: []
---

## Problem

The repo can look green (all tests pass) while core structural assumptions are broken. We need a required CI gate that validates the **contract** not just the code.

## Proposed Solution

Create required CI job `brain-health` that gates all merges to main.

## Checks Required

| Check | Command | Failure Mode |
|-------|---------|--------------|
| **Wheel Install** | `pip install dist/amos_brain*.whl` in fresh venv | Package metadata broken |
| **Public Imports** | `python -c "import amos_brain; amos_brain.get_brain()"` outside repo root | Package structure broken |
| **Entrypoints Execute** | `amos-brain --help` from outside repo root | Entrypoint misconfigured |
| **Docker Startup** | `docker run --rm amos-brain:latest amos-brain --help` | Docker/Package drift |
| **No Root Scripts** | `! find . -maxdepth 1 -name "*.py" -executable` | Legacy pattern persists |
| **CI Alignment** | CI tests use same imports as users would | CI testing wrong surface |

## Implementation

```yaml
# .github/workflows/brain-health.yml
name: Brain Health

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  brain-health:
    name: Brain Health Gate
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Build wheel
        run: pip install build && python -m build
      
      - name: Test wheel install in fresh venv
        run: |
          python -m venv /tmp/venv
          source /tmp/venv/bin/activate
          pip install dist/amos_brain*.whl
          python -c "import amos_brain; print('OK')"
      
      - name: Test entrypoints from outside repo
        run: |
          cd /tmp
          /tmp/venv/bin/amos-brain --help
      
      - name: Test no sys.path hacks needed
        run: |
          cd /tmp
          python -c "import amos_brain" 2>&1 | grep -q "sys.path" && exit 1 || echo "OK"
      
      - name: Docker build test
        run: docker build -t amos-brain:test .
      
      - name: Docker entrypoint test
        run: docker run --rm amos-brain:test amos-brain --help
```

## Done When

- [ ] `.github/workflows/brain-health.yml` created
- [ ] Job is **required** in GitHub branch protection rules
- [ ] All 6 checks implemented and passing
- [ ] Documentation in `docs/CI.md`
- [ ] Failing examples tested (e.g., PR that breaks entrypoint)

## Related

- Depends on: #1 (canonical runtime contract)
- Blocks: All feature work until passing
- Precedes: #3 (path hacks), #4 (entrypoints)
