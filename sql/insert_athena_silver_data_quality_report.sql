INSERT INTO harborwatch_lakehouse.silver_data_quality_report
SELECT
  current_date AS processing_date,
  'bronze_ais_messages_aws_sample_1k' AS source_file,
  COUNT(*) AS total_records,
  SUM(CASE WHEN quality_status = 'valid' THEN 1 ELSE 0 END) AS valid_records,
  SUM(CASE WHEN quality_status = 'rejected' THEN 1 ELSE 0 END) AS rejected_records,
  SUM(CASE WHEN is_valid_coordinate = false THEN 1 ELSE 0 END) AS invalid_coordinates_count,
  SUM(CASE WHEN is_null_vessel_id = true THEN 1 ELSE 0 END) AS null_vessel_id_count,
  SUM(CASE WHEN is_duplicate = true THEN 1 ELSE 0 END) AS duplicate_records_count,
  SUM(CASE WHEN is_impossible_speed = true THEN 1 ELSE 0 END) AS impossible_speed_count,
  SUM(CASE WHEN is_speed_unavailable = true THEN 1 ELSE 0 END) AS unavailable_speed_count,
  SUM(CASE WHEN is_future_timestamp = true THEN 1 ELSE 0 END) AS future_timestamp_count,
  CAST(SUM(CASE WHEN quality_status = 'rejected' THEN 1 ELSE 0 END) AS DOUBLE) / COUNT(*) AS rejection_rate,
  current_timestamp AS created_at
FROM harborwatch_lakehouse.silver_vessel_positions_clean;
