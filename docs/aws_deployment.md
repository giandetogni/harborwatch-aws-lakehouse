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

## Athena Validation

Athena external tables were created for the Gold outputs:

- harborwatch_lakehouse.gold_port_congestion_daily
- harborwatch_lakehouse.gold_vessel_anomalies

Validated queries:

- Port congestion ranking returned 5 MVP ports.
- Vessel anomalies query returned anomaly counts within the 20 km port radius.

Anomalies within port radius:

- New York / New Jersey: 44
- Seattle / Tacoma: 23
- Savannah: 13
- Los Angeles / Long Beach: 2

This confirms that the S3 Gold outputs are queryable through Athena.

## Athena CLI Workgroup Validation

The Terraform-managed Athena workgroup was validated through AWS CLI.

Workgroup:

- harborwatch-dev-athena-workgroup

Validated query:

SELECT port_name, port_congestion_index FROM harborwatch_lakehouse.gold_port_congestion_daily ORDER BY port_congestion_index DESC;

Execution result:

- QueryExecutionId: ed921db1-34aa-4671-b504-4efa6e4872fd
- Status: SUCCEEDED
- Data scanned: 632 bytes
- Output location: s3://harborwatch-dev-lakehouse-giandetogni/athena-results/ed921db1-34aa-4671-b504-4efa6e4872fd.csv

This confirms that the Terraform-managed Athena workgroup can execute queries against the Gold external tables.

## AWS Glue Raw-to-Bronze Validation

The first AWS Glue job was executed successfully.

Flow validated:

- Raw AIS CSV uploaded to S3 Raw
- AWS Glue job transformed Raw CSV into Bronze Parquet
- Bronze Parquet was written to S3
- Athena external table was created for Bronze
- Athena query validated row count and timestamp range

Bronze output path:

s3://harborwatch-dev-lakehouse-giandetogni/bronze/ais_messages/

Validation query result:

- row_count: 1000
- min_event_timestamp: 2024-01-01 00:00:00
- max_event_timestamp: 2024-01-01 23:59:37

This confirms that the AWS Raw-to-Bronze pipeline is operational.

## AWS Silver Data Quality Report Validation

The Silver Data Quality Report was created and validated through Athena.

Validation result:

- total_records: 1000
- valid_records: 997
- rejected_records: 3
- invalid_coordinates_count: 0
- null_vessel_id_count: 0
- duplicate_records_count: 0
- impossible_speed_count: 0
- unavailable_speed_count: 3
- future_timestamp_count: 0
- rejection_rate: 0.003

This confirms that the AWS Silver layer has an auditable data quality report.

## AWS Silver Port Proximity Validation

The AWS Glue Silver-to-Port-Proximity job was executed successfully.

Flow validated:

- Silver clean Parquet was read from S3
- Port reference CSV was read from S3
- Haversine distance was calculated for MVP ports
- Nearest port was selected for each valid vessel position
- is_within_port_radius was calculated using a 20 km threshold
- Silver port proximity Parquet was written to S3
- Athena external table was created and validated

Validation result:

- row_count: 997
- closest observed vessel-port distance: 0.35 km
- sample records returned vessels within 20 km of Los Angeles / Long Beach, Houston, Savannah, Seattle / Tacoma, and New York / New Jersey

This confirms that the AWS geospatial enrichment layer is operational.
