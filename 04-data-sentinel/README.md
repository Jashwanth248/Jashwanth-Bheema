# Data Sentinel: confidence-aware data intake

Data Sentinel is a production-style, multi-stage intake workflow built around the
[UCI Adult Census Income dataset](https://archive.ics.uci.edu/dataset/2/adult).
It is intentionally designed to answer a real operational question: **may an
incoming batch be trusted, quarantined, or sent to a data steward?**

> The source data describes people and contains sensitive demographic attributes.
> This project uses it only for data-quality demonstrations. It does not train an
> eligibility, hiring, credit, or other decision-making model.

## What makes this different

| Stage | What it does | Output confidence |
| --- | --- | --- |
| Intake | Downloads a versioned public source and captures provenance. | 1.00 when checksum/parse succeeds |
| Schema agent | Matches source columns to a canonical contract using token-vector cosine similarity. | Mapping similarity |
| Cleaning agent | Trims values, normalizes missing-value markers, and preserves raw evidence. | Transformation confidence |
| Validation agent | Enforces types, non-negative constraints, allowed labels, and completeness. | 1.00 for deterministic results |
| Anomaly agent | Uses median/MAD scores for numeric outliers. | Score-derived confidence |
| Decision agent | Combines evidence and routes batches to `accept`, `quarantine`, or `human_review`. | Weighted, policy-bounded confidence |

The included semantic lookup is a small deterministic sparse-vector implementation
so this project runs with Python's standard library. The `vectorize` and
`cosine_similarity` boundary is deliberately isolated: production can replace it
with an embedding service and pgvector/Qdrant without changing the orchestration.

## Run

```bash
# Download the real public dataset; this file is deliberately not committed.
python src/data_sentinel.py fetch --output data/adult.csv

# Process it and create a portable audit artifact.
python src/data_sentinel.py run --input data/adult.csv --output artifacts/latest_run.json

# Review the batch routing decision and agent confidence scores.
cat artifacts/latest_run.json
```

If the UCI legacy URL is unavailable in your environment, download the Adult
dataset from the UCI page above as CSV and run the second command with that file.

## Example output

`artifacts/example_run.json` is a checked-in, deterministic demonstration of the
output shape. Real runs write the same schema and include the source SHA-256,
row-level quarantine evidence, field profiles, semantic schema mappings, and
agent decision trail.

## Safety and operating rules

* Raw values are never overwritten; cleaning actions are recorded as evidence.
* Deterministic policy failures override semantic retrieval confidence.
* Low-confidence schema mappings and sensitive-field changes require human review.
* The system does not modify upstream data or automatically reprocess a batch.

## Tests

```bash
python -m unittest discover -s tests
```
