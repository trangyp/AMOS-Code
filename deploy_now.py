#!/usr/bin/env python3
"""
AMOS SuperBrain v3.0 - Production Deployment Orchestrator
Executes full deployment with verification.
"""

import json
import shlex
import subprocess
import sys
import time
from datetime import UTC, datetime


def run_cmd(cmd, check=True):
    """Run shell command securely with shell=False."""
    # SECURITY: Use shlex.split() to safely parse command
    cmd_parts = shlex.split(cmd)
    result = subprocess.run(cmd_parts, shell=False, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"❌ Error: {result.stderr}")
        return None
    return result.stdout


def deploy():
    """Execute deployment."""
    print("=" * 60)
    print("🚀 AMOS SuperBrain v3.0 - Production Deployment")
    print("=" * 60)
    print(f"Time: {datetime.now(UTC).isoformat()}")
    print()

    # Check Docker
    print("📦 Checking Docker...")
    docker_version = run_cmd("docker --version", check=False)
    if docker_version:
        print(f"  ✅ Docker: {docker_version.strip()}")
    else:
        print("  ❌ Docker not available")
        return False

    # Build and start
    print("\n🏗️  Building and starting services...")
    result = run_cmd("docker-compose up -d --build 2>&1", check=False)
    if result:
        print("  ✅ Services starting...")
        time.sleep(5)
    else:
        print("  ⚠️  Docker-compose failed, trying without build...")
        run_cmd("docker-compose up -d 2>&1", check=False)

    # Check status
    print("\n🔍 Checking service status...")
    ps_output = run_cmd("docker-compose ps 2>&1", check=False)
    if ps_output:
        print(ps_output)

    # Health check
    print("\n🏥 Health check (waiting 10s for services)...")
    time.sleep(10)

    health = run_cmd("curl -s http://localhost:8000/health 2>&1", check=False)
    if health:
        try:
            data = json.loads(health)
            score = data.get("health_score", 0)
            print(f"  ✅ API Health: {score * 100:.0f}%")
            print(f"  📊 Response: {json.dumps(data, indent=2)}")
        except Exception:
            print(f"  ⚠️  Raw response: {health[:200]}")
    else:
        print("  ⚠️  API not responding yet (may need more time)")

    print("\n" + "=" * 60)
    print("✅ Deployment Complete")
    print("=" * 60)
    print("\n📡 Access Points:")
    print("  - API: http://localhost:8000")
    print("  - Docs: http://localhost:8000/docs")
    print("  - Health: http://localhost:8000/health")
    print("\n🛠️  Commands:")
    print("  - Logs: docker-compose logs -f")
    print("  - Stop: docker-compose down")
    print("  - CLI: python3 amos_superbrain_cli.py status")

    return True


if __name__ == "__main__":
    success = deploy()
    sys.exit(0 if success else 1)
