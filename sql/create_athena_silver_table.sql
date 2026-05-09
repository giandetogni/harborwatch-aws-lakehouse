CREATE EXTERNAL TABLE IF NOT EXISTS harborwatch_lakehouse.silver_vessel_positions_clean (
  message_id string,
  source_file string,
  ingestion_timestamp timestamp,
  event_timestamp timestamp,
  mmsi string,
  latitude double,
  longitude double,
  speed_knots double,
  course double,
  heading double,
  vessel_name string,
  imo string,
  call_sign string,
  vessel_type string,
  navigation_status string,
  length double,
  width double,
  draft double,
  cargo string,
  transceiver_class string,
  raw_payload_hash string,
  event_date date,
  is_valid_coordinate boolean,
  is_null_vessel_id boolean,
  is_speed_unavailable boolean,
  is_impossible_speed boolean,
  is_valid_speed boolean,
  is_future_timestamp boolean,
  is_duplicate boolean,
  rejection_reason string,
  quality_status string
)
PARTITIONED BY (
  year int,
  month int
)
STORED AS PARQUET
LOCATION 's3://harborwatch-dev-lakehouse-giandetogni/silver/vessel_positions_clean/';
