# ML Anomaly Monitoring

A transparent anomaly-scoring and monitoring project for prioritizing potentially invalid operational records. It uses a robust, explainable baseline rather than hiding decision logic behind a black-box model.

## Approach

* Build numerical features from transaction amount and processing latency.
* Fit median and median absolute deviation (MAD) baselines on reference data.
* Score new records using robust z-scores and label high-risk outliers.
* Monitor feature drift between reference and live populations.

The baseline is a practical first deployment: it is fast, reproducible, and easy to review. It can later be compared with Isolation Forest, autoencoders, or supervised classifiers when labeled outcomes are available.

## Run

```bash
python src/monitor.py --reference data/reference.csv --live data/live.csv
```

## Resume-ready highlights

* Robust statistics avoid sensitivity to extreme values during baseline fitting.
* Each score includes per-feature contributions for investigator review.
* Drift results identify when retraining or a data-contract review may be required.
