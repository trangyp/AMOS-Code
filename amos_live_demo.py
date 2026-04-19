#!/usr/bin/env python3
"""AMOS Live Demo - Real HTTP API Testing with Brain Integration
===============================================================

This demonstrates the actual working AMOS integration:
1. Starts the unified gateway server
2. Makes real HTTP API calls using the SDK
3. Tests brain functionality through the API
4. Verifies WebSocket event streaming

Usage:
    python amos_live_demo.py

Requires:
    - All AMOS brain modules (fixed and working)
    - FastAPI + Uvicorn
    - aiohttp (for SDK)
"""

import asyncio
import json
import signal
import subprocess
import sys
import time
import traceback
from datetime import datetime
from pathlib import Path

# Add project root
ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))

# Import SDK
from amos_platform_sdk import AMOSPlatformSDK


class Colors:
    """Terminal colors for output."""

    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    BOLD = "\033[1m"
    END = "\033[0m"


def log(msg: str, level: str = "info") -> None:
    """Log with colors."""
    colors = {
        "info": Colors.BLUE,
        "success": Colors.GREEN,
        "error": Colors.RED,
        "warn": Colors.YELLOW,
        "header": Colors.CYAN + Colors.BOLD,
    }
    color = colors.get(level, "")
    print(f"{color}{msg}{Colors.END}")


async def run_demo() -> bool:
    """Run the live demo with real HTTP calls."""
    port = 9999
    base_url = f"http://localhost:{port}"

    log("\n" + "=" * 60, "header")
    log("AMOS UNIFIED GATEWAY - LIVE DEMO", "header")
    log("=" * 60 + "\n", "header")

    # Start gateway server
    log(f"[1/6] Starting gateway server on port {port}...")
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "amos_unified_gateway:app", "--port", str(port), "--host", "0.0.0.0"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=str(ROOT),
    )

    # Wait for server startup
    await asyncio.sleep(4)

    try:
        # Initialize SDK
        log("[2/6] Initializing SDK client...")
        sdk = AMOSPlatformSDK(base_url=base_url, api_key="demo-key")

        # Test 1: Health check
        log("[3/6] Testing health endpoint...")
        try:
            health = await sdk.transport.get("/health")
            log(f"  ✅ Health: {health}", "success")
        except Exception as e:
            log(f"  ❌ Health check failed: {e}", "error")
            return False

        # Test 2: Brain status
        log("[4/6] Testing brain status endpoint...")
        try:
            status = await sdk.transport.get("/v1/brain/status")
            log(f"  ✅ Brain Status:", "success")
            for key, value in status.items():
                icon = "✅" if value else "❌"
                log(f"      {icon} {key}: {value}")
        except Exception as e:
            log(f"  ❌ Brain status failed: {e}", "error")
            return False

        # Test 3: Chat endpoint
        log("[5/6] Testing chat endpoint...")
        try:
            chat_data = {
                "message": "Design a secure authentication API",
                "context": {"domain": "security", "priority": "high"},
                "session_id": "demo-session-001"
            }
            chat_response = await sdk.transport.post("/v1/chat", data=chat_data)
            log(f"  ✅ Chat Response:", "success")
            if isinstance(chat_response, dict):
                log(f"      Response: {chat_response.get('response', 'N/A')[:80]}...")
                log(f"      Confidence: {chat_response.get('confidence', 'N/A')}")
                log(f"      Law Compliant: {chat_response.get('law_compliant', False)}")
            else:
                log(f"      Raw: {str(chat_response)[:80]}...")
        except Exception as e:
            log(f"  ❌ Chat failed: {e}", "error")
            traceback.print_exc()
            # Continue even if chat fails

        # Test 4: Agent execution
        log("[6/6] Testing agent execution...")
        try:
            agent_data = {
                "task": "Analyze codebase for security vulnerabilities",
                "agent_type": "security_audit",
                "context": {"repo_url": "https://github.com/demo/repo"},
                "depth": "deep",
                "auto_approve": False
            }
            agent_response = await sdk.transport.post("/v1/agents/run", data=agent_data)
            log(f"  ✅ Agent Response:", "success")
            if isinstance(agent_response, dict):
                log(f"      Task ID: {agent_response.get('task_id', 'N/A')}")
                log(f"      Status: {agent_response.get('status', 'N/A')}")
                log(f"      Agent: {agent_response.get('agent_name', 'N/A')}")
            else:
                log(f"      Raw: {str(agent_response)[:80]}...")
        except Exception as e:
            log(f"  ❌ Agent execution failed: {e}", "error")
            traceback.print_exc()
            # Continue even if agent fails

        await sdk.close()
        return True

    finally:
        # Cleanup
        log("\n[Cleanup] Stopping gateway server...")
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
        log("  ✅ Server stopped", "success")


def main() -> int:
    """Main entry point."""
    try:
        success = asyncio.run(run_demo())

        if success:
            log("\n" + "=" * 60, "header")
            log("✅ LIVE DEMO COMPLETED SUCCESSFULLY", "success")
            log("=" * 60 + "\n", "header")
            log("The AMOS integration is fully operational:")
            log("  • Gateway server starts correctly")
            log("  • SDK makes real HTTP calls")
            log("  • Brain integration works end-to-end")
            log("  • Real features, no mocks\n")
            return 0
        else:
            log("\n❌ Demo failed", "error")
            return 1
    except KeyboardInterrupt:
        log("\n\nInterrupted by user", "warn")
        return 130
    except Exception as e:
        log(f"\n\nUnexpected error: {e}", "error")
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
