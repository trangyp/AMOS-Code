#!/usr/bin/env python3
"""AMOS Brain API Python Client

Usage:
    python python_client.py think "What are design patterns?"
    python python_client.py decide "Use SQL or NoSQL?" --options SQL NoSQL Both
    python python_client.py validate "Delete production data"
"""

import argparse
import json
import sys
from typing import Optional

try:
    import requests
except ImportError:
    print("Error: requests required. Run: pip install requests")
    sys.exit(1)


class AMOSBrainClient:
    """Client for AMOS Brain API at neurosyncai.tech"""

    def __init__(self, base_url: str = "https://neurosyncai.tech"):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()

    def health(self) -> dict:
        """Check API health."""
        r = self.session.get(f"{self.base_url}/health", timeout=10)
        r.raise_for_status()
        return r.json()

    def status(self) -> dict:
        """Get brain status."""
        r = self.session.get(f"{self.base_url}/status", timeout=10)
        r.raise_for_status()
        return r.json()

    def think(self, query: str, domain: str = "general") -> dict:
        """Send a thinking query."""
        payload = {"query": query, "domain": domain}
        r = self.session.post(f"{self.base_url}/think", json=payload, timeout=30)
        r.raise_for_status()
        return r.json()

    def decide(self, question: str, options: Optional[list] = None) -> dict:
        """Make a decision."""
        payload = {"question": question}
        if options:
            payload["options"] = options
        r = self.session.post(f"{self.base_url}/decide", json=payload, timeout=30)
        r.raise_for_status()
        return r.json()

    def validate(self, action: str) -> dict:
        """Validate an action."""
        payload = {"action": action}
        r = self.session.post(f"{self.base_url}/validate", json=payload, timeout=10)
        r.raise_for_status()
        return r.json()


def main():
    parser = argparse.ArgumentParser(description="AMOS Brain API Client")
    parser.add_argument("command", choices=["health", "status", "think", "decide", "validate"])
    parser.add_argument("input", nargs="?", help="Query, question, or action")
    parser.add_argument("--options", nargs="+", help="Decision options")
    parser.add_argument("--domain", default="general", help="Domain context")
    parser.add_argument("--url", default="https://neurosyncai.tech", help="API base URL")

    args = parser.parse_args()

    client = AMOSBrainClient(args.url)

    try:
        if args.command == "health":
            result = client.health()
            print(json.dumps(result, indent=2))

        elif args.command == "status":
            result = client.status()
            print(json.dumps(result, indent=2))

        elif args.command == "think":
            if not args.input:
                print("Error: Query required for think command")
                sys.exit(1)
            result = client.think(args.input, args.domain)
            print(json.dumps(result, indent=2))

        elif args.command == "decide":
            if not args.input:
                print("Error: Question required for decide command")
                sys.exit(1)
            result = client.decide(args.input, args.options)
            print(json.dumps(result, indent=2))

        elif args.command == "validate":
            if not args.input:
                print("Error: Action required for validate command")
                sys.exit(1)
            result = client.validate(args.input)
            print(json.dumps(result, indent=2))

    except requests.exceptions.RequestException as e:
        print(f"API Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
