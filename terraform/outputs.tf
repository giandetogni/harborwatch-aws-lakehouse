output "lakehouse_bucket_name" {
  description = "S3 bucket used for the HarborWatch lakehouse."
  value       = aws_s3_bucket.lakehouse.bucket
}

output "lakehouse_bucket_arn" {
  description = "ARN of the HarborWatch lakehouse bucket."
  value       = aws_s3_bucket.lakehouse.arn
}

output "glue_database_name" {
  description = "Glue Data Catalog database name."
  value       = aws_glue_catalog_database.lakehouse.name
}

output "raw_s3_uri" {
  description = "Raw zone S3 URI."
  value       = "s3://${aws_s3_bucket.lakehouse.bucket}/raw/"
}

output "bronze_s3_uri" {
  description = "Bronze zone S3 URI."
  value       = "s3://${aws_s3_bucket.lakehouse.bucket}/bronze/"
}

output "silver_s3_uri" {
  description = "Silver zone S3 URI."
  value       = "s3://${aws_s3_bucket.lakehouse.bucket}/silver/"
}

output "gold_s3_uri" {
  description = "Gold zone S3 URI."
  value       = "s3://${aws_s3_bucket.lakehouse.bucket}/gold/"
}


output "athena_workgroup_name" {
  description = "Athena workgroup used for HarborWatch queries."
  value       = aws_athena_workgroup.lakehouse.name
}

output "athena_results_s3_uri" {
  description = "S3 URI used for Athena query results."
  value       = "s3://${aws_s3_bucket.lakehouse.bucket}/athena-results/"
}


output "glue_service_role_name" {
  description = "IAM role name used by AWS Glue jobs."
  value       = aws_iam_role.glue_service_role.name
}

output "glue_service_role_arn" {
  description = "IAM role ARN used by AWS Glue jobs."
  value       = aws_iam_role.glue_service_role.arn
}


output "raw_to_bronze_glue_job_name" {
  description = "AWS Glue job name for Raw to Bronze transformation."
  value       = aws_glue_job.raw_to_bronze.name
}

output "bronze_to_silver_clean_glue_job_name" {
  description = "AWS Glue job name for Bronze to Silver clean transformation."
  value       = aws_glue_job.bronze_to_silver_clean.name
}
