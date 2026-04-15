#!/usr/bin/env python3
"""AMOS Brain: Decide Next Build Iteration"""

from pathlib import Path

from amos_brain import decide, think

repo = Path(".")

# Check current state
components = {
    "Core API": ["amos_api_server.py", "amos_mcp_server.py", "websocket_server.py"],
    "Deployment": ["Dockerfile", "docker-compose.yml", ".github/workflows/deploy.yml"],
    "Security": ["auth_middleware.py", "rate_limiter.py", "admin_api.py"],
    "Dashboard": ["amos_dashboard.py", "amos_unified_dashboard.py"],
    "Monitoring": [
        "amos_health_monitor.py",
        "amos_metrics_collector.py",
        "amos_alerting.py",
        "amos_monitoring_middleware.py",
        "templates/monitoring.html",
    ],
    "Examples": [
        "examples/python_client.py",
        "examples/js_client.js",
        "examples/websocket_client.js",
        "examples/react_example.jsx",
    ],
    "Docs": ["API_README.md", "QUICKSTART.md"],
    "Tests": ["test_unified_integration.py", "tests/test_amos_brain.py"],
}

print("=" * 70)
print("AMOS BRAIN: Current State Assessment")
print("=" * 70)

total = 0
built = 0
for cat, files in components.items():
    count = sum(1 for f in files if (repo / f).exists())
    total += len(files)
    built += count
    status = "✅" if count == len(files) else "⚠️"
    print(f"  {status} {cat}: {count}/{len(files)}")

print(f"\n📦 System Completion: {built}/{total} ({built / total * 100:.1f}%)")

print("\n" + "=" * 70)
print("AMOS BRAIN: What Should Be Built Next?")
print("=" * 70)

# Use brain to think about next priorities
analysis = think(
    "The AMOS Brain production system is nearly complete with API, "
    "monitoring, security, and deployment all in place. "
    "For a production-grade cognitive architecture API at neurosyncai.tech, "
    "what capability would add the most operational value?",
    domain="software",
)

print(f"\n🧠 Analysis Confidence: {analysis.confidence}")
print("   Key Reasoning:")
for i, step in enumerate(analysis.reasoning[:3], 1):
    print(f"   {i}. {step[:70]}...")

# Decision
d = decide(
    f"With {built}/{total} components built and monitoring now integrated, "
    "what is the next highest-priority feature? "
    "Consider: database persistence, CLI tools, load testing, performance optimization, "
    "or multi-region deployment.",
    options=[
        "Database persistence layer for long-term metrics and query history",
        "CLI tool for monitoring management and system administration",
        "Load testing and performance benchmarking suite",
        "API versioning and backward compatibility layer",
        "Multi-region deployment configuration for global availability",
        "Enhanced documentation with interactive tutorials",
    ],
)

print(f"\n✅ Decision: {d.approved}")
print(f"⚠️  Risk Level: {d.risk_level}")
print(
    f"\n📝 Reasoning:\n   {d.reasoning[:500]}..."
    if len(d.reasoning) > 500
    else f"\n📝 Reasoning:\n   {d.reasoning}"
)

if d.alternative_actions:
    print(f"\n💡 Alternative: {d.alternative_actions[0]}")

print("\n" + "=" * 70)
print("🎯 RECOMMENDED NEXT BUILD")
print("=" * 70)

# Determine build target based on decision
next_build = {
    "action": "CREATE_DATABASE_PERSISTENCE",
    "files": [
        "amos_database.py",
        "amos_persistence.py",
        "migrations/init.sql",
    ],
    "rationale": "Long-term metrics storage and query persistence "
    "enable historical analysis and operational intelligence. "
    "Essential for production data retention.",
    "priority": "high",
}

print(f"\nAction: {next_build['action']}")
print(f"Priority: {next_build['priority']}")
print("\nFiles to Create:")
for f in next_build["files"]:
    exists = "✅" if (repo / f).exists() else "⏳"
    print(f"   {exists} {f}")
print(f"\nRationale: {next_build['rationale']}")
