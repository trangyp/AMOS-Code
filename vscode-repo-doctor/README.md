# Repo Doctor for VS Code

Repository verification and control system with quantum-inspired state modeling, integrated directly into your IDE.

## Features

- **Repository State Visualization**: See your repo's health as a quantum state vector with real-time scoring
- **Hard Invariant Monitoring**: Automatic detection of 12 critical invariant failures
- **One-Click Scanning**: Run full diagnostics with external sensors (ruff, pyright, pip-audit, deptry)
- **Auto-Fix Integration**: Apply automated fixes directly from the editor
- **Repair Planning**: Generate optimized repair sequences with minimum-energy algorithms

## Commands

| Command | Description |
|---------|-------------|
| `Repo Doctor: Scan Repository` | Quick scan of repository state |
| `Repo Doctor: Full Scan with External Sensors` | Comprehensive analysis with external tools |
| `Repo Doctor: Apply Auto-Fixes` | Run automated fixes (with dry-run option) |
| `Repo Doctor: Show State Vector` | Display quantum state visualization |
| `Repo Doctor: Generate Repair Plan` | Create optimized repair sequence |

## Views

The extension adds a **Repo Doctor** activity bar panel with three views:

1. **Repository State** - Score, energy, health status
2. **Hard Invariants** - List of failing invariants
3. **Repair Plan** - Suggested fixes with priorities

## Configuration

```json
{
  "repoDoctor.pythonPath": "python3",
  "repoDoctor.autoScanOnSave": false,
  "repoDoctor.externalSensors": ["ruff", "pyright", "pip-audit", "deptry"]
}
```

## Installation

1. Open VS Code
2. Go to Extensions (Ctrl+Shift+X)
3. Search for "Repo Doctor"
4. Click Install

## Development

```bash
cd vscode-repo-doctor
npm install
npm run compile
```

Press F5 to open a new Extension Development Host window.

## Requirements

- Python 3.10+
- repo-doctor Python package installed:
  ```bash
  pip install -e /path/to/repo_doctor
  ```

## License

MIT - See LICENSE file in main repo_doctor repository.
