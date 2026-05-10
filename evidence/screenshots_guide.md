# HarborWatch Screenshots Guide

## Purpose

This folder stores visual evidence that the HarborWatch AWS lakehouse pipeline runs end-to-end.

Screenshots should prove that the project is not only documented, but actually deployed and validated on AWS.

## Required Screenshots

## 1. Step Functions Execution

File name:

- `01_step_functions_succeeded.png`

What to capture:

- State machine name: `harborwatch-dev-lakehouse-pipeline`
- Execution status: `SUCCEEDED`
- Visual workflow graph if available
- States showing the Glue jobs in sequence

Why it matters:

- Proves AWS orchestration works end-to-end.

## 2. Glue Jobs

File name:

- `02_glue_jobs_successful_runs.png`

What to capture:

- Glue jobs list or job run history
- Jobs:
  - `harborwatch-dev-raw-to-bronze`
  - `harborwatch-dev-bronze-to-silver-clean`
  - `harborwatch-dev-silver-to-port-proximity`
  - `harborwatch-dev-port-proximity-to-vessel-stops`
- Successful run status

Why it matters:

- Proves the transformations ran on AWS Glue.

## 3. Athena Gold Query Result

File name:

- `03_athena_gold_port_congestion.png`

What to capture:

- Athena query result for `harborwatch_lakehouse.gold_port_congestion_daily_aws`
- Query ordered by `port_congestion_index DESC`
- Five MVP ports visible
- `port_congestion_index` visible

Expected result:

- Houston ranked highest in the current AWS sample
- Five MVP ports returned

Why it matters:

- Proves the AWS-native Gold analytical output exists.

## 4. Athena Vessel Stops Validation

File name:

- `04_athena_vessel_stops.png`

What to capture:

- Athena query result showing `stop_count`

Expected result:

- `stop_count = 26`

Why it matters:

- Proves dwell time and vessel stop detection work in AWS.

## 5. S3 Lakehouse Prefixes

File name:

- `05_s3_lakehouse_prefixes.png`

What to capture:

- S3 bucket: `harborwatch-dev-lakehouse-giandetogni`
- Prefixes:
  - `raw/`
  - `bronze/`
  - `silver/`
  - `gold/`
  - `athena-results/`
  - `scripts/`

Why it matters:

- Proves the lakehouse storage layout exists in S3.

## 6. GitHub Actions CI

File name:

- `06_github_actions_ci.png`

What to capture:

- GitHub Actions workflow passing
- Python tests passing

Why it matters:

- Proves basic CI and test automation.

## 7. Terraform Outputs

File name:

- `07_terraform_outputs.png`

What to capture:

- `terraform output`
- Outputs for:
  - S3 bucket
  - Glue database
  - Glue jobs
  - Step Functions state machine
  - Athena workgroup

Why it matters:

- Proves infrastructure is managed as code.

## Screenshot Rules

Do not expose:

- AWS access keys
- Secret values
- Local credentials
- Sensitive environment variables

Acceptable but optional to blur:

- AWS account ID
- Personal email
- Browser profile name

## Recommended README Usage

The README should include a short Evidence section pointing reviewers to the validation files.

Recommended README text:

Evidence and validation artifacts are available in:

- `evidence/validation_summary.md`
- `evidence/screenshots/`

This keeps the README clean while preserving detailed validation evidence in dedicated files.

## Current Screenshot Status

| Screenshot | Status |
|---|---|
| Step Functions succeeded | Added |
| Glue jobs successful runs | Added |
| Athena Gold result | Added |
| Athena vessel stops validation | Added |
| S3 lakehouse prefixes | Added |
| GitHub Actions CI | Added |
| Terraform outputs | Added |

## Notes

Screenshots are not required for the pipeline to work, but they are important for public portfolio presentation.

A reviewer should be able to open the repository and quickly verify that:

- AWS infrastructure exists
- The pipeline ran successfully
- Glue jobs transformed data
- Athena queried analytical outputs
- Step Functions orchestrated the pipeline
- The project has real validation evidence