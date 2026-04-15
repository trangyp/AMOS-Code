"""AMOS Import Cost Auditor - Measures Import-Time Bottlenecks

Identifies exact slow imports and import cascade width.
Per Deep Debug Directive: Find exact slow line, exact blocking path.

Owner: AMOS Brain (Canonical Runtime)
Version: 1.0.0
"""

from __future__ import annotations

import sys
import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from types import ModuleType
from typing import Any, Optional


@dataclass
class ImportMeasurement:
    """Measurement of a single import operation."""
    
    module_name: str
    import_path: str
    duration_ms: float
    import_time: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    parent_module: str = ""
    import_depth: int = 0
    is_cold_import: bool = True  # First time import vs re-import
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "module_name": self.module_name,
            "import_path": self.import_path,
            "duration_ms": round(self.duration_ms, 2),
            "import_time": self.import_time,
            "parent_module": self.parent_module,
            "import_depth": self.import_depth,
            "is_cold_import": self.is_cold_import,
        }


@dataclass
class ImportCascade:
    """Represents an import cascade chain."""
    
    root_module: str
    total_duration_ms: float
    chain: list[ImportMeasurement] = field(default_factory=list)
    leaf_modules: list[str] = field(default_factory=list)
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "root_module": self.root_module,
            "total_duration_ms": round(self.total_duration_ms, 2),
            "chain_length": len(self.chain),
            "leaf_count": len(self.leaf_modules),
        }


class ImportCostAuditor:
    """Audits import-time costs and identifies bottlenecks.
    
    Measures:
    - Individual import durations
    - Import cascade width
    - Import chain depth
    - Cold vs hot imports
    
    Usage:
        auditor = ImportCostAuditor()
        auditor.install_hook()
        # ... run imports ...
        report = auditor.generate_report()
    """
    
    def __init__(self, track_cascades: bool = True):
        self.measurements: list[ImportMeasurement] = []
        self.cascades: dict[str, ImportCascade] = {}
        self.track_cascades = track_cascades
        self._original_import: Optional[callable] = None
        self._import_stack: list[str] = []
        self._module_times: dict[str, float] = {}
        self._is_installed = False
    
    def install_hook(self) -> None:
        """Install import hook to measure all imports."""
        if self._is_installed:
            return
        
        # Store original import
        self._original_import = __builtins__.__import__
        
        # Create instrumented import
        def instrumented_import(name, globals=None, locals=None, fromlist=(), level=0):
            start_time = time.perf_counter()
            module = None  # Initialize to avoid UnboundLocalError
            
            # Track cascade depth
            parent = self._import_stack[-1] if self._import_stack else ""
            self._import_stack.append(name)
            
            try:
                # Perform actual import
                module = self._original_import(name, globals, locals, fromlist, level)
            finally:
                end_time = time.perf_counter()
                duration_ms = (end_time - start_time) * 1000
                
                # Record measurement (even if import failed)
                import_path = getattr(module, '__file__', 'failed') if module else 'failed'
                measurement = ImportMeasurement(
                    module_name=name,
                    import_path=import_path,
                    duration_ms=duration_ms,
                    parent_module=parent,
                    import_depth=len(self._import_stack) - 1,
                    is_cold_import=name not in self._module_times,
                )
                self.measurements.append(measurement)
                self._module_times[name] = duration_ms
                
                # Pop from stack
                if self._import_stack and self._import_stack[-1] == name:
                    self._import_stack.pop()
            
            return module
        
        # Replace builtin import
        __builtins__.__import__ = instrumented_import
        self._is_installed = True
    
    def uninstall_hook(self) -> None:
        """Remove import hook and restore original."""
        if not self._is_installed or self._original_import is None:
            return
        
        __builtins__.__import__ = self._original_import
        self._is_installed = False
    
    def get_slowest_imports(self, n: int = 10) -> list[ImportMeasurement]:
        """Get the N slowest imports by duration."""
        return sorted(self.measurements, key=lambda m: m.duration_ms, reverse=True)[:n]
    
    def get_import_cascades(self, min_duration_ms: float = 50.0) -> list[ImportCascade]:
        """Identify import cascades that exceed threshold."""
        cascades = []
        
        # Group by parent chain
        cascade_roots: dict[str, list[ImportMeasurement]] = defaultdict(list)
        
        for measurement in self.measurements:
            if measurement.parent_module:
                cascade_roots[measurement.parent_module].append(measurement)
        
        # Build cascade objects for significant chains
        for root, chain in cascade_roots.items():
            total_duration = sum(m.duration_ms for m in chain)
            if total_duration >= min_duration_ms:
                cascades.append(ImportCascade(
                    root_module=root,
                    total_duration_ms=total_duration,
                    chain=chain,
                    leaf_modules=[m.module_name for m in chain],
                ))
        
        return sorted(cascades, key=lambda c: c.total_duration_ms, reverse=True)
    
    def get_import_summary(self) -> dict[str, Any]:
        """Get summary statistics of import measurements."""
        if not self.measurements:
            return {"total_imports": 0, "total_duration_ms": 0}
        
        total_duration = sum(m.duration_ms for m in self.measurements)
        cold_imports = [m for m in self.measurements if m.is_cold_import]
        
        return {
            "total_imports": len(self.measurements),
            "total_duration_ms": round(total_duration, 2),
            "cold_imports": len(cold_imports),
            "avg_duration_ms": round(total_duration / len(self.measurements), 2),
            "max_depth": max(m.import_depth for m in self.measurements) if self.measurements else 0,
            "slowest_module": self.get_slowest_imports(1)[0].module_name if self.measurements else "",
        }
    
    def generate_report(self, top_n: int = 20) -> dict[str, Any]:
        """Generate comprehensive import cost report."""
        summary = self.get_import_summary()
        slowest = [m.to_dict() for m in self.get_slowest_imports(top_n)]
        cascades = [c.to_dict() for c in self.get_import_cascades()]
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "summary": summary,
            "slowest_imports": slowest,
            "import_cascades": cascades,
            "audit_complete": True,
        }
    
    def find_blocking_imports(self, threshold_ms: float = 100.0) -> list[ImportMeasurement]:
        """Find imports that exceed blocking threshold."""
        return [m for m in self.measurements if m.duration_ms >= threshold_ms]
    
    def analyze_import_chain(self, target_module: str) -> Optional[ImportCascade]:
        """Analyze the import chain leading to a specific module."""
        # Find all imports that led to target
        chain = []
        current = target_module
        
        while current:
            measurement = next(
                (m for m in self.measurements if m.module_name == current),
                None
            )
            if measurement:
                chain.append(measurement)
                current = measurement.parent_module
            else:
                break
        
        if chain:
            chain.reverse()
            total_duration = sum(m.duration_ms for m in chain)
            return ImportCascade(
                root_module=chain[0].module_name if chain else "",
                total_duration_ms=total_duration,
                chain=chain,
                leaf_modules=[target_module],
            )
        
        return None


def main():
    """Run import cost audit on AMOS."""
    print("=" * 70)
    print("AMOS IMPORT COST AUDITOR")
    print("=" * 70)
    print()
    
    auditor = ImportCostAuditor()
    
    print("Installing import hook...")
    auditor.install_hook()
    print("✓ Import hook installed")
    
    print("\nTriggering AMOS imports...")
    start_time = time.time()
    
    # Import key AMOS modules
    try:
        import amos_brain
        print("✓ amos_brain imported")
    except ImportError as e:
        print(f"✗ amos_brain import failed: {e}")
    
    try:
        import amos_brain.reasoning
        print("✓ amos_brain.reasoning imported")
    except ImportError as e:
        print(f"✗ amos_brain.reasoning import failed: {e}")
    
    try:
        from repo_doctor.import_analyzer import ImportAnalyzer
        print("✓ repo_doctor.import_analyzer imported")
    except ImportError as e:
        print(f"✗ repo_doctor.import_analyzer import failed: {e}")
    
    total_import_time = (time.time() - start_time) * 1000
    
    print(f"\n✓ Imports completed in {total_import_time:.2f}ms")
    
    # Uninstall hook
    auditor.uninstall_hook()
    
    # Generate report
    report = auditor.generate_report(top_n=15)
    
    print("\n" + "=" * 70)
    print("IMPORT COST REPORT")
    print("=" * 70)
    
    summary = report["summary"]
    print(f"\nSummary:")
    print(f"  Total imports: {summary['total_imports']}")
    print(f"  Total duration: {summary['total_duration_ms']:.2f}ms")
    print(f"  Cold imports: {summary['cold_imports']}")
    print(f"  Average duration: {summary['avg_duration_ms']:.2f}ms")
    print(f"  Max depth: {summary['max_depth']}")
    
    print(f"\nTop 10 Slowest Imports:")
    for i, imp in enumerate(report["slowest_imports"][:10], 1):
        print(f"  {i:2d}. {imp['module_name'][:40]:40s} {imp['duration_ms']:8.2f}ms")
    
    # Find blocking imports
    blocking = auditor.find_blocking_imports(threshold_ms=50.0)
    if blocking:
        print(f"\n⚠️  Blocking Imports (>{50}ms):")
        for imp in blocking[:5]:
            print(f"    {imp.module_name[:40]:40s} {imp.duration_ms:8.2f}ms")
    
    print("\n" + "=" * 70)
    print("AUDIT COMPLETE")
    print("=" * 70)
    
    return report


if __name__ == "__main__":
    main()
