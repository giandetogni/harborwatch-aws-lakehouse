PYTHON=python3

RAW_RANDOM_SAMPLE=data/raw/public_ais/AIS_2024_01_01_random_sample_500k.csv
BRONZE_RANDOM=data/processed/bronze/bronze_ais_messages_random_sample_500k.csv
QUALITY_RANDOM=data/processed/silver/silver_data_quality_report_random_sample_500k.csv
SILVER_CLEAN_RANDOM=data/processed/silver/silver_vessel_positions_clean_random_sample_500k.csv
SILVER_PROXIMITY_RANDOM=data/processed/silver/silver_vessel_port_proximity_random_sample_500k.csv
SILVER_STOPS_RANDOM=data/processed/silver/silver_vessel_stops_random_sample_500k.csv
GOLD_ANOMALIES_RANDOM=data/processed/gold/gold_vessel_anomalies_random_sample_500k.csv
GOLD_CONGESTION_RANDOM=data/processed/gold/gold_port_congestion_daily_random_sample_500k.csv

.PHONY: sample bronze quality silver proximity stops anomalies gold run-local clean-outputs show-results

sample:
	$(PYTHON) src/ingestion/create_random_ais_sample.py

bronze:
	$(PYTHON) src/glue_jobs/raw_to_bronze_local.py \
		--input $(RAW_RANDOM_SAMPLE) \
		--output $(BRONZE_RANDOM)

quality:
	$(PYTHON) src/quality/profile_bronze_quality.py \
		--input $(BRONZE_RANDOM) \
		--output $(QUALITY_RANDOM)

silver:
	$(PYTHON) src/glue_jobs/bronze_to_silver_positions_clean_local.py

proximity:
	$(PYTHON) src/glue_jobs/silver_to_port_proximity_local.py

stops:
	$(PYTHON) src/glue_jobs/port_proximity_to_vessel_stops_local.py

anomalies:
	$(PYTHON) src/glue_jobs/silver_to_gold_vessel_anomalies_local.py

gold:
	$(PYTHON) src/glue_jobs/silver_to_gold_port_congestion_local.py

run-local: sample bronze quality silver proximity stops anomalies gold
	@echo "Local MVP pipeline completed."

show-results:
	@echo "Gold Port Congestion:"
	@cat $(GOLD_CONGESTION_RANDOM)
	@echo ""
	@echo "Gold Vessel Anomalies count:"
	@wc -l $(GOLD_ANOMALIES_RANDOM)

clean-outputs:
	rm -rf data/processed
	rm -rf data/profiling
	@echo "Generated outputs removed."
