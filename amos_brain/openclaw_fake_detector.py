#!/usr/bin/env python3
"""
OpenClaw Fake Build Detector
============================

Detects and prevents fake OpenClaw installations.
Implements guards against mock wrappers and install theater.
"""

from __future__ import annotations

import ast
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class OpenClawFakeDetector:
    """Detects fake OpenClaw build artifacts and prevents install theater."""
    
    FAKE_INDICATORS = [
        "if True: pass",
        "if True:\n    pass",
        "# REMOVED: fake",
        "# FAKE:",
        "# MOCK:",
        "NotImplementedError",
        "TODO: implement",
        "FIXME: implement",
        "pass  # placeholder",
        "return None  # TODO",
    ]
    
    FAKE_PATTERNS = [
        "*openclaw*fake*.py",
        "*openclaw*mock*.py",
        "*openclaw*adapter*.py",
        "*fake*openclaw*.py",
        "*mock*openclaw*.py",
    ]
    
    def __init__(self, amos_root: Path | None = None) -> None:
        self.amos_root = amos_root or Path(__file__).parent.parent
        self.detected_fakes: list[dict[str, Any]] = []
    
    def scan_for_fake_artifacts(self) -> list[dict[str, Any]]:
        """Scan codebase for fake OpenClaw artifacts."""
        self.detected_fakes = []
        
        # Scan Python files for fake indicators
        for py_file in self.amos_root.rglob("*.py"):
            # Skip the real bridge and detector
            if "openclaw_execution_bridge.py" in str(py_file):
                continue
            if "openclaw_fake_detector.py" in str(py_file):
                continue
            
            try:
                content = py_file.read_text(encoding="utf-8")
                
                # Check for fake indicators
                for indicator in self.FAKE_INDICATORS:
                    if indicator in content:
                        self.detected_fakes.append({
                            "file": str(py_file.relative_to(self.amos_root)),
                            "type": "fake_indicator",
                            "indicator": indicator,
                            "severity": "high"
                        })
                        break
                
                # Try to parse and detect empty stubs
                try:
                    tree = ast.parse(content)
                    for node in ast.walk(tree):
                        if isinstance(node, ast.FunctionDef):
                            # Check if function body is just pass/None
                            if len(node.body) == 1:
                                stmt = node.body[0]
                                if isinstance(stmt, ast.Pass):
                                    self.detected_fakes.append({
                                        "file": str(py_file.relative_to(self.amos_root)),
                                        "type": "empty_function",
                                        "function": node.name,
                                        "line": node.lineno,
                                        "severity": "medium"
                                    })
                except SyntaxError:
                    pass  # Corrupted file - already caught by indicators
                    
            except Exception as e:
                logger.debug(f"Could not read {py_file}: {e}")
        
        return self.detected_fakes
    
    def verify_real_installation_exists(self) -> dict[str, Any]:
        """Verify real OpenClaw installation exists."""
        from amos_brain.openclaw_execution_bridge import get_openclaw_bridge
        
        bridge = get_openclaw_bridge()
        
        return {
            "real_executable_exists": bridge.is_installed,
            "executable_path": bridge.openclaw_path,
            "version": bridge.version,
            "has_real_installation": bridge.is_installed and bridge.version is not None
        }
    
    def generate_report(self) -> dict[str, Any]:
        """Generate fake detection report."""
        fakes = self.scan_for_fake_artifacts()
        install_check = self.verify_real_installation_exists()
        
        return {
            "fake_artifacts_found": len(fakes) > 0,
            "fake_count": len(fakes),
            "fakes": fakes[:10],  # Limit to first 10
            "real_installation": install_check,
            "system_status": (
                "CLEAN" if not fakes and install_check["has_real_installation"]
                else "FAKES_DETECTED" if fakes
                else "NO_REAL_INSTALL"
            )
        }


def detect_openclaw_fakes() -> dict[str, Any]:
    """AMOS OpenClaw fake detection entry point."""
    detector = OpenClawFakeDetector()
    return detector.generate_report()


if __name__ == "__main__":
    print("=" * 60)
    print("OpenClaw Fake Build Detector")
    print("=" * 60)
    
    report = detect_openclaw_fakes()
    
    print(f"\n🔍 System Status: {report['system_status']}")
    print(f"\n📦 Real Installation: {report['real_installation']['has_real_installation']}")
    if report['real_installation']['version']:
        print(f"   Version: {report['real_installation']['version']}")
    
    print(f"\n🚨 Fake Artifacts: {report['fake_count']}")
    for fake in report['fakes']:
        print(f"   - {fake['file']}: {fake['type']} ({fake.get('indicator', 'N/A')})")
    
    if report['system_status'] == "CLEAN":
        print("\n✅ System is clean - real OpenClaw installation verified")
    else:
        print("\n⚠️ Issues detected - review required")
