# HarborWatch AWS Target Architecture

## Purpose

This document describes the current AWS target architecture for HarborWatch.

HarborWatch is an AWS lakehouse project for maritime supply chain risk intelligence. It processes public AIS vessel tracking data, validates data quality, enriches vessel positions with geospatial port proximity, detects vessel stop episodes, and produces Gold congestion metrics through Athena.

## Architecture Summary

The current AWS implementation uses a serverless batch-oriented lakehouse architecture.

Main AWS services:

- Amazon S3 for lakehouse storage
- AWS Glue Spark Jobs for data transformation
- AWS Glue Data Catalog for table metadata
- Amazon Athena for SQL validation and Gold analytics
- AWS Step Functions for orchestration
- IAM for least-privilege execution roles
- Terraform for infrastructure as code
- GitHub Actions for CI validation

## Data Flow

The AWS data flow is:

1. Public AIS sample is uploaded to S3 Raw.
2. AWS Glue transforms Raw CSV into Bronze Parquet.
3. AWS Glue applies data quality rules and creates Silver Clean Parquet.
4. Athena materializes the Silver Data Quality Report.
5. AWS Glue enriches Silver Clean records with nearest-port geospatial distance.
6. AWS Glue detects vessel stop episodes near MVP ports.
7. Athena produces AWS-native Gold Port Congestion metrics.
8. Step Functions orchestrates the Glue pipeline end-to-end.

## Lakehouse Layers

## Raw Layer

Purpose:

- Store source AIS data with minimal modification.
- Preserve traceability to the original public dataset.

Current S3 prefix:

- s3://harborwatch-dev-lakehouse-giandetogni/raw/

Current inputs:

- AIS sample files
- Port reference CSV

## Bronze Layer

Purpose:

- Standardize raw AIS records.
- Generate deterministic message IDs.
- Cast source fields into consistent analytical types.
- Add source_file and ingestion_timestamp metadata.

Current S3 prefix:

- s3://harborwatch-dev-lakehouse-giandetogni/bronze/ais_messages/

Current format:

- Parquet
- Partitioned by year and month

Athena table:

- harborwatch_lakehouse.bronze_ais_messages

## Silver Layer

Purpose:

- Apply data quality rules.
- Keep clean and auditable records.
- Add geospatial enrichment.
- Detect stop episodes and dwell time.

Current Silver outputs:

- silver_vessel_positions_clean
- silver_data_quality_report
- silver_vessel_port_proximity
- silver_vessel_stops

Current S3 prefixes:

- s3://harborwatch-dev-lakehouse-giandetogni/silver/vessel_positions_clean/
- s3://harborwatch-dev-lakehouse-giandetogni/silver/data_quality_report/
- s3://harborwatch-dev-lakehouse-giandetogni/silver/vessel_port_proximity/
- s3://harborwatch-dev-lakehouse-giandetogni/silver/vessel_stops/

## Gold Layer

Purpose:

- Produce analytics-ready metrics for port congestion monitoring.

Current Gold table:

- gold_port_congestion_daily_aws

Current S3 prefix:

- s3://harborwatch-dev-lakehouse-giandetogni/gold/port_congestion_daily_aws/

Current metrics:

- vessels_near_port
- stopped_vessels
- avg_dwell_time_minutes
- p90_dwell_time_minutes
- stopped_position_count
- anomaly_count
- data_quality_rejection_rate
- port_congestion_index

## Orchestration

AWS Step Functions orchestrates the Glue jobs.

State machine:

- harborwatch-dev-lakehouse-pipeline

Orchestrated jobs:

1. harborwatch-dev-raw-to-bronze
2. harborwatch-dev-bronze-to-silver-clean
3. harborwatch-dev-silver-to-port-proximity
4. harborwatch-dev-port-proximity-to-vessel-stops

The Gold table is currently generated through Athena SQL after the Silver outputs are produced.

## Infrastructure as Code

Terraform manages the core AWS infrastructure:

- S3 bucket and prefixes
- Glue Data Catalog database
- Glue jobs
- Glue job script uploads
- IAM roles and policies
- Athena workgroup
- Step Functions state machine
- Terraform outputs

Terraform files:

- providers.tf
- variables.tf
- locals.tf
- outputs.tf
- s3.tf
- glue.tf
- glue_jobs.tf
- iam.tf
- athena.tf
- step_functions.tf

## Data Quality Architecture

Data quality is implemented in the Silver layer.

Rules include:

- Latitude must be between -90 and 90
- Longitude must be between -180 and 180
- MMSI cannot be null
- Future timestamps are rejected
- Duplicate message IDs are detected
- AIS speed sentinel 102.3 is treated as speed_not_available
- Negative or unreasonable speed values are rejected

Validated AWS result:

- 1,000 total records in initial AWS validation
- 997 valid records
- 3 rejected records
- 0.003 rejection rate

## Geospatial Architecture

Geospatial enrichment is performed by AWS Glue.

The pipeline:

1. Reads Silver Clean vessel positions.
2. Reads the MVP port reference CSV.
3. Cross joins valid vessel positions with MVP ports.
4. Calculates Haversine distance.
5. Selects the nearest port for each message.
6. Flags whether the vessel is within the 20 km MVP port radius.

MVP ports:

- Los Angeles / Long Beach
- New York / New Jersey
- Houston
- Savannah
- Seattle / Tacoma

## Vessel Stop Detection

Vessel stops are detected from Silver Port Proximity.

Rules:

- Vessel must be within 20 km of the nearest MVP port.
- speed_knots must be lower than 1.
- Consecutive stopped messages must have a maximum gap of 60 minutes.
- Stop duration must be at least 30 minutes.

Validated AWS result from the 10k sample:

- 26 vessel stops detected.

Stops by port:

- Houston: 12 stops
- Seattle / Tacoma: 8 stops
- Los Angeles / Long Beach: 4 stops
- New York / New Jersey: 1 stop
- Savannah: 1 stop

## Gold Port Congestion Index

The AWS-native Gold Port Congestion table calculates a relative congestion score across the MVP ports.

Current weights:

- 40% normalized stopped vessels
- 35% normalized average dwell time
- 25% normalized stopped position count

Weather is not included in the AWS MVP.

Current AWS-native Gold ranking:

| Port | Vessels Near Port | Stopped Vessels | Avg Dwell Minutes | Port Congestion Index |
|---|---:|---:|---:|---:|
| Houston | 175 | 12 | 42.02 | 0.6405 |
| Seattle / Tacoma | 278 | 8 | 40.50 | 0.5045 |
| New York / New Jersey | 155 | 1 | 47.97 | 0.4487 |
| Los Angeles / Long Beach | 119 | 4 | 44.40 | 0.3765 |
| Savannah | 43 | 1 | 41.85 | 0.0633 |

## Security Design

Security decisions:

- S3 bucket is private.
- Public access is blocked.
- Server-side encryption is enabled.
- Glue jobs use a dedicated IAM service role.
- Step Functions uses a dedicated IAM role.
- Terraform permissions are scoped to HarborWatch resources.
- No secrets are hardcoded in the repository.

## Cost Design

Cost controls:

- Small bounded AIS samples for AWS execution.
- No always-on compute.
- No Redshift Serverless.
- No streaming services.
- Parquet outputs reduce Athena scan cost.
- Athena workgroup enforces query result settings.
- Glue jobs run only when explicitly triggered or orchestrated.

## Current Limitations

- Apache Iceberg is not implemented yet.
- AWS-native vessel anomaly generation is not implemented yet.
- Gold anomaly_count is currently set to 0.
- Weather is not included in the AWS Gold table.
- Port proximity uses representative port coordinates and 20 km radius, not official port polygons.
- The pipeline is batch-oriented, not real-time streaming.
- The AWS sample is bounded for cost control.

## Future Architecture Improvements

Planned improvements:

- Migrate external Parquet tables to Apache Iceberg tables.
- Add AWS-native vessel anomaly generation.
- Add Gold anomaly counts to the congestion table.
- Add EventBridge schedule for pipeline execution.
- Add CloudWatch alarms.
- Add S3 lifecycle policies.
- Add cost monitoring alerts.
- Add dashboard layer using Streamlit or QuickSight.
- Add architecture screenshots and execution evidence.