CREATE EXTERNAL TABLE IF NOT EXISTS harborwatch_lakehouse.gold_port_congestion_daily (
  report_date string,
  port_id string,
  port_name string,
  vessels_near_port int,
  stopped_vessels int,
  avg_dwell_time_minutes double,
  p90_dwell_time_minutes double,
  stopped_position_count int,
  anomaly_count int,
  data_quality_rejection_rate double,
  port_congestion_index double
)
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.OpenCSVSerde'
WITH SERDEPROPERTIES (
  'separatorChar' = ',',
  'quoteChar' = '"'
)
LOCATION 's3://harborwatch-dev-lakehouse-giandetogni/gold/gold_port_congestion_daily/date=2024-01-01/'
TBLPROPERTIES (
  'skip.header.line.count'='1'
);

CREATE EXTERNAL TABLE IF NOT EXISTS harborwatch_lakehouse.gold_vessel_anomalies (
  anomaly_id string,
  event_timestamp string,
  mmsi string,
  nearest_port_id string,
  nearest_port_name string,
  distance_to_port_km double,
  is_within_port_radius string,
  port_radius_km double,
  anomaly_type string,
  severity string,
  description string,
  source_message_id string,
  created_at string
)
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.OpenCSVSerde'
WITH SERDEPROPERTIES (
  'separatorChar' = ',',
  'quoteChar' = '"'
)
LOCATION 's3://harborwatch-dev-lakehouse-giandetogni/gold/gold_vessel_anomalies/date=2024-01-01/'
TBLPROPERTIES (
  'skip.header.line.count'='1'
);
