#!/usr/bin/env python3
"""Verify AMOS Brain deployment to neurosyncai.tech"""

import requests
import sys

BASE_URL = "https://neurosyncai.tech"

def test_endpoint(path, method="GET", data=None):
    try:
        url = f"{BASE_URL}{path}"
        if method == "GET":
            r = requests.get(url, timeout=10)
        else:
            r = requests.post(url, json=data, timeout=10)
        return r.status_code == 200, r.json() if r.status_code == 200 else r.text
    except Exception as e:
        return False, str(e)

def main():
    print("=" * 50)
    print("AMOS Brain Deployment Verification")
    print(f"Target: {BASE_URL}")
    print("=" * 50)

    tests = [
        ("/health", "GET", None, "Health Check"),
        ("/status", "GET", None, "Brain Status"),
        ("/think", "POST", {"query": "Test deployment"}, "Think Endpoint"),
    ]

    all_pass = True
    for path, method, data, name in tests:
        ok, result = test_endpoint(path, method, data)
        status = "✅" if ok else "❌"
        print(f"\n{status} {name}")
        if not ok:
            print(f"   Error: {result}")
            all_pass = False
        else:
            print(f"   OK: {str(result)[:100]}...")

    print("\n" + "=" * 50)
    if all_pass:
        print("🎉 All tests passed! Deployment successful.")
    else:
        print("⚠️ Some tests failed. Check deployment.")
    print("=" * 50)

    return 0 if all_pass else 1

if __name__ == "__main__":
    sys.exit(main())
