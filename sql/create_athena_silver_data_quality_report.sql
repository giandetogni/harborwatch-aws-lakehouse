CREATE EXTERNAL TABLE IF NOT EXISTS harborwatch_lakehouse.silver_data_quality_report (
  processing_date date,
  source_file string,
  total_records bigint,
  valid_records bigint,
  rejected_records bigint,
  invalid_coordinates_count bigint,
  null_vessel_id_count bigint,
  duplicate_records_count bigint,
  impossible_speed_count bigint,
  unavailable_speed_count bigint,
  future_timestamp_count bigint,
  rejection_rate double,
  created_at timestamp
)
STORED AS PARQUET
LOCATION 's3://harborwatch-dev-lakehouse-giandetogni/silver/data_quality_report/';
