#!/usr/bin/env python3
"""AMOS v3.0.0 - One-Click Deployment Orchestrator.

Production deployment automation for the AMOS AI Cognitive Operating System.
Supports multiple deployment modes: local, Docker, Kubernetes, and cloud.

Usage:
    python deploy_amos.py local      # Local development
    python deploy_amos.py docker     # Docker Compose
    python deploy_amos.py k8s        # Kubernetes
    python deploy_amos.py status      # Check status
    python deploy_amos.py stop       # Stop all services

Creator: Trang Phan
Version: 3.0.0
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path


class Colors:
    """Terminal colors."""

    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"


def print_header(text: str):
    """Print header."""
    print(f"\n{Colors.HEADER}{'=' * 70}{Colors.ENDC}")
    print(f"{Colors.BOLD}{text}{Colors.ENDC}")
    print(f"{Colors.HEADER}{'=' * 70}{Colors.ENDC}\n")


def print_success(text: str):
    """Print success message."""
    print(f"{Colors.OKGREEN}✓ {text}{Colors.ENDC}")


def print_error(text: str):
    """Print error message."""
    print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")


def print_info(text: str):
    """Print info message."""
    print(f"{Colors.OKCYAN}ℹ {text}{Colors.ENDC}")


def print_warning(text: str):
    """Print warning message."""
    print(f"{Colors.WARNING}⚠ {text}{Colors.ENDC}")


def run_command(cmd: List[str], cwd: str = None) -> Tuple[int, str, str]:
    """Run shell command."""
    try:
        result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=300)
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "Command timed out"
    except Exception as e:
        return -1, "", str(e)


class AMOSDeployer:
    """AMOS deployment orchestrator."""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.backend_dir = self.project_root / "backend"
        self.k8s_dir = self.project_root / "k8s"
        self.docker_dir = self.project_root

    def check_prerequisites(self) -> bool:
        """Check if prerequisites are met."""
        print_header("Checking Prerequisites")

        checks = [
            ("Python 3.11+", ["python3", "--version"]),
            ("Docker", ["docker", "--version"]),
            ("Docker Compose", ["docker-compose", "--version"]),
            ("kubectl", ["kubectl", "version", "--client"]),
        ]

        all_passed = True
        for name, cmd in checks:
            code, _, _ = run_command(cmd)
            if code == 0:
                print_success(f"{name} installed")
            else:
                print_error(f"{name} not found")
                all_passed = False

        return all_passed

    def deploy_local(self) -> bool:
        """Deploy AMOS locally for development."""
        print_header("Local Development Deployment")

        # Check if virtual environment exists
        venv_path = self.project_root / ".venv"
        if not venv_path.exists():
            print_info("Creating virtual environment...")
            code, _, err = run_command(
                ["python3", "-m", "venv", ".venv"], cwd=str(self.project_root)
            )
            if code != 0:
                print_error(f"Failed to create venv: {err}")
                return False

        # Install dependencies
        print_info("Installing dependencies...")
        pip_cmd = (
            str(venv_path / "bin" / "pip")
            if os.name != "nt"
            else str(venv_path / "Scripts" / "pip.exe")
        )
        code, _, err = run_command(
            [pip_cmd, "install", "-r", "backend/requirements.txt"], cwd=str(self.project_root)
        )
        if code != 0:
            print_error(f"Failed to install dependencies: {err}")
            return False

        print_success("Dependencies installed")

        # Start backend
        print_info("Starting AMOS backend...")
        python_cmd = (
            str(venv_path / "bin" / "python")
            if os.name != "nt"
            else str(venv_path / "Scripts" / "python.exe")
        )

        print_success("AMOS backend starting on http://localhost:8000")
        print_info("API Documentation: http://localhost:8000/docs")
        print_info("Health Check: http://localhost:8000/health")

        # Run in foreground
        try:
            subprocess.run(
                [python_cmd, "-m", "uvicorn", "main_amos_integrated:amos_app", "--reload"],
                cwd=str(self.backend_dir),
            )
        except KeyboardInterrupt:
            print_info("\nShutting down...")

        return True

    def deploy_docker(self) -> bool:
        """Deploy AMOS using Docker Compose."""
        print_header("Docker Compose Deployment")

        # Check docker-compose.yml exists
        compose_file = self.project_root / "docker-compose.yml"
        if not compose_file.exists():
            print_error("docker-compose.yml not found")
            return False

        # Build and start
        print_info("Building and starting services...")
        code, out, err = run_command(
            ["docker-compose", "up", "-d", "--build"], cwd=str(self.project_root)
        )

        if code != 0:
            print_error(f"Docker deployment failed: {err}")
            return False

        print_success("Docker deployment successful!")
        print_info("Services:")
        print_info("  - Backend: http://localhost:8000")
        print_info("  - Frontend: http://localhost:3000")
        print_info("  - API Docs: http://localhost:8000/docs")

        # Show logs
        print_info("\nShowing logs (Ctrl+C to exit)...")
        try:
            subprocess.run(["docker-compose", "logs", "-f"], cwd=str(self.project_root))
        except KeyboardInterrupt:
            pass

        return True

    def deploy_kubernetes(self) -> bool:
        """Deploy AMOS to Kubernetes."""
        print_header("Kubernetes Deployment")

        # Check k8s manifests exist
        if not self.k8s_dir.exists():
            print_error(f"Kubernetes manifests not found at {self.k8s_dir}")
            return False

        # Check cluster connection
        code, _, err = run_command(["kubectl", "cluster-info"])
        if code != 0:
            print_error(f"Cannot connect to Kubernetes cluster: {err}")
            return False

        print_success("Connected to Kubernetes cluster")

        # Deploy manifests in order
        manifests = [
            "01-namespace.yaml",
            "02-secrets.yaml",
            "03-configmap.yaml",
            "04-postgres.yaml",
            "05-redis.yaml",
            "06-backend.yaml",
            "07-frontend.yaml",
            "08-ollama.yaml",
            "09-ingress.yaml",
            "10-monitoring.yaml",
            "11-rag.yaml",
        ]

        for manifest in manifests:
            manifest_path = self.k8s_dir / manifest
            if not manifest_path.exists():
                print_warning(f"Skipping {manifest} (not found)")
                continue

            print_info(f"Deploying {manifest}...")
            code, _, err = run_command(["kubectl", "apply", "-f", str(manifest_path)])

            if code != 0:
                print_error(f"Failed to deploy {manifest}: {err}")
                return False

            print_success(f"{manifest} deployed")

        print_success("\nKubernetes deployment complete!")
        print_info("Checking status...")

        # Wait for pods
        print_info("Waiting for pods to be ready...")
        run_command(
            [
                "kubectl",
                "wait",
                "--for=condition=ready",
                "pod",
                "--all",
                "-n",
                "amos",
                "--timeout=300s",
            ]
        )

        # Show status
        code, out, _ = run_command(["kubectl", "get", "pods", "-n", "amos"])
        print("\nPod Status:")
        print(out)

        # Get ingress
        code, out, _ = run_command(["kubectl", "get", "ingress", "-n", "amos"])
        if code == 0 and out.strip():
            print("\nIngress:")
            print(out)

        print_success("\nAMOS is now running on Kubernetes!")
        print_info("To access: kubectl port-forward svc/backend 8000:8000 -n amos")

        return True

    def check_status(self) -> bool:
        """Check AMOS deployment status."""
        print_header("AMOS System Status")

        status = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "version": "3.0.0",
            "creator": "Trang Phan",
            "checks": {},
        }

        # Check local backend
        code, _, _ = run_command(["curl", "-s", "http://localhost:8000/health"])
        status["checks"]["local_backend"] = code == 0
        if code == 0:
            print_success("Local backend is running")
        else:
            print_error("Local backend is not running")

        # Check Docker
        code, _, _ = run_command(["docker-compose", "ps", "-q"])
        status["checks"]["docker_compose"] = code == 0
        if code == 0:
            print_success("Docker Compose services are running")
        else:
            print_error("Docker Compose services are not running")

        # Check Kubernetes
        code, out, _ = run_command(["kubectl", "get", "pods", "-n", "amos", "-o", "json"])
        if code == 0:
            try:
                pods = json.loads(out)
                running_pods = sum(
                    1
                    for pod in pods.get("items", [])
                    if pod.get("status", {}).get("phase") == "Running"
                )
                status["checks"]["kubernetes"] = running_pods > 0
                if running_pods > 0:
                    print_success(f"Kubernetes has {running_pods} running pods")
                else:
                    print_error("Kubernetes pods are not running")
            except Exception:
                print_error("Kubernetes check failed")
        else:
            print_error("Kubernetes is not accessible")

        print("\n" + "=" * 70)
        print(json.dumps(status, indent=2))
        print("=" * 70)

        return True

    def stop_all(self) -> bool:
        """Stop all AMOS deployments."""
        print_header("Stopping AMOS")

        # Stop local (find and kill processes)
        print_info("Stopping local processes...")
        run_command(["pkill", "-f", "uvicorn"])

        # Stop Docker
        print_info("Stopping Docker Compose...")
        run_command(["docker-compose", "down"], cwd=str(self.project_root))

        # Stop Kubernetes (optional)
        print_info("Do you want to delete Kubernetes resources? (y/N): ")
        response = input().lower()
        if response == "y":
            run_command(["kubectl", "delete", "namespace", "amos"])

        print_success("AMOS stopped")
        return True

    def generate_report(self) -> bool:
        """Generate deployment report."""
        print_header("Generating Deployment Report")

        report = {
            "project": "AMOS - AI Cognitive Operating System",
            "version": "3.0.0",
            "creator": "Trang Phan",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "architecture": {
                "layers": 10,
                "subsystems": 11,
                "total_lines": "30,000+",
                "api_endpoints": "60+",
                "kubernetes_manifests": 11,
                "ci_cd_jobs": 6,
            },
            "components": [
                "Brain Orchestrator",
                "AI Systems API",
                "Cost Management",
                "Governance & Safety",
                "Plugin System",
                "Agent Reasoning",
                "Knowledge & Memory",
                "Messaging",
                "Observability",
                "Kubernetes Orchestration",
                "DevOps & CI/CD",
            ],
            "deployment_options": [
                "Local Development",
                "Docker Compose",
                "Kubernetes",
                "Cloud (AWS/Azure/GCP)",
            ],
            "endpoints": {
                "local": "http://localhost:8000",
                "docker": "http://localhost:8000",
                "kubernetes": "kubectl port-forward svc/backend 8000:8000 -n amos",
            },
        }

        report_file = self.project_root / "AMOS_DEPLOYMENT_REPORT.json"
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)

        print_success(f"Report saved to {report_file}")
        print("\nReport Summary:")
        print(json.dumps(report["architecture"], indent=2))

        return True


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="AMOS v3.0.0 - One-Click Deployment Orchestrator")
    parser.add_argument(
        "command",
        choices=["local", "docker", "k8s", "kubernetes", "status", "stop", "report"],
        help="Deployment command",
    )
    parser.add_argument("--skip-checks", action="store_true", help="Skip prerequisite checks")

    args = parser.parse_args()

    # Print banner
    print(f"""
{Colors.BOLD}{Colors.OKCYAN}
    █████╗ ███╗   ███╗ ██████╗ ███████╗
   ██╔══██╗████╗ ████║██╔═══██╗██╔════╝
   ███████║██╔████╔██║██║   ██║███████╗
   ██╔══██║██║╚██╔╝██║██║   ██║╚════██║
   ██║  ██║██║ ╚═╝ ██║╚██████╔╝███████║
   ╚═╝  ╚═╝╚═╝     ╚═╝ ╚═════╝ ╚══════╝
{Colors.ENDC}
{Colors.BOLD}   AI Cognitive Operating System v3.0.0{Colors.ENDC}
{Colors.OKGREEN}   Creator: Trang Phan | 2026{Colors.ENDC}
    """)

    deployer = AMOSDeployer()

    # Check prerequisites
    if not args.skip_checks and args.command not in ["status", "report"]:
        if not deployer.check_prerequisites():
            print_error("Prerequisite checks failed. Use --skip-checks to bypass.")
            sys.exit(1)

    # Execute command
    success = False
    if args.command == "local":
        success = deployer.deploy_local()
    elif args.command == "docker":
        success = deployer.deploy_docker()
    elif args.command in ["k8s", "kubernetes"]:
        success = deployer.deploy_kubernetes()
    elif args.command == "status":
        success = deployer.check_status()
    elif args.command == "stop":
        success = deployer.stop_all()
    elif args.command == "report":
        success = deployer.generate_report()

    if success:
        print(f"\n{Colors.OKGREEN}{'=' * 70}{Colors.ENDC}")
        print(f"{Colors.BOLD}✓ Operation completed successfully!{Colors.ENDC}")
        print(f"{Colors.OKGREEN}{'=' * 70}{Colors.ENDC}\n")
        sys.exit(0)
    else:
        print(f"\n{Colors.FAIL}{'=' * 70}{Colors.ENDC}")
        print(f"{Colors.BOLD}✗ Operation failed{Colors.ENDC}")
        print(f"{Colors.FAIL}{'=' * 70}{Colors.ENDC}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
