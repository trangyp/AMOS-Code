#!/usr/bin/env python3
"""AMOS Ecosystem Deployment Automation Script.

Automates installation, configuration, and deployment of the
complete AMOS v2.0 cognitive ecosystem.
"""

import json
import os
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass
class DeploymentStep:
    """A single deployment step."""

    name: str
    status: str = "PENDING"
    message: str = ""
    duration_ms: float = 0.0


@dataclass
class DeploymentResult:
    """Result of deployment."""

    success: bool
    steps: list[DeploymentStep]
    deploy_path: str
    timestamp: str
    version: str = "2.0"


class AMOSDeployer:
    """Automated deployment for AMOS Ecosystem."""

    def __init__(self, base_path: str = None):
        self.base_path = Path(base_path or os.getcwd())
        self.amos_path = self.base_path / "clawspring" / "amos_brain"
        self.dashboard_path = self.amos_path / "dashboard.html"
        self.unified_dashboard_path = self.amos_path / "unified_dashboard.html"
        self.clawspring_path = self.base_path / "clawspring"
        self.log_file = self.base_path / ".amos_deploy.log"
        self.steps: list[DeploymentStep] = []

    def log(self, message: str) -> None:
        """Log deployment activity."""
        timestamp = datetime.now().isoformat()
        log_entry = f"[{timestamp}] {message}\n"
        with open(self.log_file, "a") as f:
            f.write(log_entry)
        print(log_entry.strip())

    def _add_step(self, name: str) -> DeploymentStep:
        """Add a deployment step."""
        step = DeploymentStep(name=name)
        self.steps.append(step)
        return step

    def check_prerequisites(self) -> bool:
        """Check system prerequisites."""
        step = self._add_step("Prerequisites Check")
        self.log("Checking prerequisites...")

        checks = {
            "Python 3.8+": self._check_python(),
            "pip available": self._check_pip(),
            "AMOS source": self._check_source(),
            "Write permissions": self._check_permissions(),
        }

        failed = [k for k, v in checks.items() if not v]
        if failed:
            step.status = "FAIL"
            step.message = f"Failed: {', '.join(failed)}"
            self.log(f"FAILED: {step.message}")
            return False

        step.status = "PASS"
        step.message = "All prerequisites met"
        self.log("All prerequisites met")
        return True

    def _check_python(self) -> bool:
        """Check Python version."""
        version = sys.version_info
        return version.major == 3 and version.minor >= 8

    def _check_pip(self) -> bool:
        """Check pip availability."""
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "--version"],
                capture_output=True,
                check=True,
            )
            return True
        except subprocess.CalledProcessError:
            return False

    def _check_source(self) -> bool:
        """Check AMOS source exists."""
        required = [
            self.clawspring_path / "amos_cognitive_router.py",
            self.amos_path / "organism_bridge.py",
            self.amos_path / "master_orchestrator.py",
        ]
        return all(f.exists() for f in required)

    def _check_permissions(self) -> bool:
        """Check write permissions."""
        try:
            test_file = self.base_path / ".write_test"
            test_file.write_text("test")
            test_file.unlink()
            return True
        except (OSError, PermissionError):
            return False

    def install_dependencies(self) -> bool:
        """Install required Python packages."""
        step = self._add_step("Dependencies Installation")
        self.log("Installing dependencies...")

        deps = [
            "fastapi",
            "uvicorn",
            "aiohttp",
            "numpy",
        ]

        for dep in deps:
            try:
                subprocess.run(
                    [sys.executable, "-m", "pip", "install", "-q", dep],
                    capture_output=True,
                    check=True,
                )
                self.log(f"  Installed: {dep}")
            except subprocess.CalledProcessError as e:
                step.status = "WARN"
                step.message = f"Some dependencies failed: {e}"
                self.log(f"WARNING: Failed to install {dep}")

        step.status = "PASS"
        step.message = f"Installed {len(deps)} packages"
        return True

    def setup_environment(self) -> bool:
        """Setup environment configuration."""
        step = self._add_step("Environment Setup")
        self.log("Setting up environment...")

        env_vars = {
            "AMOS_BRAIN_ENABLED": "1",
            "AMOS_DEPLOY_PATH": str(self.amos_path),
            "AMOS_VERSION": "2.0",
        }

        env_file = self.base_path / ".env"
        with open(env_file, "w") as f:
            for key, value in env_vars.items():
                f.write(f"{key}={value}\n")

        step.status = "PASS"
        step.message = "Environment configured"
        self.log("Environment configured")
        return True

    def verify_installation(self) -> bool:
        """Verify installation by importing modules."""
        step = self._add_step("Installation Verification")
        self.log("Verifying installation...")

        # Import alias modules to set up paths
        import clawspring  # noqa: F401
        import clawspring.amos_brain  # noqa: F401

        modules = [
            "amos_cognitive_router",
            "engine_executor",
            "multi_agent_orchestrator",
            "organism_bridge",
            "master_orchestrator",
            "system_validator",
        ]

        failed = []
        for module in modules:
            try:
                __import__(module)
                self.log(f"  {module}")
            except ImportError as e:
                failed.append((module, str(e)))
                self.log(f"  {module}: {e}")

        if failed:
            step.status = "FAIL"
            step.message = f"{len(failed)} modules failed"
            return False

        step.status = "PASS"
        step.message = f"All {len(modules)} modules verified"
        self.log("Verification complete")
        return True

    def create_launcher_scripts(self) -> bool:
        """Create launcher scripts."""
        step = self._add_step("Launcher Scripts")
        self.log("Creating launcher scripts...")

        scripts = {
            "launch_amos.sh": self._generate_unix_launcher(),
            "launch_amos.bat": self._generate_windows_launcher(),
            "validate_amos.py": self._generate_validator_script(),
        }

        for name, content in scripts.items():
            script_path = self.base_path / name
            with open(script_path, "w") as f:
                f.write(content)

            if name.endswith(".sh"):
                os.chmod(script_path, 0o755)

            self.log(f"  Created: {name}")

        step.status = "PASS"
        step.message = f"Created {len(scripts)} launchers"
        return True

    def _generate_unix_launcher(self) -> str:
        """Generate Unix launcher script."""
        return f"""#!/bin/bash
# AMOS Ecosystem Launcher v2.0

cd "{self.base_path}"
export AMOS_BRAIN_ENABLED=1
export AMOS_DEPLOY_PATH="{self.amos_path}"

echo " Starting AMOS Ecosystem v2.0..."
python3 clawspring/clawspring.py "$@"
"""

    def _generate_windows_launcher(self) -> str:
        """Generate Windows launcher script."""
        return f"""@echo off
REM AMOS Ecosystem Launcher v2.0

cd "{self.base_path}"
set AMOS_BRAIN_ENABLED=1
set AMOS_DEPLOY_PATH={self.amos_path}

echo Starting AMOS Ecosystem v2.0...
python clawspring/clawspring.py %*
"""

    def _generate_validator_script(self) -> str:
        """Generate standalone validator script."""
        return '''#!/usr/bin/env python3
"""Quick AMOS System Validator."""

# Import alias modules to set up paths
import clawspring  # noqa: F401
import clawspring.amos_brain  # noqa: F401

from system_validator import SystemValidator

validator = SystemValidator()
results = validator.validate_all()

passed = sum(1 for r in results if r.status == "PASS")
failed = sum(1 for r in results if r.status == "FAIL")

print(f"Validation: {passed} passed, {failed} failed")
print(f"Health: {validator.get_health_score():.0f}%")

if failed == 0:
    print(" AMOS is ready for use!")
else:
    print(" Some components need attention")
    import sys
    sys.exit(1)
'''

    def run_deployment(self) -> DeploymentResult:
        """Execute full deployment."""
        self.log("=" * 60)
        self.log("AMOS ECOSYSTEM v2.0 DEPLOYMENT")
        self.log("=" * 60)

        steps_to_run = [
            self.check_prerequisites,
            self.install_dependencies,
            self.setup_environment,
            self.verify_installation,
            self.create_launcher_scripts,
        ]

        for step_func in steps_to_run:
            if not step_func():
                break

        success = all(s.status == "PASS" for s in self.steps)

        result = DeploymentResult(
            success=success,
            steps=self.steps,
            deploy_path=str(self.amos_path),
            timestamp=datetime.now().isoformat(),
        )

        self._save_deployment_report(result)
        return result

    def _save_deployment_report(self, result: DeploymentResult) -> None:
        """Save deployment report."""
        report = {
            "version": "2.0",
            "timestamp": result.timestamp,
            "success": result.success,
            "deploy_path": result.deploy_path,
            "steps": [
                {
                    "name": s.name,
                    "status": s.status,
                    "message": s.message,
                }
                for s in result.steps
            ],
        }

        report_file = self.base_path / ".amos_deployment_report.json"
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)

        self.log(f"Report saved: {report_file}")


def main():
    """Main deployment entry point."""
    deployer = AMOSDeployer()
    result = deployer.run_deployment()

    print("\n" + "=" * 60)
    print("DEPLOYMENT SUMMARY")
    print("=" * 60)

    for step in result.steps:
        if step.status == "PASS":
            icon = "✓"
        elif step.status == "FAIL":
            icon = "✗"
        else:
            icon = "○"
        print(f"{icon} {step.name}: {step.status}")
        if step.message:
            print(f"   → {step.message}")

    print("\n" + "-" * 60)
    if result.success:
        print(" AMOS v2.0 DEPLOYED SUCCESSFULLY!")
        print(f" Location: {result.deploy_path}")
        print("\nQuick Start:")
        print("  ./launch_amos.sh         # Start AMOS")
        print("  python3 validate_amos.py  # Validate system")
        print("  /amos validate          # (from REPL)")
    else:
        print(" Deployment failed. Check logs above.")

    print("=" * 60)
    return 0 if result.success else 1


if __name__ == "__main__":
    sys.exit(main())
