"""AMOS Equation System - FinOps Cost Monitoring.

Cloud cost management and optimization for AWS infrastructure.
Tracks spend by service, team, and environment with alerting.

Usage:
    python finops/cost_monitor.py --report daily
    python finops/cost_monitor.py --alert-threshold 1000
    python finops/cost_monitor.py --optimize

Author: AMOS Team
Version: 2.0.0
"""

import argparse
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from decimal import Decimal

import boto3
from botocore.exceptions import ClientError
from typing import Dict, List


@dataclass
class CostBreakdown:
    """Cost breakdown by service."""

    service: str
    amount: Decimal
    last_month: Decimal
    change_percent: float
    projected_monthly: Decimal


@dataclass
class CostReport:
    """Complete cost report."""

    period: str
    total: Decimal
    services: List[CostBreakdown]
    budget_status: str
    anomalies: List[dict]
    recommendations: List[str]


class CostMonitor:
    """AWS Cost monitoring and optimization."""

    def __init__(self):
        self.ce_client = boto3.client("ce", region_name="us-east-1")
        self.budgets_client = boto3.client("budgets")

    def get_daily_costs(self, days: int = 7) -> List[dict]:
        """Get daily cost breakdown."""
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

        try:
            response = self.ce_client.get_cost_and_usage(
                TimePeriod={"Start": start_date, "End": end_date},
                Granularity="DAILY",
                Metrics=["BlendedCost", "UsageQuantity"],
                GroupBy=[{"Type": "DIMENSION", "Key": "SERVICE"}],
            )
            return response.get("ResultsByTime", [])
        except ClientError as e:
            print(f"Error fetching costs: {e}")
            return []

    def get_monthly_forecast(self) -> Decimal:
        """Forecast current month spend."""
        try:
            end_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
            start_date = datetime.now().replace(day=1).strftime("%Y-%m-%d")

            response = self.ce_client.get_cost_forecast(
                TimePeriod={"Start": start_date, "End": end_date},
                Metric="BLENDED_COST",
                Granularity="MONTHLY",
            )
            return Decimal(response.get("Total", {}).get("Amount", "0"))
        except ClientError:
            return Decimal("0")

    def check_budget_status(self) -> dict:
        """Check if spend is within budget."""
        try:
            response = self.budgets_client.describe_budget(
                AccountId=self._get_account_id(),
                BudgetName="AMOS-Monthly-Budget",
            )
            budget = response.get("Budget", {})
            limit = Decimal(budget.get("BudgetLimit", {}).get("Amount", "0"))
            actual = Decimal(
                budget.get("CalculatedSpend", {}).get("ActualSpend", {}).get("Amount", "0")
            )

            percent_used = float(actual / limit * 100) if limit > 0 else 0

            return {
                "limit": limit,
                "actual": actual,
                "percent_used": percent_used,
                "status": "exceeded"
                if percent_used > 100
                else "warning"
                if percent_used > 80
                else "ok",
            }
        except ClientError:
            return {
                "limit": Decimal("0"),
                "actual": Decimal("0"),
                "percent_used": 0,
                "status": "unknown",
            }

    def detect_anomalies(self, threshold_percent: float = 20.0) -> List[dict]:
        """Detect cost anomalies."""
        try:
            response = self.ce_client.get_anomalies(
                MonitorArn=self._get_monitor_arn(),
                StartDate=(datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d"),
                EndDate=datetime.now().strftime("%Y-%m-%d"),
            )

            anomalies = []
            for anomaly in response.get("Anomalies", []):
                impact = float(anomaly.get("Impact", {}).get("MaxImpact", 0))
                if impact > threshold_percent:
                    anomalies.append(
                        {
                            "service": anomaly.get("RootCauses", [{}])[0].get("Service", "Unknown"),
                            "impact_percent": impact,
                            "start_date": anomaly.get("AnomalyStartDate"),
                        }
                    )
            return anomalies
        except ClientError:
            return []

    def get_optimization_recommendations(self) -> List[str]:
        """Get cost optimization recommendations."""
        recommendations = []

        try:
            # Check for idle resources
            ec2 = boto3.client("ec2")
            response = ec2.describe_instances(
                Filters=[{"Name": "instance-state-name", "Values": ["running"]}]
            )

            idle_count = 0
            for reservation in response.get("Reservations", []):
                for instance in reservation.get("Instances", []):
                    # Check if instance has low CPU utilization
                    cloudwatch = boto3.client("cloudwatch")
                    metrics = cloudwatch.get_metric_statistics(
                        Namespace="AWS/EC2",
                        MetricName="CPUUtilization",
                        Dimensions=[{"Name": "InstanceId", "Value": instance["InstanceId"]}],
                        StartTime=datetime.now() - timedelta(days=7),
                        EndTime=datetime.now(),
                        Period=86400,
                        Statistics=["Average"],
                    )

                    datapoints = metrics.get("Datapoints", [])
                    if datapoints and all(dp["Average"] < 5 for dp in datapoints):
                        idle_count += 1

            if idle_count > 0:
                recommendations.append(
                    f"Found {idle_count} EC2 instances with <5% CPU for 7 days. Consider stopping or rightsizing."
                )

            # Check for unoptimized ECS tasks
            ecs = boto3.client("ecs")
            clusters = ecs.list_clusters().get("clusterArns", [])
            for cluster in clusters:
                services = ecs.list_services(cluster=cluster).get("serviceArns", [])
                for service in services[:5]:  # Check first 5 services
                    service_info = ecs.describe_services(cluster=cluster, services=[service])
                    for svc in service_info.get("services", []):
                        running = svc.get("runningCount", 0)
                        desired = svc.get("desiredCount", 0)
                        if running > desired * 1.5:
                            recommendations.append(
                                f"ECS service {service} has {running} running but {desired} desired. Scale down."
                            )

        except ClientError as e:
            print(f"Error checking optimizations: {e}")

        return recommendations

    def generate_report(self) -> CostReport:
        """Generate comprehensive cost report."""
        daily_costs = self.get_daily_costs(30)

        # Calculate totals by service
        service_costs: Dict[str, Decimal] = {}
        for day in daily_costs:
            for group in day.get("Groups", []):
                service = group.get("Keys", ["Unknown"])[0]
                amount = Decimal(group.get("Metrics", {}).get("BlendedCost", {}).get("Amount", "0"))
                service_costs[service] = service_costs.get(service, Decimal("0")) + amount

        # Build breakdown
        services = [
            CostBreakdown(
                service=svc,
                amount=amt,
                last_month=Decimal("0"),  # Would need historical data
                change_percent=0.0,
                projected_monthly=amt * Decimal("1.1"),  # Simple projection
            )
            for svc, amt in sorted(service_costs.items(), key=lambda x: x[1], reverse=True)[:10]
        ]

        total = sum(s.amount for s in services)
        budget = self.check_budget_status()
        anomalies = self.detect_anomalies()
        recommendations = self.get_optimization_recommendations()

        return CostReport(
            period=f"{datetime.now().strftime('%Y-%m-%d')} (Last 30 days)",
            total=total,
            services=services,
            budget_status=budget["status"],
            anomalies=anomalies,
            recommendations=recommendations,
        )

    def _get_account_id(self) -> str:
        """Get current AWS account ID."""
        sts = boto3.client("sts")
        return sts.get_caller_identity()["Account"]

    def _get_monitor_arn(self) -> str:
        """Get or create anomaly monitor ARN."""
        try:
            response = self.ce_client.list_anomaly_monitors()
            for monitor in response.get("AnomalyMonitors", []):
                if monitor.get("MonitorName") == "AMOS-Cost-Monitor":
                    return monitor["MonitorArn"]
        except ClientError:
            pass
        return ""


def print_report(report: CostReport):
    """Print cost report in formatted output."""
    print("\n" + "=" * 70)
    print(f"AMOS COST REPORT - {report.period}")
    print("=" * 70)
    print(f"\nTotal Spend: ${report.total:.2f}")
    print(f"Budget Status: {report.budget_status.upper()}")

    print("\nTop Services by Cost:")
    print("-" * 70)
    for svc in report.services:
        print(f"  {svc.service:40} ${svc.amount:>10.2f} ({svc.change_percent:+.1f}%)")

    if report.anomalies:
        print("\n⚠️  Cost Anomalies Detected:")
        print("-" * 70)
        for anomaly in report.anomalies:
            print(
                f"  {anomaly['service']}: +{anomaly['impact_percent']:.1f}% ({anomaly['start_date']})"
            )

    if report.recommendations:
        print("\n💡 Optimization Recommendations:")
        print("-" * 70)
        for rec in report.recommendations:
            print(f"  • {rec}")

    print("\n" + "=" * 70)


def main():
    parser = argparse.ArgumentParser(description="AMOS FinOps Cost Monitor")
    parser.add_argument("--report", choices=["daily", "weekly", "monthly"], help="Generate report")
    parser.add_argument("--alert-threshold", type=float, help="Alert if daily cost exceeds")
    parser.add_argument("--optimize", action="store_true", help="Show optimization recommendations")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    monitor = CostMonitor()

    if args.report:
        report = monitor.generate_report()
        if args.json:
            print(json.dumps(asdict(report), indent=2, default=str))
        else:
            print_report(report)

    elif args.alert_threshold:
        costs = monitor.get_daily_costs(1)
        daily_total = sum(
            Decimal(group.get("Metrics", {}).get("BlendedCost", {}).get("Amount", "0"))
            for day in costs
            for group in day.get("Groups", [])
        )

        if daily_total > Decimal(str(args.alert_threshold)):
            print(
                f"ALERT: Daily cost ${daily_total:.2f} exceeds threshold ${args.alert_threshold:.2f}"
            )
            exit(1)
        else:
            print(f"OK: Daily cost ${daily_total:.2f} within threshold")

    elif args.optimize:
        recommendations = monitor.get_optimization_recommendations()
        if recommendations:
            print("\nOptimization Opportunities:")
            for rec in recommendations:
                print(f"  • {rec}")
        else:
            print("No immediate optimization opportunities found.")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
