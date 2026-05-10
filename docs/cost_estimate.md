# HarborWatch Cost Estimate

## Scope

This document estimates the expected AWS cost for the HarborWatch MVP.

The current MVP processes a bounded AIS sample and is designed for portfolio demonstration, not production-scale continuous processing.

## Current AWS Components

The deployed AWS components are:

- Amazon S3
- AWS Glue Data Catalog
- AWS Glue Spark Jobs
- Amazon Athena
- AWS Step Functions
- IAM roles and policies

## Main Cost Drivers

### AWS Glue

AWS Glue is the main cost driver.

The current pipeline uses four Glue Spark jobs:

- Raw to Bronze
- Bronze to Silver Clean
- Silver to Port Proximity
- Port Proximity to Vessel Stops

Each job currently uses:

- Glue version: 4.0
- Worker type: G.1X
- Number of workers: 2

Cost driver: Glue cost is driven by DPU-hours consumed by job runs.

The MVP keeps input samples small to control Glue runtime and cost.

### Amazon Athena

Athena is used for SQL validation and Gold table generation.

Cost driver: Athena cost is driven by the amount of data scanned by queries.

Cost control choices:

- Parquet output for AWS pipeline layers
- Small sample size
- Partitioned outputs by year and month
- Workgroup-level query result configuration
- 1 GB bytes scanned cutoff per query

### Amazon S3

S3 stores:

- Raw AIS input samples
- Bronze Parquet
- Silver Parquet
- Gold Parquet
- Athena query results
- Glue job scripts

Cost driver: S3 cost is driven by storage size, request volume, and data transfer.

For the MVP, S3 cost is expected to remain very low because the dataset is small.

### AWS Step Functions

Step Functions orchestrates the Glue jobs.

Cost driver: Step Functions cost is driven by the number of state transitions.

The MVP state machine has a small number of states and is executed manually, so Step Functions cost is expected to be minimal.

## Current MVP Cost Controls

The project uses the following controls to reduce cost:

- Small AIS sample for AWS execution
- Glue jobs with 2 G.1X workers
- Short Glue timeout
- Athena workgroup with enforced output location
- Athena query scan cutoff
- Parquet outputs instead of repeated CSV scanning
- No Redshift Serverless
- No streaming service
- No always-on compute
- No dashboard service running continuously

## Services Intentionally Avoided

The MVP does not use:

- Redshift Serverless
- MSK or Kafka
- Kinesis streaming
- MWAA or Airflow
- Kubernetes or EKS
- Always-on EC2
- SageMaker
- OpenSearch

These services would increase cost and complexity without improving the MVP enough for the current portfolio goal.

## Expected Cost Profile

For occasional portfolio demonstration runs, the expected monthly cost should remain low.

The largest cost risk is repeated AWS Glue execution.

A conservative operating pattern is:

- Run the full Step Functions pipeline only when needed
- Avoid rerunning Glue jobs repeatedly during development
- Delete temporary outputs when no longer needed
- Keep samples small unless validating scale behavior

## Cost Risk Areas

| Risk | Impact | Mitigation |
|---|---:|---|
| Repeated Glue job runs | High | Run only when validating changes |
| Large AIS input files | High | Use bounded samples for MVP |
| Athena scanning CSV repeatedly | Medium | Use Parquet and partitions |
| Accidental large query scans | Medium | Keep Athena bytes scanned cutoff |
| Unused S3 outputs accumulating | Low | Periodically clean development prefixes |
| Adding Redshift too early | High | Avoid until clear analytical need exists |

## MVP Cost Position

The current architecture is cost-appropriate for a portfolio project.

The cost posture is strong because the project uses serverless AWS services, avoids always-on infrastructure, and limits compute-heavy work to explicit Glue job runs.

## Future Cost Improvements

Potential improvements:

- Add lifecycle rules for temporary Athena results
- Add S3 lifecycle rules for development outputs
- Parameterize sample size
- Track job runtime and DPUSeconds in documentation
- Add a cost monitoring alarm
- Use Iceberg compaction carefully if table size grows