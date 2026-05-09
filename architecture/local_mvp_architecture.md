# HarborWatch Local MVP Architecture

```mermaid
flowchart LR
    A[NOAA / MarineCadastre AIS ZIP] --> B[Random AIS Sample 500k]
    B --> C[Raw CSV]
    C --> D[Bronze AIS Messages]
    D --> E[Silver Data Quality Report]
    D --> F[Silver Vessel Positions Clean]
    F --> G[Silver Vessel Port Proximity]
    G --> H[Silver Vessel Stops]
    F --> I[Gold Vessel Anomalies]
    G --> J[Gold Port Congestion Daily]
    H --> J
    I --> J

    D:::bronze
    E:::silver
    F:::silver
    G:::silver
    H:::silver
    I:::gold
    J:::gold

    classDef bronze fill:#cd7f32,color:#fff,stroke:#333;
    classDef silver fill:#c0c0c0,color:#000,stroke:#333;
    classDef gold fill:#ffd700,color:#000,stroke:#333;
```

## Flow

1. Public AIS data is downloaded from NOAA / MarineCadastre.
2. A reproducible random sample of 500,000 records is created.
3. Raw AIS records are standardized into Bronze.
4. Bronze records are profiled for data quality.
5. Silver clean positions classify each row as valid or rejected.
6. Valid positions are enriched with nearest-port distance.
7. Vessel stop episodes are detected near ports.
8. Gold tables are generated for congestion metrics and vessel anomalies.

## Current Scope

This diagram represents the local MVP.

The AWS lakehouse architecture will extend this flow using:

- Amazon S3
- AWS Glue
- Apache Iceberg
- Glue Data Catalog
- Athena
- Step Functions
- CloudWatch
- Terraform
