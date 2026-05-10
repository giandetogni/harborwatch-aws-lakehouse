CREATE EXTERNAL TABLE IF NOT EXISTS harborwatch_lakehouse.gold_port_congestion_daily_aws (
  report_date date,
  port_id string,
  port_name string,
  vessels_near_port bigint,
  stopped_vessels bigint,
  avg_dwell_time_minutes double,
  p90_dwell_time_minutes double,
  stopped_position_count bigint,
  anomaly_count bigint,
  data_quality_rejection_rate double,
  port_congestion_index double,
  created_at timestamp
)
STORED AS PARQUET
LOCATION 's3://harborwatch-dev-lakehouse-giandetogni/gold/port_congestion_daily_aws/';
