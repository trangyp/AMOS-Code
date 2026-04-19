# AWS Elasticsearch/OpenSearch Domain for AMOS
# Managed search service for equation discovery

resource "aws_opensearch_domain" "amos_search" {
  domain_name    = "amos-${var.environment}-search"
  engine_version = "OpenSearch_2.5"

  cluster_config {
    instance_type  = var.es_instance_type  # t3.small.search for dev, m6g.large for prod
    instance_count = var.es_instance_count

    dedicated_master_enabled = var.es_instance_count >= 3
    dedicated_master_type    = var.es_instance_count >= 3 ? "t3.small.search" : null
    dedicated_master_count   = var.es_instance_count >= 3 ? 3 : null

    zone_awareness_enabled = var.es_instance_count > 1
    zone_awareness_config {
      availability_zone_count = var.es_instance_count > 1 ? 2 : null
    }
  }

  ebs_options {
    ebs_enabled = true
    volume_type = "gp3"
    volume_size = var.es_volume_size
    iops        = 3000
  }

  vpc_options {
    subnet_ids         = slice(aws_subnet.private[*].id, 0, var.es_instance_count > 1 ? 2 : 1)
    security_group_ids = [aws_security_group.elasticsearch.id]
  }

  encrypt_at_rest {
    enabled = true
  }

  node_to_node_encryption {
    enabled = true
  }

  domain_endpoint_options {
    enforce_https       = true
    tls_security_policy = "Policy-Min-TLS-1-2-2019-07"
  }

  access_policies = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          AWS = "*"
        }
        Action = "es:*"
        Resource = "arn:aws:es:${var.aws_region}:${data.aws_caller_identity.current.account_id}:domain/amos-${var.environment}-search/*"
        Condition = {
          IpAddress = {
            "aws:SourceIp" = [aws_vpc.main.cidr_block]
          }
        }
      }
    ]
  })

  advanced_security_options {
    enabled                        = true
    internal_user_database_enabled = true
    master_user_options {
      master_user_name     = var.es_master_user
      master_user_password = var.es_master_password
    }
  }

  snapshot_options {
    automated_snapshot_start_hour = 23
  }

  tags = {
    Name        = "amos-${var.environment}-search"
    Environment = var.environment
  }
}

# Security group for Elasticsearch
resource "aws_security_group" "elasticsearch" {
  name_prefix = "amos-es-"
  description = "Security group for AMOS Elasticsearch"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = [aws_vpc.main.cidr_block]
    description = "HTTPS from VPC"
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "amos-es-${var.environment}"
  }
}

# CloudWatch alarm for Elasticsearch
resource "aws_cloudwatch_metric_alarm" "es_cpu" {
  alarm_name          = "amos-${var.environment}-es-cpu"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "3"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/ES"
  period              = "300"
  statistic           = "Average"
  threshold           = "80"
  alarm_description   = "Elasticsearch CPU utilization"

  dimensions = {
    DomainName = aws_opensearch_domain.amos_search.domain_name
    ClientId   = data.aws_caller_identity.current.account_id
  }

  alarm_actions = [aws_sns_topic.alarms.arn]
}

resource "aws_cloudwatch_metric_alarm" "es_storage" {
  alarm_name          = "amos-${var.environment}-es-storage"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "FreeStorageSpace"
  namespace           = "AWS/ES"
  period              = "300"
  statistic           = "Minimum"
  threshold           = "20480"  # 20GB in MB
  alarm_description   = "Elasticsearch low storage"

  dimensions = {
    DomainName = aws_opensearch_domain.amos_search.domain_name
    ClientId   = data.aws_caller_identity.current.account_id
  }

  alarm_actions = [aws_sns_topic.alarms.arn]
}

# Outputs
output "elasticsearch_endpoint" {
  description = "Elasticsearch domain endpoint"
  value       = aws_opensearch_domain.amos_search.endpoint
  sensitive   = true
}

output "elasticsearch_arn" {
  description = "Elasticsearch domain ARN"
  value       = aws_opensearch_domain.amos_search.arn
}
