# HarborWatch Validation Evidence Summary

## Purpose

This document summarizes the main validation evidence for the HarborWatch AWS lakehouse MVP.

It is intended to provide quick proof that the project runs end-to-end on AWS and produces analytical outputs from real public AIS data.

## Current AWS Pipeline Status

The AWS pipeline is operational and orchestrated through AWS Step Functions.

Validated flow:

1. S3 Raw AIS sample
2. AWS Glue Raw-to-Bronze
3. Bronze Parquet
4. AWS Glue Bronze-to-Silver Clean
5. Silver Clean Parquet
6. Silver Data Quality Report
7. AWS Glue Silver-to-Port-Proximity
8. Silver Port Proximity Parquet
9. AWS Glue Port-Proximity-to-Vessel-Stops
10. Silver Vessel Stops Parquet
11. Athena Gold Port Congestion Daily

## Step Functions Validation

State machine:

- harborwatch-dev-lakehouse-pipeline

Execution result:

- Status: SUCCEEDED

Orchestrated Glue jobs:

- harborwatch-dev-raw-to-bronze
- harborwatch-dev-bronze-to-silver-clean
- harborwatch-dev-silver-to-port-proximity
- harborwatch-dev-port-proximity-to-vessel-stops

Final output validated:

- s3://harborwatch-dev-lakehouse-giandetogni/silver/vessel_stops/

## Data Quality Validation

Initial AWS validation sample:

- Total records: 1,000
- Valid records: 997
- Rejected records: 3
- Rejection rate: 0.003

Rejected records reason:

- speed_not_available: 3

The AIS speed value 102.3 is treated as an unavailable speed sentinel, not as a real vessel speed.

## Geospatial Validation

The AWS Silver Port Proximity layer calculates Haversine distance between vessel positions and MVP ports.

MVP ports:

- Los Angeles / Long Beach
- New York / New Jersey
- Houston
- Savannah
- Seattle / Tacoma

Validated geospatial output:

- nearest_port_id
- nearest_port_name
- distance_to_port_km
- is_within_port_radius

Port proximity aggregate result:

| Port | Total Positions | Positions Within 20 km | Distinct Vessels |
|---|---:|---:|---:|
| Seattle / Tacoma | 165 | 47 | 153 |
| Houston | 365 | 37 | 338 |
| New York / New Jersey | 166 | 27 | 160 |
| Los Angeles / Long Beach | 99 | 17 | 93 |
| Savannah | 202 | 10 | 190 |

## Vessel Stops Validation

The AWS Vessel Stops layer detects stop episodes using:

- is_within_port_radius = true
- speed_knots < 1
- maximum gap between stopped messages: 60 minutes
- minimum dwell time: 30 minutes

Validated AWS result from the 10k sample:

- Total vessel stops: 26

Stops by port:

| Port | Stops | Stopped Vessels | Avg Dwell Minutes | Max Dwell Minutes |
|---|---:|---:|---:|---:|
| Houston | 12 | 12 | 42.02 | 59.97 |
| Seattle / Tacoma | 8 | 8 | 40.50 | 54.00 |
| Los Angeles / Long Beach | 4 | 4 | 44.40 | 57.83 |
| New York / New Jersey | 1 | 1 | 47.97 | 47.97 |
| Savannah | 1 | 1 | 41.85 | 41.85 |

## AWS-Native Gold Validation

The AWS-native Gold Port Congestion table was generated from AWS Silver datasets.

Gold table:

- harborwatch_lakehouse.gold_port_congestion_daily_aws

Gold output:

| Port | Vessels Near Port | Stopped Vessels | Avg Dwell Minutes | P90 Dwell Minutes | Stopped Position Count | Data Quality Rejection Rate | Port Congestion Index |
|---|---:|---:|---:|---:|---:|---:|---:|
| Houston | 175 | 12 | 42.02 | 51.50 | 281 | 0.003 | 0.6405 |
| Seattle / Tacoma | 278 | 8 | 40.50 | 54.00 | 384 | 0.003 | 0.5045 |
| New York / New Jersey | 155 | 1 | 47.97 | 47.97 | 191 | 0.003 | 0.4487 |
| Los Angeles / Long Beach | 119 | 4 | 44.40 | 57.83 | 173 | 0.003 | 0.3765 |
| Savannah | 43 | 1 | 41.85 | 41.85 | 65 | 0.003 | 0.0633 |

## Infrastructure Validation

Terraform-managed AWS resources include:

- S3 lakehouse bucket
- Glue Data Catalog database
- Glue jobs
- Glue job scripts in S3
- IAM roles and policies
- Athena workgroup
- Step Functions state machine

Terraform validation:

- terraform fmt
- terraform validate
- terraform plan
- terraform apply

## Current Limitations

- Apache Iceberg is not implemented yet.
- AWS-native vessel anomaly generation is not implemented yet.
- anomaly_count is currently set to 0 in the AWS-native Gold table.
- Weather is not included in the AWS-native Gold table.
- Port boundaries use simplified 20 km radius logic.
- Current AWS execution uses bounded AIS samples for cost control.

## Evidence Still To Add

Recommended screenshots:

- Step Functions execution graph showing SUCCEEDED
- Glue jobs list showing successful runs
- Athena Gold query result
- S3 lakehouse prefixes
- GitHub Actions CI passing
- Terraform outputs