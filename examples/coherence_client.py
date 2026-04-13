#!/usr/bin/env python3
"""AMOS Coherence Engine Client Example

Demonstrates using the /coherence endpoint for human coherence induction.

Usage:
    python coherence_client.py
"""

import requests
import json

API_BASE = "https://neurosyncai.tech"
# API_BASE = "http://localhost:5000"  # For local testing


def coherence_analysis(message: str) -> dict:
    """Send message to coherence engine."""
    response = requests.post(
        f"{API_BASE}/coherence",
        json={"message": message},
        headers={"Content-Type": "application/json"}
    )
    return response.json()


def main():
    print("=" * 70)
    print("AMOS COHERENCE ENGINE - CLIENT DEMO")
    print("=" * 70)
    print(f"API: {API_BASE}/coherence\n")
    
    # Example messages showing different states
    examples = [
        "I can't do this, it's impossible.",
        "I'm always failing at everything.",
        "I feel overwhelmed and can't think clearly.",
        "Maybe I should just give up.",
        "I want to understand why I keep procrastinating.",
    ]
    
    for message in examples:
        print(f"\n📝 Input: {message}")
        print("-" * 70)
        
        try:
            result = coherence_analysis(message)
            
            if result.get('success'):
                print(f"🔍 Detected State: {result['state']}")
                print(f"🎯 Intervention: {result['intervention']}")
                print(f"📡 Signal: {result['signal']}")
                print(f"💪 Capacity: {result['capacity']:.2f}")
                print(f"🔆 Clarity: {result['clarity']:.2f}")
                print(f"✅ Response: {result['response']}")
                print(f"🛡️  Safety: {result['safety_maintained']}")
            else:
                print(f"❌ Error: {result.get('error')}")
                
        except Exception as e:
            print(f"❌ Request failed: {e}")
        
        print("=" * 70)


if __name__ == "__main__":
    main()
