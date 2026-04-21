#!/usr/bin/env python3
"""
OpenClaw Execution Bridge - REAL AMOS Integration
==================================================

Canonical execution bridge connecting AMOS Brain to OpenClaw.
This is a GOVERNED execution capability - NOT a parallel brain.

LAW 3 COMPLIANCE: OpenClaw is NOT a separate runtime.
- Invoked through canonical AMOS Kernel → Router → ActionGate
- Governed by AMOS policies and tool registry
- No independent persistence, memory, or process rights
"""

from __future__ import annotations

import json
import logging
import subprocess
import os
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
from typing import Any

# Configure logging
logger = logging.getLogger(__name__)


class OpenClawExecutionBridge:
    """Real OpenClaw execution bridge for AMOS brain.
    
    This bridge provides governed access to OpenClaw capabilities
    through the canonical AMOS execution path.
    """
    
    def __init__(self, openclaw_path: str | None = None) -> None:
        self.openclaw_path = openclaw_path or self._find_openclaw_executable()
        self._version: str | None = None
        self._is_verified = False
        
        if self.openclaw_path:
            self._verify_installation()
    
    def _find_openclaw_executable(self) -> str | None:
        """Find the real OpenClaw executable."""
        # Check PATH first
        try:
            result = subprocess.run(
                ["which", "openclaw"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                path = result.stdout.strip()
                logger.info(f"Found OpenClaw at: {path}")
                return path
        except Exception as e:
            logger.debug(f"which openclaw failed: {e}")
        
        # Check NVM common paths
        nvm_paths = [
            Path.home() / ".nvm" / "versions" / "node" / "v22.22.2" / "bin" / "openclaw",
            Path.home() / ".nvm" / "versions" / "node" / "v22.12.0" / "bin" / "openclaw",
            Path.home() / ".local" / "bin" / "openclaw",
            Path("/usr/local/bin/openclaw"),
        ]
        
        for path in nvm_paths:
            if path.exists():
                logger.info(f"Found OpenClaw at: {path}")
                return str(path)
        
        logger.error("OpenClaw executable not found")
        return None
    
    def _verify_installation(self) -> bool:
        """Verify OpenClaw is really installed and working."""
        if not self.openclaw_path:
            return False
            
        try:
            result = subprocess.run(
                [self.openclaw_path, "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                self._version = result.stdout.strip()
                self._is_verified = True
                logger.info(f"OpenClaw verified: {self._version}")
                return True
        except Exception as e:
            logger.error(f"OpenClaw verification failed: {e}")
        
        return False
    
    @property
    def is_installed(self) -> bool:
        """Check if OpenClaw is installed and verified."""
        return self._is_verified and self.openclaw_path is not None
    
    @property
    def version(self) -> str | None:
        """Get OpenClaw version."""
        return self._version
    
    def execute_command(
        self,
        command: str,
        args: list[str] | None = None,
        timeout: int = 30,
        capture_output: bool = True
    ) -> dict[str, Any]:
        """Execute an OpenClaw command through the governed bridge."""
        if not self.is_installed:
            return {
                "success": False,
                "error": "OpenClaw not installed or not verified",
                "command": command,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        
        cmd = [self.openclaw_path, command] + (args or [])
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=capture_output,
                text=True,
                timeout=timeout
            )
            
            return {
                "success": result.returncode == 0,
                "returncode": result.returncode,
                "stdout": result.stdout if capture_output else None,
                "stderr": result.stderr if capture_output else None,
                "command": command,
                "args": args,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": f"Command timed out after {timeout}s",
                "command": command,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "command": command,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    def get_health(self) -> dict[str, Any]:
        """Get OpenClaw health status."""
        if not self.is_installed:
            return {
                "status": "not_installed",
                "installed": False,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        
        result = self.execute_command("doctor", timeout=15)
        
        return {
            "status": "healthy" if result["success"] else "unhealthy",
            "installed": True,
            "version": self._version,
            "executable": self.openclaw_path,
            "doctor_output": result.get("stdout"),
            "doctor_error": result.get("stderr"),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    def run_agent(self, message: str, target: str | None = None) -> dict[str, Any]:
        """Run OpenClaw agent with a message."""
        args = ["--message", message]
        if target:
            args.extend(["--to", target])
        args.append("--json")
        
        return self.execute_command("agent", args, timeout=60)
    
    def search_docs(self, query: str) -> dict[str, Any]:
        """Search OpenClaw documentation."""
        return self.execute_command("docs", [query], timeout=15)


@lru_cache(maxsize=1)
def get_openclaw_bridge() -> OpenClawExecutionBridge:
    """Get the canonical OpenClaw execution bridge singleton."""
    return OpenClawExecutionBridge()


def amos_openclaw_health() -> dict[str, Any]:
    """AMOS OpenClaw health check - governed interface."""
    bridge = get_openclaw_bridge()
    return bridge.get_health()


def amos_openclaw_execute(command: str, args: list[str] | None = None) -> dict[str, Any]:
    """AMOS-governed OpenClaw execution."""
    bridge = get_openclaw_bridge()
    return bridge.execute_command(command, args)


if __name__ == "__main__":
    print("=" * 60)
    print("OpenClaw Execution Bridge - Real Installation Verification")
    print("=" * 60)
    
    bridge = get_openclaw_bridge()
    
    print(f"\n📍 Executable Path: {bridge.openclaw_path}")
    print(f"✅ Verified: {bridge.is_installed}")
    print(f"📦 Version: {bridge.version}")
    
    if bridge.is_installed:
        print("\n🏥 Health Check:")
        health = bridge.get_health()
        print(f"   Status: {health['status']}")
        print(f"   Version: {health.get('version')}")
        
        print("\n🧪 Test Command (version):")
        test_result = bridge.execute_command("--version")
        print(f"   Success: {test_result['success']}")
        if test_result.get("stdout"):
            print(f"   Output: {test_result['stdout']}")
    else:
        print("\n❌ OpenClaw not properly installed!")
        print("   Run: npm install -g openclaw@latest")
