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
    "--INPUT_PATH"                       = "s3://${aws_s3_bucket.lakehouse.bucket}/raw/public_ais/date=2024-01-01/AIS_2024_01_01_sample_10k.csv"
    "--OUTPUT_PATH"                      = "s3://${aws_s3_bucket.lakehouse.bucket}/bronze/ais_messages/"
  }
}

resource "aws_s3_object" "bronze_to_silver_clean_glue_script" {
  bucket = aws_s3_bucket.lakehouse.id
  key    = "scripts/glue/bronze_to_silver_clean_glue.py"
  source = "${path.module}/../src/glue_jobs_aws/bronze_to_silver_clean_glue.py"
  etag   = filemd5("${path.module}/../src/glue_jobs_aws/bronze_to_silver_clean_glue.py")
}

resource "aws_glue_job" "bronze_to_silver_clean" {
  name              = "${local.name_prefix}-bronze-to-silver-clean"
  description       = "Applies data quality rules to Bronze AIS Parquet data and writes Silver clean positions."
  role_arn          = aws_iam_role.glue_service_role.arn
  glue_version      = "4.0"
  worker_type       = "G.1X"
  number_of_workers = 2
  timeout           = 10
  max_retries       = 0

  command {
    name            = "glueetl"
    script_location = "s3://${aws_s3_bucket.lakehouse.bucket}/${aws_s3_object.bronze_to_silver_clean_glue_script.key}"
    python_version  = "3"
  }

  default_arguments = {
    "--job-language"                     = "python"
    "--enable-metrics"                   = "true"
    "--enable-continuous-cloudwatch-log" = "true"
    "--INPUT_PATH"                       = "s3://${aws_s3_bucket.lakehouse.bucket}/bronze/ais_messages/"
    "--OUTPUT_PATH"                      = "s3://${aws_s3_bucket.lakehouse.bucket}/silver/vessel_positions_clean/"
  }
}


resource "aws_s3_object" "silver_to_port_proximity_glue_script" {
  bucket = aws_s3_bucket.lakehouse.id
  key    = "scripts/glue/silver_to_port_proximity_glue.py"
  source = "${path.module}/../src/glue_jobs_aws/silver_to_port_proximity_glue.py"
  etag   = filemd5("${path.module}/../src/glue_jobs_aws/silver_to_port_proximity_glue.py")
}

resource "aws_glue_job" "silver_to_port_proximity" {
  name              = "${local.name_prefix}-silver-to-port-proximity"
  description       = "Enriches Silver AIS positions with nearest port and port radius flags."
  role_arn          = aws_iam_role.glue_service_role.arn
  glue_version      = "4.0"
  worker_type       = "G.1X"
  number_of_workers = 2
  timeout           = 10
  max_retries       = 0

  command {
    name            = "glueetl"
    script_location = "s3://${aws_s3_bucket.lakehouse.bucket}/${aws_s3_object.silver_to_port_proximity_glue_script.key}"
    python_version  = "3"
  }

  default_arguments = {
    "--job-language"                     = "python"
    "--enable-metrics"                   = "true"
    "--enable-continuous-cloudwatch-log" = "true"
    "--INPUT_POSITIONS_PATH"             = "s3://${aws_s3_bucket.lakehouse.bucket}/silver/vessel_positions_clean/"
    "--INPUT_PORTS_PATH"                 = "s3://${aws_s3_bucket.lakehouse.bucket}/raw/reference/ports/harborwatch_ports_mvp.csv"
    "--OUTPUT_PATH"                      = "s3://${aws_s3_bucket.lakehouse.bucket}/silver/vessel_port_proximity/"
  }
}


resource "aws_s3_object" "port_proximity_to_vessel_stops_glue_script" {
  bucket = aws_s3_bucket.lakehouse.id
  key    = "scripts/glue/port_proximity_to_vessel_stops_glue.py"
  source = "${path.module}/../src/glue_jobs_aws/port_proximity_to_vessel_stops_glue.py"
  etag   = filemd5("${path.module}/../src/glue_jobs_aws/port_proximity_to_vessel_stops_glue.py")
}

resource "aws_glue_job" "port_proximity_to_vessel_stops" {
  name              = "${local.name_prefix}-port-proximity-to-vessel-stops"
  description       = "Detects vessel stop episodes near MVP ports."
  role_arn          = aws_iam_role.glue_service_role.arn
  glue_version      = "4.0"
  worker_type       = "G.1X"
  number_of_workers = 2
  timeout           = 10
  max_retries       = 0

  command {
    name            = "glueetl"
    script_location = "s3://${aws_s3_bucket.lakehouse.bucket}/${aws_s3_object.port_proximity_to_vessel_stops_glue_script.key}"
    python_version  = "3"
  }

  default_arguments = {
    "--job-language"                     = "python"
    "--enable-metrics"                   = "true"
    "--enable-continuous-cloudwatch-log" = "true"
    "--INPUT_PATH"                       = "s3://${aws_s3_bucket.lakehouse.bucket}/silver/vessel_port_proximity/"
    "--OUTPUT_PATH"                      = "s3://${aws_s3_bucket.lakehouse.bucket}/silver/vessel_stops/"
  }
}
