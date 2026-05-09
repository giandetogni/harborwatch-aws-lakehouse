variable "aws_region" {
  description = "AWS region used for the HarborWatch MVP."
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Project name used for naming AWS resources."
  type        = string
  default     = "harborwatch"
}

variable "environment" {
  description = "Deployment environment."
  type        = string
  default     = "dev"
}

variable "bucket_name_suffix" {
  description = "Unique suffix for globally unique S3 bucket names. Example: your GitHub username or account alias."
  type        = string
}

variable "glue_database_name" {
  description = "Glue Data Catalog database name."
  type        = string
  default     = "harborwatch_lakehouse"
}
