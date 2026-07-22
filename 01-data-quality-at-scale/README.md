# Data Quality at Scale

An auditable batch-validation service for high-volume transactional records. The design mirrors an enterprise ingestion boundary: validate contracts before downstream loading, create an error quarantine, and emit machine-readable quality metrics.

## Why this matters

Bad data creates expensive downstream failures. This project demonstrates how to identify null keys, duplicates, invalid reference values, malformed amounts, and future dates before data reaches analytics or operational systems.

## Architecture

`CSV/warehouse extract → contract checks → valid + quarantine outputs → quality report → alert/triage`

The included implementation uses Python's standard library for a zero-dependency demo. In production, the same contract can be executed with Spark/Dataflow and the output can be persisted in BigQuery, Dataplex, or an operational database.

## Run

```bash
python src/pipeline.py --input data/sample_transactions.csv --output-dir artifacts
cat artifacts/quality_report.json
```

## Resume-ready highlights

* Configuration-driven data contract with row-level evidence.
* Deterministic record fingerprinting for rerun-safe duplicate detection.
* Valid/quarantine separation and quality SLO calculation.
* Unit tests for valid, duplicate, and invalid records.
