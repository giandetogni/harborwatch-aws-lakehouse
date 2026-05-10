# HarborWatch Runbook

## Purpose

This runbook describes how to operate the HarborWatch AWS lakehouse MVP.

It covers the main operational actions required to run, validate, troubleshoot, and clean up the AWS pipeline.

## Pipeline Overview

The AWS pipeline processes public AIS vessel tracking data through the following flow:

1. Raw AIS sample in Amazon S3
2. AWS Glue Raw-to-Bronze job
3. Bronze Parquet output
4. AWS Glue Bronze-to-Silver Clean job
5. Silver Clean Parquet output
6. Silver Data Quality Report
7. AWS Glue Silver-to-Port-Proximity job
8. Silver Port Proximity Parquet output
9. AWS Glue Port-Proximity-to-Vessel-Stops job
10. Silver Vessel Stops Parquet output
11. Athena Gold Port Congestion table

The Glue jobs are orchestrated by AWS Step Functions.

## Main AWS Resources

### S3 Bucket

Bucket:

- harborwatch-dev-lakehouse-giandetogni

Main prefixes:

- raw/
- bronze/
- silver/
- gold/
- athena-results/
- scripts/glue/

### Glue Jobs

Glue jobs:

- harborwatch-dev-raw-to-bronze
- harborwatch-dev-bronze-to-silver-clean
- harborwatch-dev-silver-to-port-proximity
- harborwatch-dev-port-proximity-to-vessel-stops

### Step Functions

State machine:

- harborwatch-dev-lakehouse-pipeline

### Athena

Database:

- harborwatch_lakehouse

Important tables:

- bronze_ais_messages
- silver_vessel_positions_clean
- silver_data_quality_report
- silver_vessel_port_proximity
- silver_vessel_stops
- gold_port_congestion_daily_aws

## How to Run the Pipeline

### 1. Confirm AWS credentials

Run:

aws sts get-caller-identity

Expected result:

- The command returns the active AWS account and IAM user.

### 2. Confirm Terraform outputs

Run:

cd terraform
terraform output
cd ..

Expected outputs include:

- lakehouse_bucket_name
- glue_database_name
- raw_to_bronze_glue_job_name
- bronze_to_silver_clean_glue_job_name
- silver_to_port_proximity_glue_job_name
- port_proximity_to_vessel_stops_glue_job_name
- lakehouse_pipeline_state_machine_arn

### 3. Start the Step Functions pipeline

Run:

EXECUTION_ARN=$(aws stepfunctions start-execution --state-machine-arn $(cd terraform && terraform output -raw lakehouse_pipeline_state_machine_arn) --region us-east-1 --query "executionArn" --output text)

echo $EXECUTION_ARN

### 4. Check execution status

Run:

aws stepfunctions describe-execution --execution-arn $EXECUTION_ARN --region us-east-1 --query "status" --output text

Expected final result:

- SUCCEEDED

### 5. Check execution history

Run:

aws stepfunctions get-execution-history --execution-arn $EXECUTION_ARN --region us-east-1 --reverse-order --max-results 10 --no-cli-pager

Expected result:

- ExecutionSucceeded
- Final Glue job state: SUCCEEDED
- Final job: harborwatch-dev-port-proximity-to-vessel-stops

## How to Validate Outputs

### Validate S3 outputs

Bronze:

aws s3 ls s3://harborwatch-dev-lakehouse-giandetogni/bronze/ais_messages/ --recursive

Silver Clean:

aws s3 ls s3://harborwatch-dev-lakehouse-giandetogni/silver/vessel_positions_clean/ --recursive

Silver Port Proximity:

aws s3 ls s3://harborwatch-dev-lakehouse-giandetogni/silver/vessel_port_proximity/ --recursive

Silver Vessel Stops:

aws s3 ls s3://harborwatch-dev-lakehouse-giandetogni/silver/vessel_stops/ --recursive

Gold:

aws s3 ls s3://harborwatch-dev-lakehouse-giandetogni/gold/ --recursive

## Athena Validation Queries

### Validate Silver Data Quality

Query:

SELECT
  quality_status,
  COUNT(*) AS row_count
FROM harborwatch_lakehouse.silver_vessel_positions_clean
GROUP BY quality_status
ORDER BY quality_status;

Expected result from the 1k validation sample:

- valid: 997
- rejected: 3

### Validate Silver Port Proximity

Query:

SELECT
  nearest_port_name,
  COUNT(*) AS total_positions,
  SUM(CASE WHEN is_within_port_radius THEN 1 ELSE 0 END) AS positions_within_20km,
  COUNT(DISTINCT mmsi) AS distinct_vessels
FROM harborwatch_lakehouse.silver_vessel_port_proximity
GROUP BY nearest_port_name
ORDER BY positions_within_20km DESC;

Expected result:

- Rows for the five MVP ports
- Non-zero positions within 20 km

### Validate Silver Vessel Stops

Query:

SELECT
  COUNT(*) AS stop_count
FROM harborwatch_lakehouse.silver_vessel_stops;

Expected result from the 10k sample:

- stop_count: 26

### Validate Gold Port Congestion

Query:

SELECT *
FROM harborwatch_lakehouse.gold_port_congestion_daily_aws
ORDER BY port_congestion_index DESC;

Expected result:

- 5 rows, one for each MVP port
- Houston ranked highest in the current AWS sample

## Common Failure Modes

### AWS credentials not configured

Symptom:

- AWS CLI returns Unable to locate credentials.

Resolution:

- Run aws configure or aws login, depending on the local setup.
- Re-run aws sts get-caller-identity.

### Terraform access denied

Symptom:

- Terraform fails with AccessDenied on IAM or Step Functions.

Resolution:

- Check the IAM policy attached to harborwatch-terraform.
- Confirm it allows the exact HarborWatch IAM role or Step Functions resource being managed.
- Avoid using AdministratorAccess unless absolutely necessary.

### Glue job fails

Symptom:

- Glue job state is FAILED.

Resolution:

Run:

aws glue get-job-run --job-name JOB_NAME --run-id JOB_RUN_ID --region us-east-1 --no-cli-pager

Check:

- ErrorMessage
- CloudWatch logs
- Input path exists
- Output path is writable
- IAM role has S3 access

### Athena query returns TABLE_NOT_FOUND

Symptom:

- Athena cannot find the table.

Resolution:

- Confirm the table creation SQL was executed.
- Confirm the database is harborwatch_lakehouse.
- Confirm the table name is correct.
- Run MSCK REPAIR TABLE if the table is partitioned.

### Athena query result is still RUNNING

Symptom:

- get-query-results fails because the query has not finished.

Resolution:

- Check status with get-query-execution.
- Wait until the status is SUCCEEDED.
- Then run get-query-results.

### Vessel stops output is empty

Symptom:

- Glue job succeeds but silver/vessel_stops/ has no Parquet files.

Possible cause:

- The AIS sample is too small or too sparse.
- Dwell time detection requires multiple stopped messages for the same vessel near the same port.

Resolution:

- Increase the AIS sample size.
- Re-run the pipeline.
- Validate candidate stopped positions in Athena.

## Operational Assumptions

The MVP assumes:

- AIS data is batch processed.
- Input sample is bounded.
- Port proximity uses point-based distance, not port polygons.
- Vessel stops are rule-based.
- Weather is not included in the AWS-native Gold table.
- AWS-native anomaly generation is not implemented yet.

## Recovery Procedure

If the pipeline fails midway:

1. Identify the failed Step Functions state.
2. Inspect the failed Glue job run.
3. Fix the input data, code, permissions, or SQL issue.
4. Re-run the Step Functions pipeline.
5. Validate S3 outputs.
6. Validate Athena tables.
7. Document the failure and fix if relevant.

## Cleanup Procedure

For development cleanup:

1. Avoid deleting the Terraform-managed bucket unless intentionally destroying the project.
2. Remove only temporary prefixes if needed.
3. Be careful with athena-results/ because query history may reference those outputs.
4. Use terraform destroy only if intentionally removing the whole AWS deployment.

## Current Known Limitations

- The AWS pipeline currently uses Parquet external tables, not Apache Iceberg.
- AWS-native anomaly generation is not implemented yet.
- The current AWS sample is bounded for cost control.
- Gold Port Congestion is relative to the selected sample and MVP ports.
- Port boundaries use 20 km radius from representative port coordinates, not official polygon boundaries.

## Operator Checklist

Before running the pipeline:

- AWS credentials are active.
- Terraform output is available.
- Raw AIS sample exists in S3.
- Port reference CSV exists in S3.
- Glue jobs exist.
- Step Functions state machine exists.

After running the pipeline:

- Step Functions status is SUCCEEDED.
- Bronze output exists.
- Silver Clean output exists.
- Silver Port Proximity output exists.
- Silver Vessel Stops output exists.
- Athena validation queries return expected results.
- Gold Port Congestion table returns 5 MVP ports.