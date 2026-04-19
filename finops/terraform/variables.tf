# Variables for AMOS FinOps Terraform Module

variable "environment" {
  description = "Environment (development, staging, production)"
  type        = string
  default     = "production"

  validation {
    condition     = contains(["development", "staging", "production"], var.environment)
    error_message = "Environment must be development, staging, or production."
  }
}

variable "monthly_budget_limit" {
  description = "Monthly budget limit in USD"
  type        = string
  default     = "1000"  # Adjust based on expected spend

  validation {
    condition     = can(tonumber(var.monthly_budget_limit))
    error_message = "Monthly budget limit must be a valid number."
  }
}

variable "daily_budget_limit" {
  description = "Daily budget limit in USD"
  type        = string
  default     = "100"  # Approximately monthly/30

  validation {
    condition     = can(tonumber(var.daily_budget_limit))
    error_message = "Daily budget limit must be a valid number."
  }
}

variable "budget_alert_emails" {
  description = "Email addresses for budget alerts"
  type        = list(string)
  default     = []

  validation {
    condition     = length(var.budget_alert_emails) > 0
    error_message = "At least one budget alert email is required."
  }
}

variable "finops_contact_email" {
  description = "Primary contact for FinOps alerts"
  type        = string
  default     = "finops@example.com"
}

variable "anomaly_threshold" {
  description = "Anomaly detection threshold in USD"
  type        = number
  default     = 100
}
