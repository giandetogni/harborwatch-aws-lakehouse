# HarborWatch Assumptions

## Data Source

The project uses public AIS vessel tracking data from NOAA / MarineCadastre.

The local MVP uses a random sample of 500,000 AIS records from 2024-01-01.

## Sampling

Two samples are used for different purposes:

- `quality_sample_50k`: intentionally quality-focused sample used to test data quality rejection logic.
- `random_sample_500k`: random sample used for geospatial processing, vessel stop detection, and Gold metrics.

The random sample is used for analytical outputs because it is less biased than the quality-focused sample.

## Port Scope

The MVP focuses on five US port areas:

- Los Angeles / Long Beach
- New York / New Jersey
- Houston
- Savannah
- Seattle / Tacoma

## Port Radius

A vessel is considered near a port when its distance to the nearest MVP port is less than or equal to 20 km.

This is a simplification. Real port boundaries should use polygons or operational anchorage zones.

## Stop Detection

A vessel stop is detected when:

- the vessel is within 20 km of a port;
- speed is lower than 1 knot;
- the stop episode lasts at least 30 minutes;
- consecutive stopped messages are separated by no more than 60 minutes.

If the time gap between stopped messages is greater than 60 minutes, a new stop episode starts.

## Data Quality Rules

Records are rejected or flagged when they contain:

- invalid latitude or longitude;
- missing vessel identifier;
- duplicate deterministic message ID;
- future timestamp;
- impossible speed;
- unavailable AIS speed sentinel value.

The AIS speed value `102.3` is treated as `speed_not_available`, not as a real vessel speed.

## Port Congestion Index

The MVP Port Congestion Index uses:

- 40% normalized stopped vessels;
- 35% normalized average dwell time;
- 25% normalized stopped position count.

Weather is not included in the MVP.

The index is relative to the selected sample and selected ports. It should not be interpreted as an absolute real-world congestion measurement.

## Limitations

- The MVP uses sampled AIS data, not the full dataset.
- Port proximity is point-based, not polygon-based.
- Stop detection is rule-based and approximate.
- AIS data may be incomplete, delayed, duplicated, or contain sentinel values.
- The local MVP uses CSV files; cloud deployment will later use S3, Glue, Iceberg, and Athena.
