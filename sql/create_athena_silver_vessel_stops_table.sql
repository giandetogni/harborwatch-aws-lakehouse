CREATE EXTERNAL TABLE IF NOT EXISTS harborwatch_lakehouse.silver_vessel_stops (
  stop_id string,
  mmsi string,
  nearest_port_id string,
  nearest_port_name string,
  stop_start_timestamp timestamp,
  stop_end_timestamp timestamp,
  dwell_time_minutes double,
  avg_speed_knots double,
  message_count bigint,
  stop_date date
)
PARTITIONED BY (
  year int,
  month int
)
STORED AS PARQUET
LOCATION 's3://harborwatch-dev-lakehouse-giandetogni/silver/vessel_stops/';
