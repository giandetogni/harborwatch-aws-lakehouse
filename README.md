# HarborWatch — AWS Lakehouse for Maritime Supply Chain Risk Intelligence

![CI](https://github.com/giandetogni/harborwatch-aws-lakehouse/actions/workflows/ci.yml/badge.svg)

HarborWatch is a data engineering project that transforms public AIS vessel tracking data into port congestion and maritime supply chain risk intelligence.

The project ingests raw vessel position data, standardizes it into a Bronze layer, validates and enriches it into Silver datasets, applies geospatial processing near major US ports, and produces Gold analytical tables for congestion and anomaly monitoring.

## Problem

Port congestion affects supply chain reliability. Raw AIS vessel tracking data is large, noisy, geospatial, time-dependent, and difficult to analyze directly.

HarborWatch turns raw maritime data into structured, quality-controlled, analytics-ready datasets that can support port congestion analysis, dwell time monitoring, vessel anomaly detection, and operational risk intelligence.

## Current Status

HarborWatch has a working local MVP and an AWS-deployed MVP.

### Implemented locally

- Raw AIS ingestion from public NOAA / MarineCadastre data
- Full-file profiling of 7.29M AIS records
- Reproducible random sample generation with 500,000 records
- Bronze standardized AIS messages
- Silver row-level data quality classification
- Silver port proximity enrichment
- Silver vessel stop detection
- Gold port congestion metrics
- Gold vessel anomaly table
- Unit tests for geospatial, quality, and congestion rules
- Local pipeline orchestration through Makefile
- CI with GitHub Actions

### Implemented on AWS

- Terraform-managed S3 lakehouse bucket
- Private S3 Raw, Bronze, Silver, Gold, scripts, and Athena results prefixes
- Glue Data Catalog database
- Athena workgroup
- AWS Glue Raw-to-Bronze job
- AWS Glue Bronze-to-Silver Clean job
- AWS Glue Silver-to-Port-Proximity job
- AWS Glue Port-Proximity-to-Vessel-Stops job
- Silver Data Quality Report
- Silver Port Proximity geospatial enrichment
- Silver Vessel Stops with dwell time
- AWS-native Gold Port Congestion table
- Step Functions orchestration for the Glue pipeline
- Terraform-managed IAM roles and policies
- AWS validation screenshots
- Cost estimate, runbook, incident response, data dictionary, and architecture documentation

### Not implemented yet

- Apache Iceberg table migration
- AWS-native vessel anomaly generation
- EventBridge scheduled execution
- CloudWatch alarms
- Dashboard layer

## Data Source

The project uses public AIS vessel tracking data from NOAA / MarineCadastre.

Local source file:

```text
AIS_2024_01_01.zip
```

Full source profile:

```text
Total records scanned: 7,296,275
Rejected records: 16,875
Full-file rejection rate: 0.2313%
```

Analytical sample:

```text
Random sample size: 500,000 records
Valid records: 498,874
Rejected records: 1,126
Random sample rejection rate: 0.2252%
```

## MVP Port Scope

The MVP focuses on five US port areas:

- Los Angeles / Long Beach
- New York / New Jersey
- Houston
- Savannah
- Seattle / Tacoma

## Pipeline Design

```text
Raw AIS data
→ Bronze AIS messages
→ Silver vessel positions clean
→ Silver vessel port proximity
→ Silver vessel stops
→ Gold vessel anomalies
→ Gold port congestion daily
→ Athena queries
```

## Lakehouse Layers

### Raw

Original AIS files and local development samples.

### Bronze

Standardized AIS records with:

- deterministic message ID
- source file
- ingestion timestamp
- normalized column names
- raw payload hash
- year/month/day partition fields

### Silver

Cleaned and enriched datasets:

- `silver_vessel_positions_clean`
- `silver_vessel_port_proximity`
- `silver_vessel_stops`
- `silver_data_quality_report`

### Gold

Analytics-ready outputs:

- `gold_port_congestion_daily`
- `gold_vessel_anomalies`

## Data Quality

The pipeline checks:

- invalid latitude or longitude
- missing vessel identifier
- duplicate message ID
- future timestamp
- impossible speed
- unavailable AIS speed sentinel value

The AIS speed value `102.3` is treated as `speed_not_available`, not as a real speed.

Random sample quality results:

| Metric | Value |
|---|---:|
| Total records | 500,000 |
| Valid records | 498,874 |
| Rejected records | 1,126 |
| Rejection rate | 0.2252% |
| speed_not_available | 1,121 |
| impossible_speed | 3 |
| duplicate_message_id | 2 |

## Geospatial Processing

The MVP uses latitude and longitude to calculate:

- nearest MVP port
- distance to nearest port
- whether a vessel is within 20 km of a port
- stopped vessel episodes near ports
- dwell time in minutes

Current assumptions:

- port radius: 20 km
- stopped vessel threshold: speed lower than 1 knot
- minimum stop duration: 30 minutes
- maximum gap within same stop episode: 60 minutes

## Local MVP Results

### Port Proximity

| Port | Distinct Vessels | AIS Positions Within 20 km |
|---|---:|---:|
| Houston | 302 | 15,110 |
| Los Angeles / Long Beach | 324 | 9,730 |
| New York / New Jersey | 300 | 12,295 |
| Savannah | 79 | 2,804 |
| Seattle / Tacoma | 711 | 20,629 |

### Vessel Stops

| Port | Stops | Stopped Vessels | Avg Dwell Minutes |
|---|---:|---:|---:|
| Houston | 945 | 279 | 211.16 |
| Los Angeles / Long Beach | 1,078 | 272 | 126.38 |
| New York / New Jersey | 783 | 257 | 183.93 |
| Savannah | 235 | 64 | 167.32 |
| Seattle / Tacoma | 2,516 | 614 | 121.13 |

### Gold Port Congestion

| Port | Vessels Near Port | Stopped Vessels | Avg Dwell Minutes | P90 Dwell Minutes | Stopped Position Count | Anomaly Count | Port Congestion Index |
|---|---:|---:|---:|---:|---:|---:|---:|
| Houston | 302 | 279 | 211.16 | 494.16 | 13,400 | 0 | 0.6649 |
| Seattle / Tacoma | 711 | 614 | 121.13 | 228.02 | 19,626 | 23 | 0.6500 |
| New York / New Jersey | 300 | 257 | 183.93 | 428.91 | 9,834 | 44 | 0.4906 |
| Los Angeles / Long Beach | 324 | 272 | 126.38 | 254.97 | 8,856 | 2 | 0.2635 |
| Savannah | 79 | 64 | 167.32 | 339.20 | 2,610 | 13 | 0.1796 |

## Port Congestion Index

The MVP Port Congestion Index uses:

```text
0.40 * normalized_stopped_vessels
+ 0.35 * normalized_avg_dwell_time
+ 0.25 * normalized_stopped_position_count
```

Weather is not included in the MVP.

The score is relative to the selected sample and selected ports. It should not be interpreted as an absolute real-world congestion measurement.

## AWS End-to-End Pipeline Status

The AWS pipeline is operational and orchestrated through AWS Step Functions.

Validated AWS flow:

```text
S3 Raw AIS sample
→ AWS Glue Raw-to-Bronze
→ Bronze Parquet
→ AWS Glue Bronze-to-Silver Clean
→ Silver Clean Parquet
→ Silver Data Quality Report
→ AWS Glue Silver-to-Port-Proximity
→ Silver Port Proximity Parquet
→ AWS Glue Port-Proximity-to-Vessel-Stops
→ Silver Vessel Stops Parquet
→ Athena Gold Port Congestion Daily
```

AWS orchestration:

- Step Functions state machine: `harborwatch-dev-lakehouse-pipeline`
- Step Functions execution status: `SUCCEEDED`
- Orchestrated Glue jobs:
  - `harborwatch-dev-raw-to-bronze`
  - `harborwatch-dev-bronze-to-silver-clean`
  - `harborwatch-dev-silver-to-port-proximity`
  - `harborwatch-dev-port-proximity-to-vessel-stops`

Latest AWS validation results:

- AIS sample size: 10,000 records
- Silver Data Quality Report: 1,000 total records, 997 valid, 3 rejected, 0.003 rejection rate
- Silver Port Proximity: geospatial distance to MVP ports calculated with Haversine distance
- Silver Vessel Stops detected: 26
- AWS-native Gold table returned 5 MVP ports
- Final Step Functions output path: `s3://harborwatch-dev-lakehouse-giandetogni/silver/vessel_stops/`

AWS-native Gold Port Congestion ranking:

| Port | Vessels Near Port | Stopped Vessels | Avg Dwell Minutes | P90 Dwell Minutes | Stopped Position Count | Data Quality Rejection Rate | Port Congestion Index |
|---|---:|---:|---:|---:|---:|---:|---:|
| Houston | 175 | 12 | 42.02 | 51.50 | 281 | 0.003 | 0.6405 |
| Seattle / Tacoma | 278 | 8 | 40.50 | 54.00 | 384 | 0.003 | 0.5045 |
| New York / New Jersey | 155 | 1 | 47.97 | 47.97 | 191 | 0.003 | 0.4487 |
| Los Angeles / Long Beach | 119 | 4 | 44.40 | 57.83 | 173 | 0.003 | 0.3765 |
| Savannah | 43 | 1 | 41.85 | 41.85 | 65 | 0.003 | 0.0633 |

Current AWS limitation:

- AWS-native vessel anomaly generation is not implemented yet, so `anomaly_count` is currently set to `0` in the AWS-native Gold table.
- Apache Iceberg migration is still planned.

## AWS Deployment

The AWS MVP is deployed with Terraform and validated through AWS Glue, Athena, S3, and Step Functions.

### Terraform-managed resources

- Private S3 lakehouse bucket
- Raw, Bronze, Silver, Gold, scripts, and Athena results prefixes
- Glue Data Catalog database
- Athena workgroup
- AWS Glue ETL jobs
- Glue job scripts uploaded to S3
- IAM roles and policies for Glue and Step Functions
- Step Functions state machine

### S3 bucket

`harborwatch-dev-lakehouse-giandetogni`

### Main S3 prefixes

- `raw/`
- `bronze/`
- `silver/`
- `gold/`
- `scripts/`
- `athena-results/`

### Glue Data Catalog database

`harborwatch_lakehouse`

### AWS Glue jobs

- `harborwatch-dev-raw-to-bronze`
- `harborwatch-dev-bronze-to-silver-clean`
- `harborwatch-dev-silver-to-port-proximity`
- `harborwatch-dev-port-proximity-to-vessel-stops`

### Step Functions

State machine:

- `harborwatch-dev-lakehouse-pipeline`

Validated execution:

- Status: `SUCCEEDED`
- Final output: `s3://harborwatch-dev-lakehouse-giandetogni/silver/vessel_stops/`

### Athena validation

Validated AWS tables include:

- `harborwatch_lakehouse.silver_vessel_positions_clean`
- `harborwatch_lakehouse.silver_data_quality_report`
- `harborwatch_lakehouse.silver_vessel_port_proximity`
- `harborwatch_lakehouse.silver_vessel_stops`
- `harborwatch_lakehouse.gold_port_congestion_daily_aws`

Current AWS validation highlights:

- Silver Data Quality: 997 valid records, 3 rejected records in the initial 1k validation
- Silver Vessel Stops: 26 detected stops from the 10k AWS sample
- Gold Port Congestion: 5 MVP ports returned
- Step Functions orchestration: `SUCCEEDED`

## How to Run Locally

The local MVP pipeline can be executed with `make`.

### Run the full local pipeline

```bash
make run-local
```

### Show current Gold outputs

```bash
make show-results
```

### Clean generated outputs

```bash
make clean-outputs
```

The full local pipeline executes:

```text
1. Create random AIS sample
2. Raw to Bronze
3. Bronze quality profiling
4. Bronze to Silver clean positions
5. Silver positions to port proximity
6. Port proximity to vessel stops
7. Silver to Gold vessel anomalies
8. Silver to Gold port congestion
```

## Tests

Run tests locally:

```bash
python -m pytest
```

The current test suite covers:

- haversine distance calculation
- latitude and longitude validation
- AIS speed sentinel handling
- impossible speed detection
- min-max normalization
- Port Congestion Index calculation

CI runs automatically through GitHub Actions on push and pull request.

## Terraform

Terraform files are located in:

```text
terraform/
```

Current Terraform scope:

- S3 lakehouse bucket
- S3 public access block
- S3 server-side encryption
- S3 versioning
- Raw/Bronze/Silver/Gold/Scripts/Athena prefixes
- Glue Data Catalog database
- Glue job script uploads
- AWS Glue ETL jobs
- Athena workgroup
- IAM roles and policies
- Step Functions state machine
- Terraform outputs

Validate Terraform:

```bash
cd terraform
terraform fmt
terraform validate
```

Review plan:

```bash
terraform plan
```

Apply infrastructure:

```bash
terraform apply
```

Do not commit:

- `terraform.tfstate`
- `terraform.tfstate.backup`
- `terraform.tfvars`
- AWS access keys
- local data files

## Repository Structure

```text
harborwatch-aws-lakehouse/
├── .github/
│   └── workflows/
├── architecture/
├── data/
│   └── raw/
├── docs/
├── sql/
├── src/
│   ├── geospatial/
│   ├── glue_jobs/
│   ├── ingestion/
│   ├── metrics/
│   └── quality/
├── terraform/
├── tests/
├── Makefile
└── README.md
```

## Documentation

Additional documentation:

- docs/assumptions.md
- docs/local_mvp_results.md
- docs/aws_deployment.md
- architecture/local_mvp_architecture.md
- architecture/aws_target_architecture.md
- sql/create_athena_gold_tables.sql
- docs/cost_estimate.md
- docs/runbook.md
- docs/incident_response.md
- evidence/validation_summary.md
- docs/data_dictionary.md
- docs/release_checklist.md
- architecture/tradeoffs.md
- evidence/screenshots_guide.md
- evidence/screenshots/

## Evidence

Validation evidence and operational proof are available in:

- `evidence/validation_summary.md`
- `evidence/screenshots_guide.md`
- `evidence/screenshots/`

The current AWS MVP has validated:

- Step Functions execution with `SUCCEEDED`
- AWS Glue jobs running end-to-end
- Silver Data Quality Report
- Silver Port Proximity geospatial enrichment
- Silver Vessel Stops with 26 detected stops
- AWS-native Gold Port Congestion table with 5 MVP ports

## Security

Current security choices:

- S3 public access is blocked.
- S3 server-side encryption is enabled with AES256.
- Terraform state and variable files are ignored by Git.
- AWS credentials are not stored in the repository.
- Generated local data outputs are ignored by Git.

## Current Limitations

- Apache Iceberg is not implemented yet.
- AWS-native vessel anomaly generation is not implemented yet.
- AWS-native Gold currently sets `anomaly_count` to `0`.
- Weather is not included in the AWS-native Gold table.
- Port proximity is point-based using representative coordinates and a 20 km radius, not official port polygons.
- Stop detection is rule-based and approximate.
- The AWS execution uses bounded AIS samples for cost control.
- The Port Congestion Index is relative to the selected sample and MVP ports.
- The pipeline is batch-oriented, not real-time streaming.
- EventBridge scheduling and CloudWatch alarms are not implemented yet.
- A dashboard is not implemented yet.

## Trade-offs

### Batch instead of streaming

AIS data can be processed in batch for the MVP. Streaming would add complexity without enough return at this stage.

### Athena before Redshift

Athena is sufficient for querying small Gold outputs and validating the lakehouse path. Redshift Serverless is unnecessary for the current scope.

### Step Functions before Airflow

Step Functions is the target orchestrator for AWS because the pipeline scope is small and AWS-native. Airflow would be overkill for the MVP.

### Point-radius proximity before polygons

The MVP uses a 20 km radius around port coordinates. A production-grade version should use port polygons, terminals, anchorages, and shipping lanes.

## Next Steps

- Migrate Bronze, Silver, and Gold tables to Apache Iceberg.
- Add AWS-native vessel anomaly generation.
- Join AWS-native anomaly counts into the Gold congestion table.
- Add EventBridge scheduled execution.
- Add CloudWatch alarms and operational metrics.
- Add S3 lifecycle policies for temporary outputs.
- Add a lightweight dashboard using Streamlit or QuickSight.
- Improve CI with Terraform formatting checks and linting.