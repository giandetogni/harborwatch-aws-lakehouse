# HarborWatch Data Dictionary

## Purpose

This document defines the main HarborWatch lakehouse tables, fields, and metrics.

The goal is to make the data model understandable for reviewers, recruiters, and technical evaluators.

## Lakehouse Layers

HarborWatch follows a layered lakehouse design:

- Raw: source data preserved with minimal modification
- Bronze: standardized source-aligned data
- Silver: cleaned, validated, and enriched data
- Gold: analytics-ready metrics

## Raw Inputs

### AIS Source Data

Source:

- NOAA / MarineCadastre public AIS vessel tracking data

Current MVP sample:

- AIS_2024_01_01_sample_10k.csv

Main source fields:

| Field | Description |
|---|---|
| MMSI | Maritime Mobile Service Identity, used as vessel identifier |
| BaseDateTime | AIS message timestamp |
| LAT | Vessel latitude |
| LON | Vessel longitude |
| SOG | Speed over ground in knots |
| COG | Course over ground |
| Heading | Vessel heading |
| VesselName | Vessel name |
| IMO | International Maritime Organization vessel identifier |
| CallSign | Vessel call sign |
| VesselType | Vessel type code |
| Status | AIS navigation status |
| Length | Vessel length |
| Width | Vessel width |
| Draft | Vessel draft |
| Cargo | Cargo type |
| TransceiverClass | AIS transceiver class |

### Port Reference Data

Table/file:

- harborwatch_ports_mvp.csv

Fields:

| Field | Type | Description |
|---|---|---|
| port_id | string | Stable port identifier |
| port_name | string | Human-readable port name |
| latitude | double | Representative port latitude |
| longitude | double | Representative port longitude |
| port_radius_km | double | MVP proximity radius in kilometers |

MVP ports:

- Los Angeles / Long Beach
- New York / New Jersey
- Houston
- Savannah
- Seattle / Tacoma

## Bronze Tables

## bronze_ais_messages

Purpose:

Standardized AIS messages with consistent types, traceability fields, and deterministic message IDs.

Location:

- s3://harborwatch-dev-lakehouse-giandetogni/bronze/ais_messages/

Format:

- Parquet

Partitioning:

- year
- month

Fields:

| Field | Type | Description |
|---|---|---|
| message_id | string | Deterministic SHA-256 ID generated from core AIS message fields |
| source_file | string | Source input file path |
| ingestion_timestamp | timestamp | Timestamp when the record was processed |
| event_timestamp | timestamp | AIS event timestamp |
| mmsi | string | Vessel identifier |
| latitude | double | Vessel latitude |
| longitude | double | Vessel longitude |
| speed_knots | double | Vessel speed over ground in knots |
| course | double | Course over ground |
| heading | double | Vessel heading |
| vessel_name | string | Vessel name |
| imo | string | IMO identifier |
| call_sign | string | Vessel call sign |
| vessel_type | string | Vessel type |
| navigation_status | string | AIS navigation status |
| length | double | Vessel length |
| width | double | Vessel width |
| draft | double | Vessel draft |
| cargo | string | Cargo classification |
| transceiver_class | string | AIS transceiver class |
| raw_payload_hash | string | SHA-256 hash of raw source payload |
| event_date | date | Date derived from event_timestamp |
| year | int | Partition year |
| month | int | Partition month |

## Silver Tables

## silver_vessel_positions_clean

Purpose:

Cleaned AIS positions with row-level data quality classification.

Location:

- s3://harborwatch-dev-lakehouse-giandetogni/silver/vessel_positions_clean/

Fields:

| Field | Type | Description |
|---|---|---|
| message_id | string | Deterministic AIS message ID |
| source_file | string | Source input file path |
| ingestion_timestamp | timestamp | Processing timestamp |
| event_timestamp | timestamp | AIS event timestamp |
| mmsi | string | Vessel identifier |
| latitude | double | Vessel latitude |
| longitude | double | Vessel longitude |
| speed_knots | double | Vessel speed over ground |
| course | double | Course over ground |
| heading | double | Vessel heading |
| vessel_name | string | Vessel name |
| imo | string | IMO identifier |
| call_sign | string | Vessel call sign |
| vessel_type | string | Vessel type |
| navigation_status | string | Navigation status |
| length | double | Vessel length |
| width | double | Vessel width |
| draft | double | Vessel draft |
| cargo | string | Cargo type |
| transceiver_class | string | AIS transceiver class |
| raw_payload_hash | string | Raw payload hash |
| event_date | date | Event date |
| is_valid_coordinate | boolean | True when latitude and longitude are within valid ranges |
| is_null_vessel_id | boolean | True when vessel identifier is missing |
| is_speed_unavailable | boolean | True when AIS speed uses the 102.3 unavailable sentinel |
| is_impossible_speed | boolean | True when speed is negative or above the MVP threshold |
| is_valid_speed | boolean | True when speed is usable for analytics |
| is_future_timestamp | boolean | True when event timestamp is in the future |
| is_duplicate | boolean | True when message_id appears more than once |
| rejection_reason | string | Pipe-delimited rejection reason |
| quality_status | string | valid or rejected |
| year | int | Partition year |
| month | int | Partition month |

## silver_data_quality_report

Purpose:

Aggregated audit report for data quality outcomes.

Location:

- s3://harborwatch-dev-lakehouse-giandetogni/silver/data_quality_report/

Fields:

| Field | Type | Description |
|---|---|---|
| processing_date | date | Date when report was generated |
| source_file | string | Logical source identifier |
| total_records | bigint | Total records evaluated |
| valid_records | bigint | Records classified as valid |
| rejected_records | bigint | Records classified as rejected |
| invalid_coordinates_count | bigint | Records with invalid coordinates |
| null_vessel_id_count | bigint | Records with missing vessel identifier |
| duplicate_records_count | bigint | Duplicate message records |
| impossible_speed_count | bigint | Records with impossible speed |
| unavailable_speed_count | bigint | Records with AIS speed sentinel 102.3 |
| future_timestamp_count | bigint | Records with future timestamp |
| rejection_rate | double | rejected_records divided by total_records |
| created_at | timestamp | Report creation timestamp |

## silver_vessel_port_proximity

Purpose:

AIS vessel positions enriched with nearest MVP port and distance-to-port metrics.

Location:

- s3://harborwatch-dev-lakehouse-giandetogni/silver/vessel_port_proximity/

Fields:

| Field | Type | Description |
|---|---|---|
| message_id | string | AIS message ID |
| event_timestamp | timestamp | AIS event timestamp |
| mmsi | string | Vessel identifier |
| latitude | double | Vessel latitude |
| longitude | double | Vessel longitude |
| speed_knots | double | Vessel speed |
| nearest_port_id | string | Nearest MVP port identifier |
| nearest_port_name | string | Nearest MVP port name |
| port_latitude | double | Representative port latitude |
| port_longitude | double | Representative port longitude |
| port_radius_km | double | Port proximity radius |
| distance_to_port_km | double | Haversine distance from vessel to nearest port |
| is_within_port_radius | boolean | True when vessel is within 20 km of nearest MVP port |
| year | int | Partition year |
| month | int | Partition month |

## silver_vessel_stops

Purpose:

Detected vessel stop episodes near MVP ports.

Location:

- s3://harborwatch-dev-lakehouse-giandetogni/silver/vessel_stops/

Fields:

| Field | Type | Description |
|---|---|---|
| stop_id | string | Deterministic stop episode identifier |
| mmsi | string | Vessel identifier |
| nearest_port_id | string | Port identifier |
| nearest_port_name | string | Port name |
| stop_start_timestamp | timestamp | First timestamp in stop episode |
| stop_end_timestamp | timestamp | Last timestamp in stop episode |
| dwell_time_minutes | double | Stop duration in minutes |
| avg_speed_knots | double | Average speed during stop episode |
| message_count | bigint | Number of AIS messages in stop episode |
| stop_date | date | Stop date |
| year | int | Partition year |
| month | int | Partition month |

Stop detection rules:

- is_within_port_radius = true
- speed_knots < 1
- maximum gap between consecutive stopped messages = 60 minutes
- minimum dwell time = 30 minutes

## Gold Tables

## gold_port_congestion_daily_aws

Purpose:

Daily analytics-ready port congestion metrics generated from AWS Silver datasets.

Location:

- s3://harborwatch-dev-lakehouse-giandetogni/gold/port_congestion_daily_aws/

Fields:

| Field | Type | Description |
|---|---|---|
| report_date | date | Date of congestion metrics |
| port_id | string | Port identifier |
| port_name | string | Port name |
| vessels_near_port | bigint | Distinct vessels within port radius |
| stopped_vessels | bigint | Distinct vessels with detected stop episodes |
| avg_dwell_time_minutes | double | Average dwell time across stop episodes |
| p90_dwell_time_minutes | double | 90th percentile dwell time |
| stopped_position_count | bigint | Number of stopped AIS positions near port |
| anomaly_count | bigint | Number of vessel anomalies. Currently 0 in AWS-native Gold |
| data_quality_rejection_rate | double | Latest Silver data quality rejection rate |
| port_congestion_index | double | Relative congestion score across MVP ports |
| created_at | timestamp | Gold record creation timestamp |

## Metrics

## vessels_near_port

Definition:

Distinct vessels with at least one valid AIS position within the 20 km MVP port radius.

## stopped_vessels

Definition:

Distinct vessels with a detected stop episode near the port.

## avg_dwell_time_minutes

Definition:

Average duration of detected stop episodes in minutes.

## p90_dwell_time_minutes

Definition:

90th percentile dwell time across stop episodes.

## stopped_position_count

Definition:

Count of AIS position messages near a port where speed_knots < 1.

## data_quality_rejection_rate

Definition:

Rejected records divided by total evaluated records.

## port_congestion_index

Definition:

Relative MVP congestion score calculated from normalized congestion components.

Current AWS MVP formula:

- 40% normalized stopped vessels
- 35% normalized average dwell time
- 25% normalized stopped position count

Weather is not included in the current AWS MVP.

## Known Modeling Limitations

- Port proximity uses representative coordinates and a 20 km radius, not official port polygons.
- AIS data can be sparse, delayed, duplicated, or contain sentinel values.
- Vessel stop detection is rule-based.
- AWS-native anomaly generation is not implemented yet.
- Current AWS sample is bounded for cost control.