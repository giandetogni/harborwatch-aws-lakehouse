resource "aws_athena_workgroup" "lakehouse" {
  name        = "${local.name_prefix}-athena-workgroup"
  description = "Athena workgroup for HarborWatch lakehouse queries."

  configuration {
    enforce_workgroup_configuration    = true
    publish_cloudwatch_metrics_enabled = true
    bytes_scanned_cutoff_per_query     = 1073741824

    result_configuration {
      output_location = "s3://${aws_s3_bucket.lakehouse.bucket}/athena-results/"

      encryption_configuration {
        encryption_option = "SSE_S3"
      }
    }
  }
}
