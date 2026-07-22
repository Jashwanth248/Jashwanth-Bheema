# Jashwanth Bheema | Production AI & Data Portfolio

This repository contains three independent, production-oriented portfolio projects. They are deliberately built around synthetic data and configurable rules so they demonstrate enterprise data engineering and AI practices without exposing employer or customer data.

| Project | Focus | Demonstrates |
| --- | --- | --- |
| [01 — Data Quality at Scale](01-data-quality-at-scale) | Batch validation and remediation | Python, SQL patterns, data contracts, idempotency, observability |
| [02 — AI Data Quality Investigator](02-ai-data-quality-agent) | Evidence-first investigation agent | Agent workflows, retrieval, guardrails, auditability |
| [03 — ML Anomaly Monitoring](03-ml-anomaly-monitoring) | Anomaly scoring and drift monitoring | Feature engineering, model evaluation, monitoring |

## Portfolio principles

* **Reproducible:** each project includes deterministic sample data, tests, and clear run instructions.
* **Production-minded:** validation, structured outputs, configuration, and error handling are first-class concerns.
* **Responsible:** synthetic records are used throughout; agent recommendations are advisory and traceable.

## Quick verification

```bash
python -m unittest discover -s 01-data-quality-at-scale/tests
python -m unittest discover -s 02-ai-data-quality-agent/tests
python -m unittest discover -s 03-ml-anomaly-monitoring/tests
```

## Contact

* Email: [bheemajashwanth9@gmail.com](mailto:bheemajashwanth9@gmail.com)
* Location: California, USA
