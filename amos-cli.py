#!/usr/bin/env python3
"""AMOS Brain CLI - Unified Management Tool

Usage:
    amos-cli.py status          # Check system status
    amos-cli.py deploy          # Deploy to production
    amos-cli.py logs            # View logs
    amos-cli.py backup          # Create backup
    amos-cli.py monitor         # Start monitoring
    amos-cli.py test            # Run tests
    amos-cli.py key generate    # Generate API key
    amos-cli.py analytics       # Show analytics
"""

import argparse
import subprocess
import sys
import os
import json
from pathlib import Path
import requests

BASE_URL = os.environ.get('AMOS_API_URL', 'https://neurosyncai.tech')
MASTER_KEY = os.environ.get('ADMIN_MASTER_KEY', 'dev-master-key')


class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    END = '\033[0m'


def print_status(message, status="info"):
    """Print colored status message."""
    colors = {
        "success": Colors.GREEN,
        "warning": Colors.YELLOW,
        "error": Colors.RED,
        "info": Colors.BLUE
    }
    icon = {"success": "✓", "warning": "⚠", "error": "✗", "info": "ℹ"}.get(status, "•")
    print(f"{colors.get(status, '')}{icon} {message}{Colors.END}")


def cmd_status(args):
    """Check system status."""
    print_status("Checking AMOS Brain system status...", "info")
    
    try:
        # Check API health
        r = requests.get(f"{BASE_URL}/health", timeout=5)
        if r.status_code == 200:
            data = r.json()
            print_status(f"API: {data.get('status', 'unknown')}", "success")
        else:
            print_status(f"API: HTTP {r.status_code}", "error")
    except Exception as e:
        print_status(f"API: {e}", "error")
    
    # Check Docker containers
    try:
        result = subprocess.run(
            ['docker-compose', 'ps'],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent
        )
        if result.returncode == 0:
            print("\nDocker Containers:")
            print(result.stdout)
    except Exception as e:
        print_status(f"Docker check failed: {e}", "warning")


def cmd_deploy(args):
    """Deploy to production."""
    print_status("Starting deployment...", "info")
    
    # Build
    print_status("Building images...", "info")
    result = subprocess.run(
        ['docker-compose', 'build'],
        cwd=Path(__file__).parent
    )
    if result.returncode != 0:
        print_status("Build failed", "error")
        return 1
    
    # Deploy
    print_status("Deploying...", "info")
    result = subprocess.run(
        ['docker-compose', 'up', '-d'],
        cwd=Path(__file__).parent
    )
    if result.returncode == 0:
        print_status("Deployment successful!", "success")
        print(f"\nDashboard: http://localhost:8080")
        print(f"API: {BASE_URL}")
    else:
        print_status("Deployment failed", "error")
        return 1
    
    return 0


def cmd_logs(args):
    """View logs."""
    service = args.service if hasattr(args, 'service') and args.service else None
    
    cmd = ['docker-compose', 'logs', '-f']
    if service:
        cmd.append(service)
    
    print_status(f"Showing logs{' for ' + service if service else ''}...", "info")
    subprocess.run(cmd, cwd=Path(__file__).parent)


def cmd_backup(args):
    """Create backup."""
    backup_dir = Path("backups")
    backup_dir.mkdir(exist_ok=True)
    
    timestamp = subprocess.check_output(['date', '+%Y%m%d_%H%M%S']).decode().strip()
    backup_file = backup_dir / f"amos_backup_{timestamp}.tar.gz"
    
    print_status(f"Creating backup: {backup_file}", "info")
    
    # Backup database and data
    result = subprocess.run([
        'tar', '-czf', str(backup_file),
        'data/', 'amos-memory/', 'amos-logs/'
    ], cwd=Path(__file__).parent)
    
    if result.returncode == 0:
        print_status(f"Backup created: {backup_file}", "success")
    else:
        print_status("Backup failed", "error")


def cmd_monitor(args):
    """Start monitoring dashboard."""
    print_status("Starting monitoring dashboard...", "info")
    subprocess.run([sys.executable, 'monitor_dashboard.py'])


def cmd_test(args):
    """Run tests."""
    print_status("Running API tests...", "info")
    result = subprocess.run([sys.executable, 'test_api.py', '-v'])
    return result.returncode


def cmd_key_generate(args):
    """Generate API key."""
    print_status("Generating new API key...", "info")
    
    try:
        r = requests.post(
            f"{BASE_URL}/admin/keys",
            headers={"X-Master-Key": MASTER_KEY},
            timeout=10
        )
        if r.status_code == 200:
            data = r.json()
            print_status(f"API Key: {data.get('api_key')}", "success")
            print("\n⚠️  Save this key - it cannot be retrieved again!")
        else:
            print_status(f"Failed: HTTP {r.status_code}", "error")
    except Exception as e:
        print_status(f"Error: {e}", "error")


def cmd_analytics(args):
    """Show analytics."""
    print_status("Fetching analytics...", "info")
    
    try:
        r = requests.get(
            f"{BASE_URL}/admin/stats",
            headers={"X-Master-Key": MASTER_KEY},
            timeout=10
        )
        if r.status_code == 200:
            data = r.json()
            print("\n" + "=" * 50)
            print("AMOS Brain Analytics")
            print("=" * 50)
            print(json.dumps(data, indent=2))
        else:
            print_status(f"Failed: HTTP {r.status_code}", "error")
    except Exception as e:
        print_status(f"Error: {e}", "error")


def main():
    parser = argparse.ArgumentParser(
        description="AMOS Brain CLI - Unified Management Tool"
    )
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Status
    subparsers.add_parser('status', help='Check system status')
    
    # Deploy
    subparsers.add_parser('deploy', help='Deploy to production')
    
    # Logs
    logs_parser = subparsers.add_parser('logs', help='View logs')
    logs_parser.add_argument('service', nargs='?', help='Service name')
    
    # Backup
    subparsers.add_parser('backup', help='Create backup')
    
    # Monitor
    subparsers.add_parser('monitor', help='Start monitoring')
    
    # Test
    subparsers.add_parser('test', help='Run tests')
    
    # Key management
    key_parser = subparsers.add_parser('key', help='API key management')
    key_sub = key_parser.add_subparsers(dest='key_action')
    key_sub.add_parser('generate', help='Generate new API key')
    
    # Analytics
    subparsers.add_parser('analytics', help='Show analytics')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    commands = {
        'status': cmd_status,
        'deploy': cmd_deploy,
        'logs': cmd_logs,
        'backup': cmd_backup,
        'monitor': cmd_monitor,
        'test': cmd_test,
        'analytics': cmd_analytics,
    }
    
    if args.command == 'key' and args.key_action == 'generate':
        return cmd_key_generate(args) or 0
    
    if args.command in commands:
        return commands[args.command](args) or 0
    else:
        parser.print_help()
        return 1


if __name__ == '__main__':
    sys.exit(main())
