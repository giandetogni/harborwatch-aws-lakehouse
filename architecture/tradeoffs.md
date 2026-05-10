# HarborWatch Architecture Trade-offs

## Purpose

This document explains the main architecture trade-offs made in the HarborWatch AWS lakehouse MVP.

The goal is to show not only what was built, but why specific technical decisions were made.

## Summary

HarborWatch prioritizes a realistic, cost-controlled, serverless AWS data engineering architecture.

The MVP favors:

- Batch processing over streaming
- AWS Glue over always-on compute
- Athena over Redshift
- Parquet external tables before Apache Iceberg
- Step Functions over Airflow
- Small bounded samples over full-scale processing
- Rule-based analytics over premature machine learning

These choices reduce complexity and cost while still demonstrating real data engineering capability.

## Trade-off 1: Batch Processing vs Streaming

### Decision

The MVP uses batch processing.

### Why

AIS data can be processed in daily or hourly batches for the current portfolio use case. The goal is to demonstrate ingestion, lakehouse layers, data quality, geospatial enrichment, dwell time, and analytics-ready metrics.

### Alternatives Considered

- Kinesis Data Streams
- MSK / Kafka
- Near-real-time streaming pipeline

### Why Not Streaming Now

Streaming would increase complexity, cost, and operational burden without improving the MVP enough for portfolio evaluation.

### Impact

Positive:

- Lower cost
- Easier reproducibility
- Easier debugging
- Simpler AWS architecture

Negative:

- Not real-time
- Cannot support live alerting yet

### Future Improvement

Add streaming only if the project evolves toward real-time vessel monitoring.

## Trade-off 2: AWS Glue vs EMR or EC2 Spark

### Decision

The MVP uses AWS Glue Spark Jobs.

### Why

Glue provides managed Spark execution, integrates well with S3 and Glue Data Catalog, and avoids cluster management.

### Alternatives Considered

- Amazon EMR
- EC2-hosted Spark
- AWS Batch
- Local-only PySpark

### Why Glue Fits

Glue is appropriate for a serverless portfolio lakehouse because it shows real AWS data engineering without requiring always-on infrastructure.

### Impact

Positive:

- Managed Spark
- Serverless execution
- Good integration with S3, IAM, and Step Functions
- Strong signal for AWS Data Engineering roles

Negative:

- Cold start latency
- Job runs can be relatively expensive if repeated unnecessarily
- Debugging can be slower than local execution

### Future Improvement

Use job bookmarks, parameterized runs, and stronger observability if the pipeline becomes recurring.

## Trade-off 3: Athena vs Redshift Serverless

### Decision

The MVP uses Athena for SQL analytics and validation.

### Why

The project primarily queries lakehouse files in S3. Athena is serverless, simple, and cost-effective for the current scale.

### Alternatives Considered

- Redshift Serverless
- Redshift Spectrum
- DuckDB for local analytics

### Why Not Redshift Now

Redshift would add cost and complexity before there is a clear need for warehouse-specific performance, concurrency, or BI workload management.

### Impact

Positive:

- Lower operational burden
- Direct querying over S3
- Good fit for Parquet lakehouse data
- No always-on warehouse

Negative:

- Query performance depends on file layout and scan volume
- Less suitable for high-concurrency BI workloads

### Future Improvement

Add Redshift only if the project needs dashboard concurrency, complex semantic modeling, or warehouse-specific optimization.

## Trade-off 4: Parquet External Tables vs Apache Iceberg

### Decision

The current AWS MVP uses Parquet external tables.

### Why

The first priority was to prove the full AWS pipeline end-to-end: Raw, Bronze, Silver, Gold, data quality, geospatial processing, dwell time, and orchestration.

### Alternatives Considered

- Apache Iceberg tables from the beginning
- Delta Lake
- Hudi

### Why Iceberg Was Deferred

Iceberg is valuable, but implementing it before the pipeline worked would increase risk and slow down MVP completion.

### Impact

Positive:

- Faster MVP delivery
- Simpler debugging
- Easier Athena validation
- Lower implementation complexity

Negative:

- No table-level ACID semantics
- No schema evolution management
- No time travel
- Manual table management is less robust

### Future Improvement

Migrate Bronze, Silver, and Gold tables to Apache Iceberg after the pipeline is stable.

## Trade-off 5: Step Functions vs Airflow / MWAA

### Decision

The MVP uses AWS Step Functions for orchestration.

### Why

The pipeline has a clear linear sequence of Glue jobs. Step Functions is serverless, visual, and integrates directly with Glue.

### Alternatives Considered

- MWAA / Airflow
- EventBridge-only orchestration
- Manual job execution
- GitHub Actions triggering AWS jobs

### Why Not Airflow Now

Airflow would be overkill for the current MVP. It adds cost, environment management, DAG complexity, and operational overhead.

### Impact

Positive:

- Serverless orchestration
- Visual execution graph
- Direct Glue integration
- Strong AWS-native signal

Negative:

- Less flexible than Airflow for complex DAG ecosystems
- Gold Athena SQL is not fully orchestrated yet

### Future Improvement

Add Athena SQL execution through Lambda or Step Functions SDK integrations.

## Trade-off 6: Representative Port Coordinates vs Port Polygons

### Decision

The MVP uses representative port coordinates and a 20 km radius.

### Why

This enables real geospatial distance calculations without requiring complex polygon datasets or geospatial indexing.

### Alternatives Considered

- Official port boundary polygons
- Anchorage zone polygons
- H3 hex indexing
- Geohash-based spatial bucketing

### Why Radius-Based Logic Now

The current MVP needs to prove useful geospatial enrichment with low complexity.

### Impact

Positive:

- Simple and explainable
- Easy to implement in Spark
- Works for MVP analytics
- Good enough to detect proximity patterns

Negative:

- Not equivalent to official port boundaries
- Can include nearby non-port waters
- Can miss operational anchorage zones outside radius

### Future Improvement

Replace radius logic with port polygons, anchorage zones, or H3-based spatial modeling.

## Trade-off 7: Rule-Based Vessel Stops vs Advanced Trajectory Modeling

### Decision

The MVP uses rule-based vessel stop detection.

### Current Stop Rule

- Vessel is within 20 km of an MVP port
- speed_knots < 1
- consecutive stopped messages separated by no more than 60 minutes
- dwell time is at least 30 minutes

### Why

This rule is transparent, testable, and explainable.

### Alternatives Considered

- Trajectory clustering
- Hidden Markov models
- ML-based behavior classification
- Spatial-temporal segmentation algorithms

### Why Not ML Now

Machine learning would be premature. The core value of this project is engineering the lakehouse pipeline, not building a sophisticated prediction model.

### Impact

Positive:

- Easy to validate
- Easy to explain
- Strong fit for data engineering portfolio
- Low operational complexity

Negative:

- May miss complex waiting behavior
- Sensitive to AIS sampling density
- Depends on threshold choices

### Future Improvement

Add more robust trajectory segmentation only after the data platform is stable.

## Trade-off 8: Small Sample vs Full AIS Dataset

### Decision

The AWS MVP uses bounded AIS samples.

### Why

Full AIS daily files are large. Processing full-scale data repeatedly would increase cost and slow iteration.

### Alternatives Considered

- Full-day AIS processing
- Multi-day AIS processing
- Full monthly backfill

### Why Bounded Sample Now

The project goal is to prove architecture and data engineering competence, not operate a production maritime intelligence platform.

### Impact

Positive:

- Lower cost
- Faster feedback loop
- Easier debugging
- Safer AWS usage

Negative:

- Metrics are sample-relative
- Congestion ranking is not a definitive real-world measurement
- Dwell time requires enough temporal density

### Future Improvement

Scale to 1 to 7 full days after MVP validation.

## Trade-off 9: No Weather in MVP

### Decision

Weather is not included in the AWS-native MVP.

### Why

The current project already includes ingestion, quality, geospatial enrichment, dwell time, orchestration, and Gold metrics. Adding weather too early would increase scope.

### Alternatives Considered

- NOAA weather enrichment
- Port-level weather severity score
- Wind and wave conditions

### Impact

Positive:

- Keeps MVP focused
- Avoids scope creep
- Reduces integration risk

Negative:

- Port Congestion Index does not account for weather-driven disruption

### Future Improvement

Add weather severity as an additional Gold feature after AWS-native anomaly generation is complete.

## Trade-off 10: No AWS-Native Anomaly Generation Yet

### Decision

AWS-native anomaly generation is deferred.

### Why

The local MVP already demonstrates anomaly logic, but the AWS pipeline first needed to prove the core lakehouse path through Gold congestion.

### Current State

The AWS-native Gold table sets anomaly_count to 0.

### Impact

Positive:

- Keeps AWS Gold pipeline stable
- Avoids mixing incomplete anomaly logic into congestion metrics

Negative:

- Gold table does not yet reflect anomaly counts
- AWS pipeline does not fully match the local anomaly feature set

### Future Improvement

Add an AWS Glue job for vessel anomalies and join anomaly_count into Gold.

## Overall Architecture Position

The current architecture is appropriate for a portfolio-grade AWS lakehouse MVP.

It demonstrates:

- Serverless AWS data engineering
- S3-based lakehouse layering
- Glue Spark transformations
- Data quality enforcement
- Geospatial enrichment
- Dwell time analytics
- Athena Gold metrics
- Step Functions orchestration
- Terraform infrastructure
- Operational documentation

The main missing lakehouse capability is Apache Iceberg.

## Next Architecture Improvements

Recommended next steps:

1. Add AWS-native vessel anomaly generation.
2. Add Iceberg tables for Bronze, Silver, and Gold.
3. Add EventBridge scheduling.
4. Add CloudWatch alarms.
5. Add screenshots and visual evidence.
6. Add a lightweight dashboard.
7. Add S3 lifecycle policies.