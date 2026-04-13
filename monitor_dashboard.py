#!/usr/bin/env python3
"""AMOS Brain API Monitoring Dashboard

Usage:
    python monitor_dashboard.py

Features:
    - Real-time API health monitoring
    - Request rate tracking
    - Error rate alerts
    - Response time metrics
"""

import time
import json
from datetime import datetime
from pathlib import Path
import sys

try:
    import requests
except ImportError:
    print("pip install requests")
    sys.exit(1)

BASE_URL = "http://localhost:5000"
LOG_FILE = Path("amos_monitoring.log")


class APIMonitor:
    """Monitor AMOS Brain API health and performance."""
    
    def __init__(self, base_url=BASE_URL):
        self.base_url = base_url
        self.checks = []
        self.alerts = []
    
    def check_health(self):
        """Check API health."""
        try:
            start = time.time()
            r = requests.get(f"{self.base_url}/health", timeout=5)
            elapsed = time.time() - start
            
            status = {
                'timestamp': datetime.now().isoformat(),
                'endpoint': '/health',
                'status_code': r.status_code,
                'response_time_ms': elapsed * 1000,
                'healthy': r.status_code == 200 and r.json().get('status') == 'healthy'
            }
            
            self.checks.append(status)
            return status
            
        except Exception as e:
            status = {
                'timestamp': datetime.now().isoformat(),
                'endpoint': '/health',
                'error': str(e),
                'healthy': False
            }
            self.checks.append(status)
            return status
    
    def get_stats(self):
        """Get monitoring statistics."""
        if not self.checks:
            return None
        
        recent = self.checks[-100:]  # Last 100 checks
        healthy_count = sum(1 for c in recent if c.get('healthy'))
        
        times = [c['response_time_ms'] for c in recent if 'response_time_ms' in c]
        
        return {
            'total_checks': len(self.checks),
            'recent_healthy': healthy_count,
            'recent_total': len(recent),
            'uptime_percent': healthy_count / len(recent) * 100 if recent else 0,
            'avg_response_ms': sum(times) / len(times) if times else 0,
            'last_check': self.checks[-1] if self.checks else None
        }
    
    def display_dashboard(self, stats):
        """Display monitoring dashboard."""
        print("\033[2J\033[H")  # Clear screen
        
        print("=" * 60)
        print("AMOS BRAIN API - Monitoring Dashboard")
        print(f"URL: {self.base_url}")
        print("=" * 60)
        
        if not stats:
            print("\nNo data yet...")
            return
        
        # Health status
        health_icon = "✅" if stats['uptime_percent'] > 95 else "⚠️" if stats['uptime_percent'] > 80 else "❌"
        print(f"\n{health_icon} Health Status")
        print(f"   Uptime: {stats['uptime_percent']:.1f}%")
        print(f"   Checks: {stats['recent_healthy']}/{stats['recent_total']}")
        
        # Response time
        print(f"\n📊 Response Time")
        print(f"   Average: {stats['avg_response_ms']:.1f}ms")
        
        # Last check
        if stats['last_check']:
            print(f"\n🕐 Last Check: {stats['last_check']['timestamp']}")
            if 'status_code' in stats['last_check']:
                print(f"   Status: {stats['last_check']['status_code']}")
            if 'error' in stats['last_check']:
                print(f"   ⚠️  Error: {stats['last_check']['error']}")
        
        print("\n" + "=" * 60)
        print("Press Ctrl+C to exit")
        print("=" * 60)
    
    def run(self, interval=5):
        """Run monitoring loop."""
        print(f"Starting monitor for {self.base_url}...")
        print(f"Check interval: {interval}s")
        
        try:
            while True:
                self.check_health()
                stats = self.get_stats()
                self.display_dashboard(stats)
                
                # Log to file
                with open(LOG_FILE, 'a') as f:
                    f.write(json.dumps(self.checks[-1]) + '\n')
                
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\n\nStopping monitor...")
            self.print_summary()
    
    def print_summary(self):
        """Print final summary."""
        stats = self.get_stats()
        if stats:
            print("\n📈 Session Summary:")
            print(f"   Total checks: {stats['total_checks']}")
            print(f"   Uptime: {stats['uptime_percent']:.1f}%")
            print(f"   Avg response: {stats['avg_response_ms']:.1f}ms")


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default=BASE_URL, help="API base URL")
    parser.add_argument("--interval", type=int, default=5, help="Check interval in seconds")
    args = parser.parse_args()
    
    monitor = APIMonitor(args.url)
    monitor.run(args.interval)


if __name__ == "__main__":
    main()
