INSERT INTO harborwatch_lakehouse.gold_port_congestion_daily_aws
WITH proximity_metrics AS (
  SELECT
    CAST(event_timestamp AS date) AS report_date,
    nearest_port_id AS port_id,
    nearest_port_name AS port_name,
    COUNT(DISTINCT mmsi) AS vessels_near_port,
    SUM(CASE WHEN speed_knots < 1 THEN 1 ELSE 0 END) AS stopped_position_count
  FROM harborwatch_lakehouse.silver_vessel_port_proximity
  WHERE is_within_port_radius = true
  GROUP BY
    CAST(event_timestamp AS date),
    nearest_port_id,
    nearest_port_name
),
stops_metrics AS (
  SELECT
    stop_date AS report_date,
    nearest_port_id AS port_id,
    nearest_port_name AS port_name,
    COUNT(*) AS stops,
    COUNT(DISTINCT mmsi) AS stopped_vessels,
    ROUND(AVG(dwell_time_minutes), 2) AS avg_dwell_time_minutes,
    ROUND(APPROX_PERCENTILE(dwell_time_minutes, 0.9), 2) AS p90_dwell_time_minutes
  FROM harborwatch_lakehouse.silver_vessel_stops
  GROUP BY
    stop_date,
    nearest_port_id,
    nearest_port_name
),
latest_quality_report AS (
  SELECT rejection_rate
  FROM harborwatch_lakehouse.silver_data_quality_report
  ORDER BY created_at DESC
  LIMIT 1
),
base AS (
  SELECT
    p.report_date,
    p.port_id,
    p.port_name,
    p.vessels_near_port,
    COALESCE(s.stopped_vessels, 0) AS stopped_vessels,
    COALESCE(s.avg_dwell_time_minutes, 0.0) AS avg_dwell_time_minutes,
    COALESCE(s.p90_dwell_time_minutes, 0.0) AS p90_dwell_time_minutes,
    p.stopped_position_count,
    CAST(0 AS bigint) AS anomaly_count,
    q.rejection_rate AS data_quality_rejection_rate
  FROM proximity_metrics p
  LEFT JOIN stops_metrics s
    ON p.report_date = s.report_date
   AND p.port_id = s.port_id
  CROSS JOIN latest_quality_report q
),
normalized AS (
  SELECT
    *,
    CASE
      WHEN MAX(stopped_vessels) OVER () = MIN(stopped_vessels) OVER () THEN 0.0
      ELSE CAST(stopped_vessels - MIN(stopped_vessels) OVER () AS double)
        / NULLIF(MAX(stopped_vessels) OVER () - MIN(stopped_vessels) OVER (), 0)
    END AS normalized_stopped_vessels,
    CASE
      WHEN MAX(avg_dwell_time_minutes) OVER () = MIN(avg_dwell_time_minutes) OVER () THEN 0.0
      ELSE CAST(avg_dwell_time_minutes - MIN(avg_dwell_time_minutes) OVER () AS double)
        / NULLIF(MAX(avg_dwell_time_minutes) OVER () - MIN(avg_dwell_time_minutes) OVER (), 0)
    END AS normalized_avg_dwell_time,
    CASE
      WHEN MAX(stopped_position_count) OVER () = MIN(stopped_position_count) OVER () THEN 0.0
      ELSE CAST(stopped_position_count - MIN(stopped_position_count) OVER () AS double)
        / NULLIF(MAX(stopped_position_count) OVER () - MIN(stopped_position_count) OVER (), 0)
    END AS normalized_stopped_position_count
  FROM base
)
SELECT
  report_date,
  port_id,
  port_name,
  vessels_near_port,
  stopped_vessels,
  avg_dwell_time_minutes,
  p90_dwell_time_minutes,
  stopped_position_count,
  anomaly_count,
  data_quality_rejection_rate,
  ROUND(
    0.40 * normalized_stopped_vessels
    + 0.35 * normalized_avg_dwell_time
    + 0.25 * normalized_stopped_position_count,
    4
  ) AS port_congestion_index,
  current_timestamp AS created_at
FROM normalized;
