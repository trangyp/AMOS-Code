# AWS Budgets and Cost Alerts for AMOS Equation System
# Provides proactive cost management and alerting

# Monthly Budget with Alert Thresholds
resource "aws_budgets_budget" "monthly" {
  name              = "AMOS-Monthly-Budget"
  budget_type       = "COST"
  limit_amount      = var.monthly_budget_limit
  limit_unit        = "USD"
  time_period_start = "2024-01-01_00:00"
  time_unit         = "MONTHLY"

  cost_filter {
    name = "TagKeyValue"
    values = [
      "user:Project$AMOS",
      "user:Environment${var.environment}",
    ]
  }

  notification {
    comparison_operator        = "GREATER_THAN"
    threshold                  = 80
    threshold_type             = "PERCENTAGE"
    notification_type          = "ACTUAL"
    subscriber_email_addresses = var.budget_alert_emails
    subscriber_sns_topic_arns  = [aws_sns_topic.budget_alerts.arn]
  }

  notification {
    comparison_operator        = "GREATER_THAN"
    threshold                  = 100
    threshold_type             = "PERCENTAGE"
    notification_type          = "FORECASTED"
    subscriber_email_addresses = var.budget_alert_emails
    subscriber_sns_topic_arns  = [aws_sns_topic.budget_alerts.arn]
  }

  tags = {
    Name        = "AMOS-Monthly-Budget"
    Environment = var.environment
    ManagedBy   = "Terraform"
    Category    = "FinOps"
  }
}

# Daily Budget for Rapid Spend Detection
resource "aws_budgets_budget" "daily" {
  name              = "AMOS-Daily-Budget"
  budget_type       = "COST"
  limit_amount      = var.daily_budget_limit
  limit_unit        = "USD"
  time_period_start = "2024-01-01_00:00"
  time_unit         = "DAILY"

  notification {
    comparison_operator        = "GREATER_THAN"
    threshold                  = 100
    threshold_type             = "PERCENTAGE"
    notification_type          = "ACTUAL"
    subscriber_email_addresses = var.budget_alert_emails
    subscriber_sns_topic_arns  = [aws_sns_topic.budget_alerts.arn]
  }

  tags = {
    Name        = "AMOS-Daily-Budget"
    Environment = var.environment
    ManagedBy   = "Terraform"
    Category    = "FinOps"
  }
}

# Cost Anomaly Monitor
resource "aws_ce_anomaly_monitor" "service_monitor" {
  name              = "AMOS-Service-Cost-Monitor"
  monitor_type      = "DIMENSIONAL"
  monitor_dimension = "SERVICE"

  tags = {
    Name        = "AMOS-Cost-Anomaly-Monitor"
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

# Anomaly Alert Subscription
resource "aws_ce_anomaly_subscription" "service_alerts" {
  name      = "AMOS-Anomaly-Alert"
  threshold = 100  # $100 minimum anomaly
  frequency = "IMMEDIATE"

  monitor_arn_list = [aws_ce_anomaly_monitor.service_monitor.arn]

  subscriber {
    type    = "EMAIL"
    address = var.finops_contact_email
  }

  subscriber {
    type    = "SNS"
    address = aws_sns_topic.budget_alerts.arn
  }
}

# SNS Topic for Budget Alerts
resource "aws_sns_topic" "budget_alerts" {
  name = "amos-budget-alerts"

  tags = {
    Name        = "AMOS-Budget-Alerts"
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

# SNS Topic Policy
resource "aws_sns_topic_policy" "budget_alerts" {
  arn = aws_sns_topic.budget_alerts.arn

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "AllowBudgetsPublish"
        Effect = "Allow"
        Principal = {
          Service = "budgets.amazonaws.com"
        }
        Action   = "SNS:Publish"
        Resource = aws_sns_topic.budget_alerts.arn
      }
    ]
  })
}

# Lambda for Automated Cost Actions
resource "aws_lambda_function" "cost_optimizer" {
  filename         = data.archive_file.cost_optimizer_zip.output_path
  function_name    = "amos-cost-optimizer"
  role             = aws_iam_role.cost_optimizer.arn
  handler          = "index.handler"
  runtime          = "python3.11"
  timeout          = 300
  memory_size      = 256

  environment {
    variables = {
      ENVIRONMENT     = var.environment
      DRY_RUN         = "true"  # Set to false to enable actual actions
      MAX_IDLE_DAYS   = "7"
      NOTIFICATION_SNS = aws_sns_topic.budget_alerts.arn
    }
  }

  tags = {
    Name        = "AMOS-Cost-Optimizer"
    Environment = var.environment
    ManagedBy   = "Terraform"
    Category    = "FinOps"
  }
}

# IAM Role for Cost Optimizer Lambda
resource "aws_iam_role" "cost_optimizer" {
  name = "amos-cost-optimizer-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name        = "AMOS-Cost-Optimizer-Role"
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

# IAM Policy for Cost Optimizer
resource "aws_iam_role_policy" "cost_optimizer" {
  name = "amos-cost-optimizer-policy"
  role = aws_iam_role.cost_optimizer.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ce:GetCostAndUsage",
          "ce:GetAnomalies",
          "ce:GetAnomalyMonitors",
          "ce:ListCostAllocationTags",
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "ec2:DescribeInstances",
          "ec2:DescribeInstanceAttribute",
          "ec2:StopInstances",
          "ec2:TerminateInstances",
          "ec2:DescribeRegions",
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "cloudwatch:GetMetricStatistics",
          "cloudwatch:ListMetrics",
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "ecs:DescribeServices",
          "ecs:ListServices",
          "ecs:UpdateService",
          "ecs:ListClusters",
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "sns:Publish",
        ]
        Resource = aws_sns_topic.budget_alerts.arn
      },
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents",
        ]
        Resource = "arn:aws:logs:*:*:*"
      },
    ]
  })
}

# CloudWatch Event Rule for Daily Cost Check
resource "aws_cloudwatch_event_rule" "daily_cost_check" {
  name                = "amos-daily-cost-check"
  description         = "Trigger cost optimization check daily"
  schedule_expression = "cron(0 9 * * ? *)"  # 9 AM UTC daily

  tags = {
    Name        = "AMOS-Daily-Cost-Check"
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

resource "aws_cloudwatch_event_target" "cost_optimizer" {
  rule      = aws_cloudwatch_event_rule.daily_cost_check.name
  target_id = "CostOptimizerLambda"
  arn       = aws_lambda_function.cost_optimizer.arn
}

resource "aws_lambda_permission" "allow_cloudwatch" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.cost_optimizer.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.daily_cost_check.arn
}

# Cost Allocation Tags - Required for proper cost tracking
resource "aws_ce_cost_allocation_tag" "project" {
  tag_key = "Project"
  status  = "Active"
}

resource "aws_ce_cost_allocation_tag" "environment" {
  tag_key = "Environment"
  status  = "Active"
}

resource "aws_ce_cost_allocation_tag" "team" {
  tag_key = "Team"
  status  = "Active"
}

resource "aws_ce_cost_allocation_tag" "service" {
  tag_key = "Service"
  status  = "Active"
}

# Data source for Lambda zip
# Note: In production, use a proper CI/CD pipeline to build and deploy
# For initial setup, you can manually create the zip
data "archive_file" "cost_optimizer_zip" {
  type        = "zip"
  output_path = "${path.module}/cost_optimizer.zip"

  source {
    content  = <<-EOF
import json
import boto3
import os
from datetime import datetime, timedelta

def handler(event, context):
    """Lambda handler for cost optimization."""
    dry_run = os.environ.get('DRY_RUN', 'true').lower() == 'true'

    ec2 = boto3.client('ec2')
    cloudwatch = boto3.client('cloudwatch')
    sns = boto3.client('sns')

    findings = []

    # Check for idle EC2 instances
    instances = ec2.describe_instances(
        Filters=[{'Name': 'instance-state-name', 'Values': ['running']}]
    )

    for reservation in instances.get('Reservations', []):
        for instance in reservation.get('Instances', []):
            instance_id = instance['InstanceId']

            # Get CPU metrics for last 7 days
            metrics = cloudwatch.get_metric_statistics(
                Namespace='AWS/EC2',
                MetricName='CPUUtilization',
                Dimensions=[{'Name': 'InstanceId', 'Value': instance_id}],
                StartTime=datetime.now() - timedelta(days=7),
                EndTime=datetime.now(),
                Period=86400,
                Statistics=['Average'],
            )

            datapoints = metrics.get('Datapoints', [])
            if datapoints and all(dp['Average'] < 5 for dp in datapoints):
                findings.append({
                    'resource': instance_id,
                    'type': 'EC2',
                    'reason': 'CPU < 5% for 7 days',
                    'action': 'Stop or terminate',
                    'dry_run': dry_run
                })

                if not dry_run:
                    ec2.stop_instances(InstanceIds=[instance_id])

    # Send notification if findings
    if findings:
        message = {
            'default': json.dumps({
                'alert_type': 'Cost Optimization',
                'findings_count': len(findings),
                'findings': findings,
                'timestamp': datetime.now().isoformat(),
            }, indent=2)
        }

        sns.publish(
            TopicArn=os.environ.get('NOTIFICATION_SNS'),
            Message=json.dumps(message),
            MessageStructure='json'
        )

    return {
        'statusCode': 200,
        'body': json.dumps({
            'findings': len(findings),
            'dry_run': dry_run
        })
    }
EOF
    filename = "index.py"
  }
}

# Outputs
output "budget_alerts_topic_arn" {
  description = "SNS topic ARN for budget alerts"
  value       = aws_sns_topic.budget_alerts.arn
}

output "monthly_budget_limit" {
  description = "Monthly budget limit in USD"
  value       = var.monthly_budget_limit
}

output "anomaly_monitor_arn" {
  description = "Cost anomaly monitor ARN"
  value       = aws_ce_anomaly_monitor.service_monitor.arn
}
