"""Explainable robust anomaly scoring and simple population drift monitoring."""
from __future__ import annotations

import argparse
import csv
import json
import statistics
from pathlib import Path

FEATURES = ("amount", "processing_minutes")


def read_rows(path: Path) -> list[dict[str, float | str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return [{**row, **{feature: float(row[feature]) for feature in FEATURES}} for row in csv.DictReader(handle)]


def fit(reference: list[dict]) -> dict[str, dict[str, float]]:
    if len(reference) < 3:
        raise ValueError("At least three reference records are required")
    model = {}
    for feature in FEATURES:
        values = [float(row[feature]) for row in reference]
        median = statistics.median(values)
        mad = statistics.median([abs(value - median) for value in values]) or 1.0
        model[feature] = {"median": median, "mad": mad}
    return model


def score(row: dict, model: dict[str, dict[str, float]], threshold: float = 3.5) -> dict:
    contributions = {feature: round(0.6745 * abs(float(row[feature]) - baseline["median"]) / baseline["mad"], 3) for feature, baseline in model.items()}
    anomaly_score = max(contributions.values())
    return {"record_id": row["record_id"], "anomaly_score": anomaly_score, "is_anomaly": anomaly_score >= threshold, "feature_contributions": contributions}


def drift(reference: list[dict], live: list[dict]) -> dict[str, float]:
    """Median shift relative to reference MAD; values above 3 merit review."""
    model = fit(reference)
    return {feature: round(abs(statistics.median([float(row[feature]) for row in live]) - baseline["median"]) / baseline["mad"], 3) for feature, baseline in model.items()}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(); parser.add_argument("--reference", type=Path, required=True); parser.add_argument("--live", type=Path, required=True)
    args = parser.parse_args()
    reference, live = read_rows(args.reference), read_rows(args.live)
    model = fit(reference)
    print(json.dumps({"model": model, "scores": [score(row, model) for row in live], "median_shift_in_mad": drift(reference, live)}, indent=2))
