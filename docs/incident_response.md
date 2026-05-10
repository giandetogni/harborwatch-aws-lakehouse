# HarborWatch Incident Response

## Purpose

This document defines how to respond to operational incidents in the HarborWatch AWS lakehouse MVP.

The goal is to quickly identify failures, limit unnecessary AWS cost, preserve useful evidence, and restore the pipeline to a valid state.

## Incident Severity Levels

| Severity | Definition | Example |
|---|---|---|
| SEV-1 | Pipeline cannot run end-to-end | Step Functions fails before completion |
| SEV-2 | Pipeline runs but output is invalid | Gold table returns missing or incorrect ports |
| SEV-3 | Non-critical validation issue | Documentation mismatch or delayed Athena query |
| SEV-4 | Cosmetic or low-impact issue | README typo or old query result artifact |

## Primary Incident Types

## 1. Step Functions Execution Failure

### Symptoms

- Step Functions status is FAILED
- One of the Glue job states fails
- Pipeline does not reach vessel stops output

### Immediate Checks

Run:

aws stepfunctions describe-execution --execution-arn EXECUTION_ARN --region us-east-1 --no-cli-pager

Then inspect the execution history:

aws stepfunctions get-execution-history --execution-arn EXECUTION_ARN --region us-east-1 --reverse-order --max-results 20 --no-cli-pager

### Likely Causes

- Glue job failure
- IAM permission issue
- Missing S3 input path
- Invalid script uploaded to S3
- Incorrect Terraform configuration

### Response

1. Identify the failed state.
2. Extract the failed Glue job name and JobRunId.
3. Inspect the Glue job run.
4. Fix the root cause.
5. Re-run the Step Functions pipeline.
6. Validate final outputs in S3 and Athena.

---

## 2. Glue Job Failure

### Symptoms

- Glue job state is FAILED
- Step Functions fails at a Glue task
- Expected Parquet output is missing

### Immediate Checks

Run:

aws glue get-job-run --job-name JOB_NAME --run-id JOB_RUN_ID --region us-east-1 --no-cli-pager

Check:

- JobRunState
- ErrorMessage
- StartedOn
- CompletedOn
- ExecutionTime
- DPUSeconds

### Likely Causes

- Input path does not exist
- Script error
- Schema mismatch
- IAM role lacks S3 access
- Output path conflict
- Bad data type conversion

### Response

1. Confirm input data exists in S3.
2. Confirm Glue script exists in scripts/glue/.
3. Check CloudWatch logs.
4. Fix the script or Terraform configuration.
5. Re-apply Terraform if the script or job definition changed.
6. Re-run only the failed job first.
7. If successful, re-run the full Step Functions pipeline.

---

## 3. Missing S3 Output

### Symptoms

- Glue job succeeds but expected S3 prefix is empty
- Athena table returns zero rows
- Downstream job has no input data

### Immediate Checks

Run:

aws s3 ls s3://harborwatch-dev-lakehouse-giandetogni/bronze/ais_messages/ --recursive

aws s3 ls s3://harborwatch-dev-lakehouse-giandetogni/silver/vessel_positions_clean/ --recursive

aws s3 ls s3://harborwatch-dev-lakehouse-giandetogni/silver/vessel_port_proximity/ --recursive

aws s3 ls s3://harborwatch-dev-lakehouse-giandetogni/silver/vessel_stops/ --recursive

### Likely Causes

- Empty input sample
- Filtering removed all rows
- Vessel stop detection sample too sparse
- Output prefix overwritten
- Job wrote to unexpected path

### Response

1. Confirm upstream output exists.
2. Validate row counts in Athena.
3. Inspect filtering logic.
4. Increase sample size if temporal density is insufficient.
5. Re-run the pipeline.

---

## 4. Athena Table Not Found

### Symptoms

- Athena returns TABLE_NOT_FOUND
- Query fails for an expected table

### Likely Causes

- Table creation SQL was not executed
- Wrong database selected
- Table name mismatch
- Terraform does not manage the table
- Manual Athena table was dropped

### Response

1. Confirm database is harborwatch_lakehouse.
2. Re-run the relevant SQL file from the sql/ folder.
3. If table is partitioned, run MSCK REPAIR TABLE.
4. Re-run validation query.

Example:

MSCK REPAIR TABLE harborwatch_lakehouse.silver_vessel_stops;

---

## 5. Athena Query Still Running

### Symptoms

- get-query-results fails because query is still RUNNING

### Response

1. Check query status:

aws athena get-query-execution --region us-east-1 --query-execution-id QUERY_ID --query "QueryExecution.Status" --output json --no-cli-pager

2. Wait until SUCCEEDED.
3. Run get-query-results again.

This is not a pipeline failure. It usually means the result was requested too quickly.

---

## 6. Incorrect Data Quality Results

### Symptoms

- Valid/rejected counts are unexpected
- Rejection rate changes significantly
- speed_not_available count is abnormal

### Immediate Checks

Run:

SELECT
  quality_status,
  COUNT(*) AS row_count
FROM harborwatch_lakehouse.silver_vessel_positions_clean
GROUP BY quality_status
ORDER BY quality_status;

Then inspect rejection reasons:

SELECT
  rejection_reason,
  COUNT(*) AS row_count
FROM harborwatch_lakehouse.silver_vessel_positions_clean
WHERE quality_status = 'rejected'
GROUP BY rejection_reason
ORDER BY row_count DESC;

### Likely Causes

- Input sample changed
- AIS sentinel values changed
- Data quality rule changed
- Schema conversion issue

### Response

1. Compare current results with docs/aws_deployment.md.
2. Inspect rejected records.
3. Confirm rules in the Glue script.
4. Update documentation if the new sample is intentionally different.

---

## 7. Vessel Stops Missing or Too Low

### Symptoms

- silver_vessel_stops returns zero rows
- Stop count is much lower than expected

### Likely Causes

- AIS sample too small
- Random sample lacks temporal continuity
- Vessels have only one stopped message
- Gap between messages exceeds threshold
- Dwell threshold is too strict for the sample

### Response

1. Validate candidate stopped positions:

SELECT
  COUNT(*) AS candidate_stopped_positions,
  COUNT(DISTINCT mmsi) AS distinct_vessels
FROM harborwatch_lakehouse.silver_vessel_port_proximity
WHERE is_within_port_radius = true
  AND speed_knots < 1;

2. Validate temporal density:

SELECT
  mmsi,
  nearest_port_name,
  COUNT(*) AS stopped_messages,
  MIN(event_timestamp) AS first_timestamp,
  MAX(event_timestamp) AS last_timestamp,
  date_diff('minute', MIN(event_timestamp), MAX(event_timestamp)) AS raw_time_span_minutes
FROM harborwatch_lakehouse.silver_vessel_port_proximity
WHERE is_within_port_radius = true
  AND speed_knots < 1
GROUP BY mmsi, nearest_port_name
ORDER BY stopped_messages DESC, raw_time_span_minutes DESC
LIMIT 20;

3. If temporal density is insufficient, increase the sample size.
4. Re-run the pipeline.

---

## 8. Gold Table Looks Wrong

### Symptoms

- Gold table returns fewer than 5 ports
- Port Congestion Index is null
- Data quality rejection rate is missing
- Stopped vessels are all zero

### Immediate Checks

Validate source tables:

SELECT COUNT(*) FROM harborwatch_lakehouse.silver_vessel_port_proximity;

SELECT COUNT(*) FROM harborwatch_lakehouse.silver_vessel_stops;

SELECT * FROM harborwatch_lakehouse.silver_data_quality_report;

### Likely Causes

- Silver source table empty
- Gold insert ran before Silver tables were refreshed
- Data quality report missing
- Join key mismatch
- Output prefix conflict

### Response

1. Validate all Silver source tables.
2. Re-run Gold insert SQL.
3. Query Gold table again.
4. Document any intentional sample changes.

---

## 9. Terraform Drift or Apply Failure

### Symptoms

- terraform plan shows unexpected changes
- terraform apply fails
- AWS resource exists but Terraform does not recognize it

### Response

1. Run:

cd terraform
terraform fmt
terraform validate
terraform plan

2. If plan shows unexpected destroy actions, stop.
3. Inspect the changed resource.
4. Do not manually delete resources unless the impact is understood.
5. Fix Terraform configuration or import resource if needed.

---

## Escalation Checklist

Before considering an incident resolved:

- Root cause is identified.
- Failed job or query has been rerun successfully.
- Step Functions execution returns SUCCEEDED if orchestration was involved.
- S3 output exists.
- Athena validation query returns expected result.
- Documentation is updated if behavior changed.

## Current Recovery Baseline

A healthy HarborWatch AWS MVP should show:

- Step Functions execution status: SUCCEEDED
- Silver vessel stops count: 26 for the current 10k sample
- Gold Port Congestion table returns 5 MVP ports
- Data Quality report returns a non-null rejection rate
- No unexpected Terraform drift

## Known Limitations

- This MVP is not production monitored.
- There is no automated alerting yet.
- Gold anomaly_count is currently set to 0.
- Apache Iceberg is not implemented yet.
- Port radius uses simplified point-based geospatial logic.
- Weather is not included in the current AWS-native Gold table.