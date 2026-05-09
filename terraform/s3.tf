resource "aws_s3_bucket" "lakehouse" {
  bucket = local.lakehouse_bucket_name
}

resource "aws_s3_bucket_public_access_block" "lakehouse" {
  bucket = aws_s3_bucket.lakehouse.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_versioning" "lakehouse" {
  bucket = aws_s3_bucket.lakehouse.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "lakehouse" {
  bucket = aws_s3_bucket.lakehouse.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_object" "raw_prefix" {
  bucket  = aws_s3_bucket.lakehouse.id
  key     = "raw/"
  content = ""
}

resource "aws_s3_object" "bronze_prefix" {
  bucket  = aws_s3_bucket.lakehouse.id
  key     = "bronze/"
  content = ""
}

resource "aws_s3_object" "silver_prefix" {
  bucket  = aws_s3_bucket.lakehouse.id
  key     = "silver/"
  content = ""
}

resource "aws_s3_object" "gold_prefix" {
  bucket  = aws_s3_bucket.lakehouse.id
  key     = "gold/"
  content = ""
}

resource "aws_s3_object" "athena_prefix" {
  bucket  = aws_s3_bucket.lakehouse.id
  key     = "athena-results/"
  content = ""
}
