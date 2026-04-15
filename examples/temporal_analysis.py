#!/usr/bin/env python3
"""Temporal analysis example - tracks repository evolution."""

from repo_doctor_omega.temporal import DriftTracker


def main():
    """Analyze repository drift over time."""
    print("=" * 60)
    print("TEMPORAL ANALYSIS EXAMPLE")
    print("=" * 60)

    # Initialize tracker
    tracker = DriftTracker(".")
    print(f"\nRepository: {tracker.substrate.repo_path}")

    # Analyze drift
    print("\nAnalyzing last 50 commits...")
    report = tracker.analyze_drift(commits=50, threshold=0.3)

    print(f"\n{'=' * 60}")
    print("DRIFT REPORT")
    print(f"{'=' * 60}")
    print(f"Total Drift: {report.total_drift:.2f}")
    print(f"Energy Trend: {report.energy_trend:+.2f}")

    # Show trends
    if report.trends:
        print("\nSubsystem Trends:")
        degrading = [t for t in report.trends if t.trend_direction == "degrading"]
        improving = [t for t in report.trends if t.trend_direction == "improving"]

        if degrading:
            print("\n  Degrading:")
            for trend in degrading[:5]:
                print(f"    ⚠ {trend.subsystem}: slope={trend.slope:+.3f}")

        if improving:
            print("\n  Improving:")
            for trend in improving[:5]:
                print(f"    ✓ {trend.subsystem}: slope={trend.slope:+.3f}")

    # Destabilizing commits
    if report.destabilizing_commits:
        print("\n  Destabilizing Commits:")
        for commit, drift in report.destabilizing_commits[:5]:
            print(f"    {commit[:8]}: drift={drift:.2f}")
    else:
        print("\n  No destabilizing commits found")

    # Stability prediction
    print("\n" + "=" * 60)
    print("STABILITY PREDICTION (next 10 commits)")
    print("=" * 60)
    predictions = tracker.predict_stability(horizon=10)

    for subsystem, predicted in list(predictions.items())[:5]:
        current = tracker.get_drift_timeseries(subsystem, commits=1)
        current_val = current[0][1] if current else 1.0
        change = predicted - current_val
        direction = "↓" if change < 0 else "↑" if change > 0 else "→"
        print(f"  {subsystem:15} {current_val:.2f} {direction} {predicted:.2f}")

    return 0


if __name__ == "__main__":
    exit(main())
