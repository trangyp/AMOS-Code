"""
AMOS SuperBrain Monitoring - CloudWatch Alarms & Dashboards
Production-grade observability for the 30-layer ecosystem

Author: AMOS Team
Version: 2.0.0
"""

# =============================================================================
# CloudWatch Log Groups
# =============================================================================

resource "aws_cloudwatch_log_group" "superbrain_audit" {
  name              = "/aws/amossuperbrain/${var.environment}/audit"
  retention_in_days = 365
  kms_key_id        = aws_kms_key.logs.arn

  tags = {
    Name        = "${var.project_name}-superbrain-audit"
    Component   = "SuperBrain"
    Purpose     = "AuditTrail"
  }
}

resource "aws_cloudwatch_log_group" "superbrain_governance" {
  name              = "/aws/amossuperbrain/${var.environment}/governance"
  retention_in_days = 90

  tags = {
    Name        = "${var.project_name}-superbrain-governance"
    Component   = "SuperBrain"
    Purpose     = "ActionGate"
  }
}

resource "aws_cloudwatch_log_group" "knowledge_loader" {
  name              = "/aws/amossuperbrain/${var.environment}/knowledge"
  retention_in_days = 30

  tags = {
    Name        = "${var.project_name}-knowledge-loader"
    Component   = "Knowledge"
    Purpose     = "1,500+Files"
  }
}

# =============================================================================
# CloudWatch Alarms - SuperBrain Health
# =============================================================================

resource "aws_cloudwatch_metric_alarm" "superbrain_health" {
  alarm_name          = "${var.project_name}-superbrain-health-${var.environment}"
  comparison_operator   = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "HealthCheckFailures"
  namespace           = "AWS/ApplicationELB"
  period              = "60"
  statistic           = "Sum"
  threshold           = "2"
  alarm_description   = "SuperBrain health check failures"
  alarm_actions       = [aws_sns_topic.alerts.arn]
  ok_actions          = [aws_sns_topic.alerts.arn]

  dimensions = {
    LoadBalancer = aws_lb.main.arn_suffix
  }

  tags = {
    Name        = "${var.project_name}-superbrain-health"
    Severity    = "CRITICAL"
    Component   = "SuperBrain"
  }
}

resource "aws_cloudwatch_metric_alarm" "superbrain_high_latency" {
  alarm_name          = "${var.project_name}-superbrain-latency-${var.environment}"
  comparison_operator   = "GreaterThanThreshold"
  evaluation_periods  = "3"
  metric_name         = "TargetResponseTime"
  namespace           = "AWS/ApplicationELB"
  period              = "60"
  statistic           = "Average"
  threshold           = "1.0"
  alarm_description   = "SuperBrain response time > 1 second"
  alarm_actions       = [aws_sns_topic.alerts.arn]

  dimensions = {
    LoadBalancer = aws_lb.main.arn_suffix
  }

  tags = {
    Name        = "${var.project_name}-superbrain-latency"
    Severity    = "WARNING"
    Component   = "SuperBrain"
  }
}

resource "aws_cloudwatch_metric_alarm" "superbrain_5xx_errors" {
  alarm_name          = "${var.project_name}-superbrain-5xx-${var.environment}"
  comparison_operator   = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "HTTPCode_Target_5XX_Count"
  namespace           = "AWS/ApplicationELB"
  period              = "60"
  statistic           = "Sum"
  threshold           = "10"
  alarm_description   = "SuperBrain 5xx errors > 10"
  alarm_actions       = [aws_sns_topic.alerts.arn]

  dimensions = {
    LoadBalancer = aws_lb.main.arn_suffix
  }

  tags = {
    Name        = "${var.project_name}-superbrain-5xx"
    Severity    = "CRITICAL"
    Component   = "SuperBrain"
  }
}

# =============================================================================
# CloudWatch Alarms - Knowledge System
# =============================================================================

resource "aws_cloudwatch_metric_alarm" "knowledge_loader_errors" {
  alarm_name          = "${var.project_name}-knowledge-errors-${var.environment}"
  comparison_operator   = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "KnowledgeLoadErrors"
  namespace           = "AMOS/SuperBrain"
  period              = "300"
  statistic           = "Sum"
  threshold           = "5"
  alarm_description   = "Knowledge loader errors > 5 in 5 minutes"
  alarm_actions       = [aws_sns_topic.alerts.arn]

  tags = {
    Name        = "${var.project_name}-knowledge-errors"
    Severity    = "WARNING"
    Component   = "KnowledgeLoader"
  }
}

# =============================================================================
# CloudWatch Alarms - Database & Cache
# =============================================================================

resource "aws_cloudwatch_metric_alarm" "rds_cpu_high" {
  alarm_name          = "${var.project_name}-rds-cpu-${var.environment}"
  comparison_operator   = "GreaterThanThreshold"
  evaluation_periods  = "3"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/RDS"
  period              = "300"
  statistic           = "Average"
  threshold           = "80"
  alarm_description   = "RDS CPU utilization > 80%"
  alarm_actions       = [aws_sns_topic.alerts.arn]

  dimensions = {
    DBInstanceIdentifier = aws_db_instance.main.identifier
  }

  tags = {
    Name        = "${var.project_name}-rds-cpu"
    Severity    = "WARNING"
    Component   = "Database"
  }
}

resource "aws_cloudwatch_metric_alarm" "redis_cpu_high" {
  alarm_name          = "${var.project_name}-redis-cpu-${var.environment}"
  comparison_operator   = "GreaterThanThreshold"
  evaluation_periods  = "3"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/ElastiCache"
  period              = "300"
  statistic           = "Average"
  threshold           = "80"
  alarm_description   = "Redis CPU utilization > 80%"
  alarm_actions       = [aws_sns_topic.alerts.arn]

  dimensions = {
    CacheClusterId = aws_elasticache_replication_group.main.id
  }

  tags = {
    Name        = "${var.project_name}-redis-cpu"
    Severity    = "WARNING"
    Component   = "Cache"
  }
}

# =============================================================================
# SNS Topic for Alerts
# =============================================================================

resource "aws_sns_topic" "alerts" {
  name = "${var.project_name}-alerts-${var.environment}"

  tags = {
    Name        = "${var.project_name}-alerts"
    Purpose     = "SuperBrainMonitoring"
  }
}

# =============================================================================
# CloudWatch Dashboard - SuperBrain Overview
# =============================================================================

resource "aws_cloudwatch_dashboard" "superbrain" {
  dashboard_name = "${var.project_name}-superbrain-${var.environment}"

  dashboard_body = jsonencode({
    widgets = [
      {
        type   = "metric"
        x      = 0
        y      = 0
        width  = 12
        height = 6
        properties = {
          title  = "SuperBrain Health Status"
          region = var.aws_region
          metrics = [
            ["AWS/ApplicationELB", "HealthyHostCount", "LoadBalancer", aws_lb.main.arn_suffix],
            [".", "UnHealthyHostCount", ".", "."]
          ]
          period = 60
          stat   = "Average"
        }
      },
      {
        type   = "metric"
        x      = 12
        y      = 0
        width  = 12
        height = 6
        properties = {
          title  = "Response Time (ms)"
          region = var.aws_region
          metrics = [
            ["AWS/ApplicationELB", "TargetResponseTime", "LoadBalancer", aws_lb.main.arn_suffix]
          ]
          period = 60
          stat   = "p99"
        }
      },
      {
        type   = "metric"
        x      = 0
        y      = 6
        width  = 8
        height = 6
        properties = {
          title  = "Request Count"
          region = var.aws_region
          metrics = [
            ["AWS/ApplicationELB", "RequestCount", "LoadBalancer", aws_lb.main.arn_suffix]
          ]
          period = 60
          stat   = "Sum"
        }
      },
      {
        type   = "metric"
        x      = 8
        y      = 6
        width  = 8
        height = 6
        properties = {
          title  = "5xx Errors"
          region = var.aws_region
          metrics = [
            ["AWS/ApplicationELB", "HTTPCode_Target_5XX_Count", "LoadBalancer", aws_lb.main.arn_suffix]
          ]
          period = 60
          stat   = "Sum"
        }
      },
      {
        type   = "metric"
        x      = 16
        y      = 6
        width  = 8
        height = 6
        properties = {
          title  = "RDS CPU Utilization"
          region = var.aws_region
          metrics = [
            ["AWS/RDS", "CPUUtilization", "DBInstanceIdentifier", aws_db_instance.main.identifier]
          ]
          period = 300
          stat   = "Average"
        }
      },
      {
        type   = "text"
        x      = 0
        y      = 12
        width  = 24
        height = 3
        properties = {
          markdown = <<-EOT
            ## AMOS SuperBrain v2.0.0 - System Status
            - **Features Governed**: 4,644
            - **Engines**: 251+
            - **Knowledge Files**: 1,500+
            - **Subsystems**: 14
            - **Integrations**: 10 systems under SuperBrain governance
          EOT
        }
      }
    ]
  })
}

# =============================================================================
# KMS Key for Log Encryption
# =============================================================================

resource "aws_kms_key" "logs" {
  description             = "KMS key for CloudWatch log encryption"
  deletion_window_in_days = 7
  enable_key_rotation     = true

  tags = {
    Name        = "${var.project_name}-logs-key"
    Purpose     = "Encryption"
  }
}

resource "aws_kms_alias" "logs" {
  name          = "alias/${var.project_name}-logs"
  target_key_id = aws_kms_key.logs.key_id
}
