resource "aws_s3_object" "raw_to_bronze_glue_script" {
  bucket = aws_s3_bucket.lakehouse.id
  key    = "scripts/glue/raw_to_bronze_glue.py"
  source = "${path.module}/../src/glue_jobs_aws/raw_to_bronze_glue.py"
  etag   = filemd5("${path.module}/../src/glue_jobs_aws/raw_to_bronze_glue.py")
}

resource "aws_glue_job" "raw_to_bronze" {
  name              = "${local.name_prefix}-raw-to-bronze"
  description       = "Transforms raw AIS CSV data from S3 into Bronze Parquet data."
  role_arn          = aws_iam_role.glue_service_role.arn
  glue_version      = "4.0"
  worker_type       = "G.1X"
  number_of_workers = 2
  timeout           = 10
  max_retries       = 0

  command {
    name            = "glueetl"
    script_location = "s3://${aws_s3_bucket.lakehouse.bucket}/${aws_s3_object.raw_to_bronze_glue_script.key}"
    python_version  = "3"
  }

  default_arguments = {
    "--job-language"                     = "python"
    "--enable-metrics"                   = "true"
    "--enable-continuous-cloudwatch-log" = "true"
    "--INPUT_PATH"                       = "s3://${aws_s3_bucket.lakehouse.bucket}/raw/public_ais/date=2024-01-01/AIS_2024_01_01_sample_1k.csv"
    "--OUTPUT_PATH"                      = "s3://${aws_s3_bucket.lakehouse.bucket}/bronze/ais_messages/"
  }
}
