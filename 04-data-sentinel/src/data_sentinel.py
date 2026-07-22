"""Confidence-aware, auditable intake workflow for tabular data."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
import statistics
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlretrieve

UCI_ADULT_URL = "https://archive.ics.uci.edu/ml/machine-learning-databases/adult/adult.data"
CANONICAL_FIELDS = {
    "age": {"aliases": ("age",), "kind": "integer", "required": True, "sensitive": False},
    "workclass": {"aliases": ("workclass", "employment class"), "kind": "text", "required": True, "sensitive": False},
    "education_num": {"aliases": ("education num", "education number"), "kind": "integer", "required": True, "sensitive": False},
    "capital_gain": {"aliases": ("capital gain",), "kind": "integer", "required": True, "sensitive": False},
    "hours_per_week": {"aliases": ("hours per week", "weekly hours"), "kind": "integer", "required": True, "sensitive": False},
    "income": {"aliases": ("income", "income label", "salary band"), "kind": "label", "required": True, "sensitive": False},
    "race": {"aliases": ("race", "ethnicity"), "kind": "text", "required": False, "sensitive": True},
    "sex": {"aliases": ("sex", "gender"), "kind": "text", "required": False, "sensitive": True},
}
ADULT_COLUMNS = ("age", "workclass", "fnlwgt", "education", "education_num", "marital_status", "occupation", "relationship", "race", "sex", "capital_gain", "capital_loss", "hours_per_week", "native_country", "income")
NUMERIC_FIELDS = ("age", "education_num", "capital_gain", "capital_loss", "hours_per_week", "fnlwgt")
INCOME_LABELS = {"<=50K", ">50K", "<=50K.", ">50K."}


def tokens(value: str) -> Counter[str]:
    return Counter(re.findall(r"[a-z0-9]+", value.replace("_", " ").lower()))


def cosine_similarity(left: str, right: str) -> float:
    """Sparse token-vector cosine similarity; replaceable by a dense embedding service."""
    a, b = tokens(left), tokens(right)
    numerator = sum(a[token] * b[token] for token in a.keys() & b.keys())
    denominator = math.sqrt(sum(value * value for value in a.values())) * math.sqrt(sum(value * value for value in b.values()))
    return round(numerator / denominator, 4) if denominator else 0.0


def schema_agent(headers: list[str]) -> list[dict]:
    mappings = []
    for source in headers:
        if source in ADULT_COLUMNS and source not in CANONICAL_FIELDS:
            mappings.append({"source_field": source, "canonical_field": None, "status": "out_of_scope", "confidence": 1.0, "requires_human_approval": False})
            continue
        candidates = [(field, max(cosine_similarity(source, alias) for alias in spec["aliases"])) for field, spec in CANONICAL_FIELDS.items()]
        canonical, confidence = max(candidates, key=lambda item: item[1])
        mappings.append({"source_field": source, "canonical_field": canonical if confidence else None, "status": "mapped" if confidence else "unmapped", "confidence": confidence, "requires_human_approval": confidence < 0.9 or CANONICAL_FIELDS[canonical]["sensitive"]})
    return mappings


def clean(value: str) -> tuple[str | None, float, str | None]:
    original = value
    value = value.strip()
    if value in {"?", "", "NULL", "null"}:
        return None, 1.0, "normalized_missing_marker"
    return value, 1.0, "trimmed" if value != original else None


def validate(row: dict[str, str | None]) -> list[str]:
    failures = []
    for field, spec in CANONICAL_FIELDS.items():
        if spec["required"] and not row.get(field):
            failures.append(f"missing_{field}")
    for field in NUMERIC_FIELDS:
        value = row.get(field)
        if value is None:
            continue
        try:
            if int(value) < 0:
                failures.append(f"negative_{field}")
        except ValueError:
            failures.append(f"invalid_{field}")
    if row.get("income") and row["income"] not in INCOME_LABELS:
        failures.append("invalid_income_label")
    return failures


def numeric_anomaly(row: dict[str, str | None], baselines: dict[str, tuple[float, float]]) -> dict:
    contributions = {}
    for field, (median, mad) in baselines.items():
        if row.get(field) is not None:
            contributions[field] = round(0.6745 * abs(int(row[field]) - median) / mad, 3)
    score = max(contributions.values(), default=0.0)
    return {"score": score, "is_anomaly": score >= 3.5, "feature_contributions": contributions, "confidence": round(min(0.99, 0.5 + score / 10), 3)}


def read_adult(path: Path) -> list[dict[str, str]]:
    rows = []
    with path.open(newline="", encoding="utf-8") as handle:
        for values in csv.reader(handle):
            if not values or values[0].startswith("|"):
                continue
            if len(values) != len(ADULT_COLUMNS):
                raise ValueError(f"Expected {len(ADULT_COLUMNS)} columns, found {len(values)}")
            rows.append(dict(zip(ADULT_COLUMNS, values)))
    if not rows:
        raise ValueError("No records found")
    return rows


def run(path: Path) -> dict:
    raw_rows = read_adult(path)
    cleaned, quarantine, transformation_counts = [], [], Counter()
    for index, raw in enumerate(raw_rows, start=1):
        row, changes = {}, []
        for field, value in raw.items():
            normalized, confidence, action = clean(value)
            row[field] = normalized
            if action:
                changes.append({"field": field, "action": action, "confidence": confidence})
                transformation_counts[action] += 1
        failures = validate(row)
        if failures:
            quarantine.append({"row_number": index, "failures": failures, "raw": raw, "cleaned": row, "cleaning_confidence": 1.0})
        else:
            cleaned.append(row)
    baselines = {field: (statistics.median([int(row[field]) for row in cleaned if row[field] is not None]), 1.0) for field in ("age", "education_num", "hours_per_week")}
    anomalies = [numeric_anomaly(row, baselines) for row in cleaned]
    anomaly_count = sum(item["is_anomaly"] for item in anomalies)
    quality_score = len(cleaned) / len(raw_rows)
    schema = schema_agent(list(raw_rows[0]))
    review_reasons = ["sensitive_fields_detected"] if any(item["canonical_field"] and CANONICAL_FIELDS[item["canonical_field"]]["sensitive"] for item in schema) else []
    if any(item["status"] == "unmapped" or (item["status"] == "mapped" and item["confidence"] < 0.9) for item in schema):
        review_reasons.append("low_confidence_schema_mapping")
    if quarantine:
        decision = "quarantine"
    elif review_reasons:
        decision = "human_review"
    else:
        decision = "accept"
    decision_confidence = round(0.5 * quality_score + 0.3 * (1 - anomaly_count / max(1, len(cleaned))) + 0.2 * min(item["confidence"] for item in schema), 3)
    return {
        "run_at": datetime.now(timezone.utc).isoformat(),
        "source": {"path": str(path), "sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "records_received": len(raw_rows)},
        "decision": {"status": decision, "confidence": decision_confidence, "requires_human_approval": bool(review_reasons), "reasons": review_reasons},
        "agents": {
            "schema_agent": {"mappings": schema, "confidence": min(item["confidence"] for item in schema)},
            "cleaning_agent": {"transformations": dict(transformation_counts), "confidence": 1.0},
            "validation_agent": {"records_valid": len(cleaned), "records_quarantined": len(quarantine), "quality_score": round(quality_score, 4), "confidence": 1.0},
            "anomaly_agent": {"records_flagged": anomaly_count, "rate": round(anomaly_count / max(1, len(cleaned)), 4), "confidence": round(statistics.mean(item["confidence"] for item in anomalies), 3)},
        },
        "quarantine_sample": quarantine[:10],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    fetch = commands.add_parser("fetch"); fetch.add_argument("--output", type=Path, required=True); fetch.add_argument("--url", default=UCI_ADULT_URL)
    execute = commands.add_parser("run"); execute.add_argument("--input", type=Path, required=True); execute.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "fetch":
        args.output.parent.mkdir(parents=True, exist_ok=True); urlretrieve(args.url, args.output); print(json.dumps({"downloaded": str(args.output), "url": args.url}))
    else:
        result = run(args.input); args.output.parent.mkdir(parents=True, exist_ok=True); args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8"); print(json.dumps(result["decision"], indent=2))


if __name__ == "__main__":
    main()
