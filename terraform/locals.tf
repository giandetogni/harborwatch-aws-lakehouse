locals {
  name_prefix = "${var.project_name}-${var.environment}"

  lakehouse_bucket_name = lower(
    "${local.name_prefix}-lakehouse-${var.bucket_name_suffix}"
  )

  common_tags = {
    Project     = "HarborWatch"
    Environment = var.environment
    ManagedBy   = "Terraform"
    Owner       = "Gian Detogni"
  }
}
