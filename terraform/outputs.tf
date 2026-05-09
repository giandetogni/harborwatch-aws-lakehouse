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
