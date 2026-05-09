# HarborWatch — AWS Lakehouse for Maritime Supply Chain Risk Intelligence

![CI](https://github.com/giandetogni/harborwatch-aws-lakehouse/actions/workflows/ci.yml/badge.svg)

HarborWatch is a data engineering project that transforms public AIS vessel tracking data into port congestion and maritime supply chain risk intelligence.

The project ingests raw vessel position data, standardizes it into a Bronze layer, validates and enriches it into Silver datasets, applies geospatial processing near major US ports, and produces Gold analytical tables for congestion and anomaly monitoring.

## Problem

Port congestion affects supply chain reliability. Raw AIS vessel tracking data is large, noisy, geospatial, time-dependent, and difficult to analyze directly.

HarborWatch turns raw maritime data into structured, quality-controlled, analytics-ready datasets that can support port congestion analysis, dwell time monitoring, vessel anomaly detection, and operational risk intelligence.

## Current Status

The project currently has a working local MVP and an initial AWS foundation.

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
- Local architecture and assumptions documentation

### Implemented on AWS

- Terraform foundation for S3 and Glue Data Catalog
- Private S3 lakehouse bucket
- Raw, Bronze, Silver, Gold, and Athena results prefixes
- Glue Data Catalog database
- Gold CSV outputs uploaded to S3
- Athena external tables for Gold congestion and vessel anomalies
- Athena validation queries returning port congestion and anomaly results

### Planned next

- Terraform-managed Athena workgroup
- AWS Glue ETL jobs
- Apache Iceberg tables
- Step Functions orchestration
- CloudWatch logging and monitoring
- Cost estimate and operational runbook
- Dashboard or query result screenshots

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

## AWS Deployment

The current AWS foundation was provisioned with Terraform.

Created resources:

- S3 lakehouse bucket
- Raw zone prefix
- Bronze zone prefix
- Silver zone prefix
- Gold zone prefix
- Athena results prefix
- Glue Data Catalog database

S3 bucket:

```text
harborwatch-dev-lakehouse-giandetogni
```

S3 prefixes:

```text
athena-results/
bronze/
gold/
raw/
silver/
```

Glue database:

```text
harborwatch_lakehouse
```

Gold outputs uploaded to S3:

```text
s3://harborwatch-dev-lakehouse-giandetogni/gold/gold_port_congestion_daily/date=2024-01-01/gold_port_congestion_daily.csv
s3://harborwatch-dev-lakehouse-giandetogni/gold/gold_vessel_anomalies/date=2024-01-01/gold_vessel_anomalies.csv
```

## Athena Validation

Athena external tables were created for:

- `harborwatch_lakehouse.gold_port_congestion_daily`
- `harborwatch_lakehouse.gold_vessel_anomalies`

Validated query:

```sql
SELECT *
FROM harborwatch_lakehouse.gold_port_congestion_daily
ORDER BY port_congestion_index DESC;
```

Result: 5 MVP ports returned.

Validated anomaly query:

```sql
SELECT
  nearest_port_name,
  anomaly_type,
  severity,
  COUNT(*) AS anomaly_count
FROM harborwatch_lakehouse.gold_vessel_anomalies
WHERE is_within_port_radius = 'True'
GROUP BY nearest_port_name, anomaly_type, severity
ORDER BY anomaly_count DESC;
```

Result:

| Port | Anomaly Type | Severity | Count |
|---|---|---|---:|
| New York / New Jersey | speed_not_available | low | 44 |
| Seattle / Tacoma | speed_not_available | low | 23 |
| Savannah | speed_not_available | low | 13 |
| Los Angeles / Long Beach | speed_not_available | low | 2 |

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
- Raw/Bronze/Silver/Gold/Athena prefixes
- Glue Data Catalog database
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

- `docs/assumptions.md`
- `docs/local_mvp_results.md`
- `docs/aws_deployment.md`
- `architecture/local_mvp_architecture.md`
- `architecture/aws_target_architecture.md`
- `sql/create_athena_gold_tables.sql`

## Security

Current security choices:

- S3 public access is blocked.
- S3 server-side encryption is enabled with AES256.
- Terraform state and variable files are ignored by Git.
- AWS credentials are not stored in the repository.
- Generated local data outputs are ignored by Git.

## Current Limitations

- Local MVP uses CSV files, not Iceberg tables yet.
- AWS Glue ETL jobs are not implemented yet.
- Port proximity is point-based, not polygon-based.
- Stop detection is rule-based and approximate.
- Only one AIS day is used.
- Local analytical outputs are based on a random sample, not the full dataset.
- The Port Congestion Index is relative to the sample and MVP ports.
- Athena currently queries external CSV Gold tables, not Iceberg tables.

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

- Add Terraform-managed Athena workgroup
- Port local CSV transformations to AWS Glue jobs
- Store Bronze, Silver, and Gold tables as Apache Iceberg
- Orchestrate the AWS pipeline with Step Functions
- Add CloudWatch logging and pipeline monitoring
- Add cost estimate and operational runbook
- Add dashboard or query result screenshots