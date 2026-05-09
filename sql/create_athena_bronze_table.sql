CREATE EXTERNAL TABLE IF NOT EXISTS harborwatch_lakehouse.bronze_ais_messages (
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
  event_date date
)
PARTITIONED BY (
  year int,
  month int
)
STORED AS PARQUET
LOCATION 's3://harborwatch-dev-lakehouse-giandetogni/bronze/ais_messages/';
