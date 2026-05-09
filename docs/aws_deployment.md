# AWS Deployment Notes

## Current AWS Foundation

Terraform has been applied successfully for the HarborWatch AWS foundation.

Created resources:

- S3 lakehouse bucket
- Raw zone prefix
- Bronze zone prefix
- Silver zone prefix
- Gold zone prefix
- Athena results prefix
- Glue Data Catalog database

## S3 Bucket

harborwatch-dev-lakehouse-giandetogni

## S3 Prefixes

- athena-results/
- bronze/
- gold/
- raw/
- silver/

## Glue Database

harborwatch_lakehouse

## Terraform Outputs

- raw_s3_uri: s3://harborwatch-dev-lakehouse-giandetogni/raw/
- bronze_s3_uri: s3://harborwatch-dev-lakehouse-giandetogni/bronze/
- silver_s3_uri: s3://harborwatch-dev-lakehouse-giandetogni/silver/
- gold_s3_uri: s3://harborwatch-dev-lakehouse-giandetogni/gold/
- glue_database_name: harborwatch_lakehouse

## Current Scope

This deployment is the AWS foundation only.

It does not yet include:

- AWS Glue ETL jobs
- Apache Iceberg tables
- Athena table queries
- Step Functions orchestration
- Lambda file discovery
- CloudWatch pipeline monitoring

## Validation Commands

aws s3 ls s3://harborwatch-dev-lakehouse-giandetogni/
aws glue get-database --name harborwatch_lakehouse --region us-east-1
cd terraform && terraform output

## Important

Terraform state files and local variable files must not be committed to Git.

## Uploaded Gold Outputs

Gold CSV outputs were uploaded to S3:

- s3://harborwatch-dev-lakehouse-giandetogni/gold/gold_port_congestion_daily/date=2024-01-01/gold_port_congestion_daily.csv
- s3://harborwatch-dev-lakehouse-giandetogni/gold/gold_vessel_anomalies/date=2024-01-01/gold_vessel_anomalies.csv

These files prove that the AWS foundation contains real analytical outputs from the local MVP pipeline.
