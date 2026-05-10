# HarborWatch Release Checklist

## Purpose

This checklist defines the minimum quality bar before presenting HarborWatch publicly on GitHub, LinkedIn, or in job applications.

## Repository

- [x] README explains the problem, solution, architecture, pipeline, metrics, and limitations.
- [x] Repository has clear folder structure.
- [x] Source code is organized by ingestion, Glue jobs, quality, geospatial, and metrics.
- [x] SQL files are versioned.
- [x] Terraform files are versioned.
- [x] Documentation is available under docs/ and architecture/.
- [x] Evidence is available under evidence/.

## AWS Pipeline

- [x] S3 lakehouse bucket exists.
- [x] Raw layer exists.
- [x] Bronze Parquet layer exists.
- [x] Silver Clean layer exists.
- [x] Silver Data Quality Report exists.
- [x] Silver Port Proximity exists.
- [x] Silver Vessel Stops exists.
- [x] AWS-native Gold Port Congestion table exists.
- [x] Step Functions orchestrates the Glue pipeline.
- [x] Athena validates final outputs.

## Data Engineering

- [x] Raw to Bronze transformation implemented.
- [x] Bronze to Silver cleaning implemented.
- [x] Data quality rules implemented.
- [x] Geospatial nearest-port enrichment implemented.
- [x] Vessel stop and dwell time detection implemented.
- [x] Gold congestion metrics implemented.
- [x] Port Congestion Index implemented.

## Validation Evidence

- [x] Step Functions execution screenshot.
- [x] Glue successful runs screenshots.
- [x] Athena Gold query screenshot.
- [x] Athena vessel stops query screenshot.
- [x] S3 lakehouse prefixes screenshot.
- [x] GitHub Actions CI screenshot.
- [x] Terraform outputs screenshot.
- [x] Validation summary document.

## Documentation

- [x] Data dictionary.
- [x] Cost estimate.
- [x] Runbook.
- [x] Incident response.
- [x] AWS target architecture.
- [x] Architecture trade-offs.
- [x] AWS deployment notes.
- [x] Screenshots guide.

## Security

- [ ] No AWS access keys committed.
- [ ] No secrets committed.
- [ ] No .env file committed.
- [ ] No terraform.tfvars committed.
- [ ] No terraform.tfstate committed.
- [ ] S3 bucket is private.
- [ ] Public access is blocked.
- [ ] IAM roles are scoped to HarborWatch resources.

## Known Limitations

- [x] Apache Iceberg is not implemented yet.
- [x] AWS-native anomaly generation is not implemented yet.
- [x] Weather is not included yet.
- [x] Port proximity uses simplified 20 km radius logic.
- [x] Current AWS execution uses bounded AIS samples for cost control.

## Final Public Release Criteria

Before posting publicly:

- [ ] GitHub repository is public.
- [ ] README renders correctly.
- [ ] Screenshots render correctly.
- [ ] CI badge is passing.
- [ ] No secrets are present.
- [ ] Main branch is clean.
- [ ] LinkedIn post links to the repository.