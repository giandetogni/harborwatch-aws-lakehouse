resource "aws_iam_role" "glue_service_role" {
  name = "${local.name_prefix}-glue-service-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "glue.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "glue_service_role_basic" {
  role       = aws_iam_role.glue_service_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSGlueServiceRole"
}

resource "aws_iam_policy" "glue_lakehouse_s3_access" {
  name        = "${local.name_prefix}-glue-lakehouse-s3-access"
  description = "Allows Glue jobs to read and write HarborWatch lakehouse data in S3."

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject"
        ]
        Resource = [
          "${aws_s3_bucket.lakehouse.arn}/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "s3:ListBucket",
          "s3:GetBucketLocation"
        ]
        Resource = [
          aws_s3_bucket.lakehouse.arn
        ]
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "glue_lakehouse_s3_access" {
  role       = aws_iam_role.glue_service_role.name
  policy_arn = aws_iam_policy.glue_lakehouse_s3_access.arn
}


resource "aws_iam_role" "step_functions_role" {
  name = "${local.name_prefix}-step-functions-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "states.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })
}

resource "aws_iam_role_policy" "step_functions_glue_access" {
  name = "${local.name_prefix}-step-functions-glue-access"
  role = aws_iam_role.step_functions_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "glue:StartJobRun",
          "glue:GetJobRun",
          "glue:GetJobRuns",
          "glue:BatchStopJobRun"
        ]
        Resource = [
          aws_glue_job.raw_to_bronze.arn,
          aws_glue_job.bronze_to_silver_clean.arn,
          aws_glue_job.silver_to_port_proximity.arn,
          aws_glue_job.port_proximity_to_vessel_stops.arn
        ]
      }
    ]
  })
}
