#!/usr/bin/env python3
"""AMOS Brain Performance Profiling Suite
=====================================

State-of-the-art profiling using py-spy and memray.
Establishes performance baselines for critical paths.

Usage:
    python profiling_suite.py --cpu      # CPU profiling with py-spy
    python profiling_suite.py --memory   # Memory profiling with memray
    python profiling_suite.py --full     # Both CPU and memory
    python profiling_suite.py --test     # Run test suite with profiling
"""

import argparse
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional


class ProfilerConfig:
    """Configuration for profiling runs."""

    # Test targets for profiling
    TEST_TARGETS = [
        "tests/test_model_backends.py",
        "tests/test_coherence_bridge.py",
        "tests/test_orchestrator_integration.py",
        "tests/test_full_integration.py",
    ]

    # Output directories
    PROFILE_DIR = Path("profiling_results")
    CPU_DIR = PROFILE_DIR / "cpu"
    MEMORY_DIR = PROFILE_DIR / "memory"

    @classmethod
    def ensure_dirs(cls) -> None:
        """Create profiling output directories."""
        cls.PROFILE_DIR.mkdir(exist_ok=True)
        cls.CPU_DIR.mkdir(exist_ok=True)
        cls.MEMORY_DIR.mkdir(exist_ok=True)


class CPProfiler:
    """CPU profiling using py-spy."""

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.check_pyspy()

    def check_pyspy(self) -> bool:
        """Check if py-spy is installed."""
        try:
            subprocess.run(["py-spy", "--version"], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("⚠️  py-spy not found. Install with: pip install py-spy")
            return False

    def profile_test(self, test_file: str, duration: int = 30) -> Optional[Path]:
        """Profile a test file execution."""
        test_path = Path(test_file)
        if not test_path.exists():
            print(f"❌ Test file not found: {test_file}")
            return None

        output_file = self.output_dir / f"{test_path.stem}_cpu.svg"

        print(f"\n🔥 CPU Profiling: {test_file}")
        print(f"   Duration: {duration}s | Output: {output_file}")

        # Build py-spy command
        cmd = [
            "py-spy",
            "record",
            "-o",
            str(output_file),
            "--duration",
            str(duration),
            "--rate",
            "100",  # 100 samples/second
            "--",
            sys.executable,
            str(test_path),
        ]

        try:
            start_time = time.time()
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=duration + 10,  # Buffer for startup
            )
            elapsed = time.time() - start_time

            if result.returncode == 0:
                print(f"   ✅ Complete in {elapsed:.1f}s")
                print(f"   📊 Flamegraph: {output_file}")
                return output_file
            else:
                print(f"   ⚠️  Exit code: {result.returncode}")
                if result.stderr:
                    print(f"   Error: {result.stderr[:200]}")
                return None

        except subprocess.TimeoutExpired:
            print(f"   ⏱️  Timeout after {duration + 10}s")
            return None
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return None

    def profile_all(self, duration: int = 30) -> list[Path]:
        """Profile all test targets."""
        results = []
        for test_file in ProfilerConfig.TEST_TARGETS:
            result = self.profile_test(test_file, duration)
            if result:
                results.append(result)
        return results


class MemoryProfiler:
    """Memory profiling using memray."""

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.check_memray()

    def check_memray(self) -> bool:
        """Check if memray is installed."""
        try:
            subprocess.run(
                ["python3", "-m", "memray", "--version"], capture_output=True, check=True
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("⚠️  memray not found. Install with: pip install memray")
            return False

    def profile_test(self, test_file: str) -> Optional[Path]:
        """Profile memory usage of a test file."""
        test_path = Path(test_file)
        if not test_path.exists():
            print(f"❌ Test file not found: {test_file}")
            return None

        bin_file = self.output_dir / f"{test_path.stem}_memory.bin"
        html_file = self.output_dir / f"{test_path.stem}_memory.html"

        print(f"\n💾 Memory Profiling: {test_file}")
        print(f"   Output: {bin_file}")

        # Run memray
        cmd = [sys.executable, "-m", "memray", "run", "--output", str(bin_file), str(test_path)]

        try:
            start_time = time.time()
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            elapsed = time.time() - start_time

            if result.returncode == 0:
                print(f"   ✅ Complete in {elapsed:.1f}s")

                # Generate flamegraph
                self._generate_flamegraph(bin_file, html_file)
                return bin_file
            else:
                print(f"   ⚠️  Exit code: {result.returncode}")
                if result.stderr:
                    print(f"   Stderr: {result.stderr[:500]}")
                return None

        except subprocess.TimeoutExpired:
            print("   ⏱️  Timeout after 60s - test may be too slow")
            return None
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return None

    def _generate_flamegraph(self, bin_file: Path, html_file: Path) -> None:
        """Generate HTML flamegraph from memray binary."""
        cmd = [
            sys.executable,
            "-m",
            "memray",
            "flamegraph",
            str(bin_file),
            "-o",
            str(html_file),
            "--temporal",
        ]

        try:
            subprocess.run(cmd, capture_output=True, timeout=30)
            if html_file.exists():
                print(f"   📊 Flamegraph: {html_file}")
        except Exception:
            pass  # Flamegraph generation is optional

    def profile_all(self) -> list[Path]:
        """Profile memory for all test targets."""
        results = []
        for test_file in ProfilerConfig.TEST_TARGETS:
            result = self.profile_test(test_file)
            if result:
                results.append(result)
        return results


class BaselineReport:
    """Generate performance baseline reports."""

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.results_file = output_dir / "baseline_report.md"

    def generate(self, cpu_results: list[Path], memory_results: list[Path]) -> None:
        """Generate markdown report."""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

        report = f"""# AMOS Brain Performance Baseline Report

**Generated:** {timestamp}
**Python:** {sys.version.split()[0]}
**Platform:** {sys.platform}

## CPU Profiling Results (py-spy)

| Test File | Flamegraph |
|-----------|------------|
"""
        for result in cpu_results:
            report += f"| {result.stem} | [{result.name}]({result}) |\n"

        report += """
## Memory Profiling Results (memray)

| Test File | Binary | Flamegraph |
|-----------|--------|------------|
"""
        for result in memory_results:
            html_file = result.with_suffix(".html")
            report += (
                f"| {result.stem} | [{result.name}]({result}) | [{html_file.name}]({html_file}) |\n"
            )

        report += """
## Analysis Notes

- CPU profiles show hot paths and function call frequency
- Memory profiles track heap allocations over time
- Run `py-spy top --pid <PID>` for live monitoring
- Run `memray live <PID>` for live memory tracking

## Next Steps

1. Compare future runs against this baseline
2. Investigate functions with >10% CPU time
3. Monitor memory growth patterns
4. Set up CI to fail on significant regressions

---
*Generated by AMOS Brain Profiling Suite*
"""

        self.results_file.write_text(report)
        print(f"\n📝 Baseline report: {self.results_file}")


def install_profiling_tools() -> None:
    """Install profiling dependencies."""
    print("\n📦 Installing profiling tools...")
    tools = ["py-spy", "memray", "icecream", "rich"]

    for tool in tools:
        print(f"   Installing {tool}...")
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "-q", tool],
                capture_output=True,
                check=True,
            )
            print(f"   ✅ {tool}")
        except subprocess.CalledProcessError:
            print(f"   ⚠️  {tool} install failed")


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="AMOS Brain Performance Profiling Suite")
    parser.add_argument("--cpu", action="store_true", help="Run CPU profiling with py-spy")
    parser.add_argument("--memory", action="store_true", help="Run memory profiling with memray")
    parser.add_argument("--full", action="store_true", help="Run both CPU and memory profiling")
    parser.add_argument("--test", action="store_true", help="Run test suite with profiling")
    parser.add_argument("--install", action="store_true", help="Install profiling tools")
    parser.add_argument(
        "--duration", type=int, default=30, help="Profiling duration in seconds (default: 30)"
    )

    args = parser.parse_args()

    if args.install:
        install_profiling_tools()
        return 0

    # Default to full profiling if no args
    if not any([args.cpu, args.memory, args.full, args.test, args.install]):
        args.full = True

    ProfilerConfig.ensure_dirs()

    print("=" * 60)
    print("AMOS BRAIN PERFORMANCE PROFILING SUITE")
    print("=" * 60)

    cpu_results = []
    memory_results = []

    if args.cpu or args.full:
        cpu_profiler = CPProfiler(ProfilerConfig.CPU_DIR)
        if cpu_profiler.check_pyspy():
            cpu_results = cpu_profiler.profile_all(args.duration)

    if args.memory or args.full:
        mem_profiler = MemoryProfiler(ProfilerConfig.MEMORY_DIR)
        if mem_profiler.check_memray():
            memory_results = mem_profiler.profile_all()

    if args.test:
        print("\n🧪 Running test suite with profiling...")
        # This would run tests with both profilers attached

    # Generate baseline report
    if cpu_results or memory_results:
        report = BaselineReport(ProfilerConfig.PROFILE_DIR)
        report.generate(cpu_results, memory_results)

    print("\n" + "=" * 60)
    print("PROFILING COMPLETE")
    print("=" * 60)
    print(f"\nResults in: {ProfilerConfig.PROFILE_DIR}")
    print("\nNext steps:")
    print("  - Open SVG flamegraphs in browser to analyze")
    print("  - Compare future runs against this baseline")
    print("  - Set up CI integration for regression detection")

    return 0


if __name__ == "__main__":
    sys.exit(main())
