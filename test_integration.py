#!/usr/bin/env python3
"""
AMOS Integration Test Suite

Validates end-to-end connectivity between all layers:
- Backend API endpoints
- LLM providers (Ollama, OpenAI, Anthropic, Mock)
- WebSocket connections
- Frontend API compatibility

Usage:
    python test_integration.py

Creator: Trang Phan
Version: 3.0.0
"""

import asyncio
import sys
import json
from typing import Dict

# Test Configuration
API_BASE = "http://localhost:8000"
WS_URL = "ws://localhost:8000/ws/dashboard"


class Colors:
    """Terminal colors for output."""
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    RESET = "\033[0m"


def print_header(text: str):
    """Print section header."""
    print(f"\n{Colors.BLUE}{'=' * 60}{Colors.RESET}")
    print(f"{Colors.BLUE}{text}{Colors.RESET}")
    print(f"{Colors.BLUE}{'=' * 60}{Colors.RESET}")


def print_success(text: str):
    """Print success message."""
    print(f"{Colors.GREEN}✓ {text}{Colors.RESET}")


def print_error(text: str):
    """Print error message."""
    print(f"{Colors.RED}✗ {text}{Colors.RESET}")


def print_warning(text: str):
    """Print warning message."""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.RESET}")


class IntegrationTester:
    """Test AMOS integration end-to-end."""

    def __init__(self):
        self.results: Dict[str, bool] = {}
        self.errors: Dict[str, str] = {}

    async def test_backend_health(self) -> bool:
        """Test backend health endpoint."""
        try:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{API_BASE}/health") as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        print_success(f"Backend healthy: v{data.get('version', 'unknown')}")
                        return True
                    else:
                        print_error(f"Backend returned {resp.status}")
                        return False
        except Exception as e:
            print_error(f"Backend health check failed: {e}")
            return False

    async def test_api_llm_providers(self) -> bool:
        """Test LLM providers endpoint."""
        try:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{API_BASE}/api/v1/llm/providers") as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        providers = data.get('providers', [])
                        print_success(f"Found {len(providers)} LLM provider(s)")
                        for p in providers:
                            print(f"  - {p['name']}: {', '.join(p['models'][:3])}")
                        return True
                    else:
                        print_error(f"Providers endpoint returned {resp.status}")
                        return False
        except Exception as e:
            print_error(f"LLM providers test failed: {e}")
            return False

    async def test_api_chat_completion(self) -> bool:
        """Test chat completion with mock provider."""
        try:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                payload = {
                    "messages": [
                        {"role": "user", "content": "Hello AMOS!"}
                    ],
                    "model": "mock-gpt",
                    "provider": "mock"
                }
                async with session.post(
                    f"{API_BASE}/api/v1/llm/chat",
                    json=payload
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        print_success(f"Chat completion: {data['content'][:50]}...")
                        print(f"  Provider: {data['provider']}, Model: {data['model']}")
                        print(f"  Latency: {data['latency_ms']:.0f}ms")
                        return True
                    else:
                        error = await resp.text()
                        print_error(f"Chat endpoint returned {resp.status}: {error}")
                        return False
        except Exception as e:
            print_error(f"Chat completion test failed: {e}")
            return False

    async def test_api_agents(self) -> bool:
        """Test agent task endpoints."""
        try:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                # Create task
                payload = {
                    "name": "Test Task",
                    "description": "Integration test task",
                    "agent_type": "general",
                    "priority": "normal"
                }
                async with session.post(
                    f"{API_BASE}/api/v1/agents/tasks",
                    json=payload
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        task_id = data['id']
                        print_success(f"Created agent task: {task_id}")

                        # List tasks
                        async with session.get(f"{API_BASE}/api/v1/agents/tasks") as list_resp:
                            if list_resp.status == 200:
                                list_data = await list_resp.json()
                                print_success(f"Task list: {list_data['total']} total, {list_data['running']} running")
                                return True
                    else:
                        error = await resp.text()
                        print_error(f"Agents endpoint returned {resp.status}: {error}")
                        return False
        except Exception as e:
            print_error(f"Agent test failed: {e}")
            return False

    async def test_api_system(self) -> bool:
        """Test system status endpoint."""
        try:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{API_BASE}/api/v1/system/status") as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        print_success(f"System status: {data['status']}")
                        print(f"  Version: {data['version']}")
                        print(f"  Uptime: {data['uptime_seconds']:.0f}s")
                        print(f"  Providers: {len(data['providers'])}")
                        return True
                    else:
                        print_error(f"System endpoint returned {resp.status}")
                        return False
        except Exception as e:
            print_error(f"System test failed: {e}")
            return False

    async def test_websocket(self) -> bool:
        """Test WebSocket connection."""
        try:
            import websockets
            async with websockets.connect(WS_URL) as ws:
                # Wait for connection confirmation
                response = await asyncio.wait_for(ws.recv(), timeout=5.0)
                data = json.loads(response)

                if data.get('type') == 'connection':
                    print_success(f"WebSocket connected: {data.get('channel')}")

                    # Send ping
                    await ws.send(json.dumps({"type": "ping"}))
                    pong = await asyncio.wait_for(ws.recv(), timeout=5.0)
                    pong_data = json.loads(pong)

                    if pong_data.get('type') == 'pong':
                        print_success("WebSocket ping/pong successful")
                        return True

                print_error("Unexpected WebSocket response")
                return False
        except ImportError:
            print_warning("websockets library not installed, skipping WebSocket test")
            print("  Install with: pip install websockets")
            return True  # Don't fail if optional dependency missing
        except Exception as e:
            print_error(f"WebSocket test failed: {e}")
            return False

    async def run_all_tests(self):
        """Run all integration tests."""
        print_header("AMOS v3.0.0 Integration Test Suite")

        tests = [
            ("Backend Health", self.test_backend_health),
            ("LLM Providers", self.test_api_llm_providers),
            ("Chat Completion", self.test_api_chat_completion),
            ("Agent Tasks", self.test_api_agents),
            ("System Status", self.test_api_system),
            ("WebSocket", self.test_websocket),
        ]

        for name, test_func in tests:
            print(f"\n  Testing: {name}...")
            try:
                result = await test_func()
                self.results[name] = result
            except Exception as e:
                print_error(f"Test crashed: {e}")
                self.results[name] = False
                self.errors[name] = str(e)

        # Print summary
        self.print_summary()

    def print_summary(self):
        """Print test summary."""
        print_header("Test Summary")

        passed = sum(1 for v in self.results.values() if v)
        total = len(self.results)

        for name, result in self.results.items():
            status = f"{Colors.GREEN}PASS{Colors.RESET}" if result else f"{Colors.RED}FAIL{Colors.RESET}"
            print(f"  {status} - {name}")

        print(f"\n{Colors.BLUE}Results: {passed}/{total} tests passed{Colors.RESET}")

        if passed == total:
            print(f"\n{Colors.GREEN}✓ All integration tests passed!{Colors.RESET}")
            print(f"{Colors.GREEN}✓ AMOS v3.0.0 is ready for deployment.{Colors.RESET}")
        else:
            print(f"\n{Colors.RED}✗ Some tests failed. Check errors above.{Colors.RESET}")
            if self.errors:
                print(f"\n{Colors.YELLOW}Errors:{Colors.RESET}")
                for name, error in self.errors.items():
                    print(f"  {name}: {error}")

        return passed == total


def main():
    """Main entry point."""
    print(f"{Colors.BLUE}AMOS Integration Tester{Colors.RESET}")
    print(f"API Base: {API_BASE}")
    print(f"WebSocket: {WS_URL}")

    tester = IntegrationTester()

    try:
        result = asyncio.run(tester.run_all_tests())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user.")
        sys.exit(130)


if __name__ == "__main__":
    main()
