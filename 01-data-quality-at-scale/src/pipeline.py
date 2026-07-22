"""Contract-driven, auditable validation for inbound transaction records."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter
from datetime import date
from pathlib import Path

ALLOWED_PARTNERS = {"ACME", "BRAVO", "CYPRESS"}
REQUIRED_COLUMNS = ("transaction_id", "partner_code", "amount", "received_at")


def fingerprint(row: dict[str, str]) -> str:
    payload = "|".join(row.get(column, "").strip() for column in REQUIRED_COLUMNS)
    return hashlib.sha256(payload.encode()).hexdigest()[:16]


def validate(row: dict[str, str], seen: set[str], today: date | None = None) -> list[str]:
    """Return all contract failures for a row, preserving evidence for triage."""
    today = today or date.today()
    errors = [f"missing_{column}" for column in REQUIRED_COLUMNS if not row.get(column, "").strip()]
    key = fingerprint(row)
    if key in seen:
        errors.append("duplicate_record")
    seen.add(key)
    if row.get("partner_code") and row["partner_code"] not in ALLOWED_PARTNERS:
        errors.append("invalid_partner_code")
    try:
        if float(row.get("amount", "")) <= 0:
            errors.append("amount_must_be_positive")
    except ValueError:
        errors.append("invalid_amount")
    try:
        if date.fromisoformat(row.get("received_at", "")) > today:
            errors.append("received_at_in_future")
    except ValueError:
        errors.append("invalid_received_at")
    return errors


def run(input_path: Path, output_dir: Path, today: date | None = None) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    seen, valid, quarantine, reasons = set(), [], [], Counter()
    with input_path.open(newline="", encoding="utf-8") as source:
        reader = csv.DictReader(source)
        if not reader.fieldnames or set(REQUIRED_COLUMNS) - set(reader.fieldnames):
            raise ValueError("Input does not satisfy the required column contract")
        for row in reader:
            errors = validate(row, seen, today)
            if errors:
                quarantine.append({**row, "error_codes": ";".join(errors), "record_fingerprint": fingerprint(row)})
                reasons.update(errors)
            else:
                valid.append(row)
    for name, records in (("valid.csv", valid), ("quarantine.csv", quarantine)):
        fields = list(records[0]) if records else list(REQUIRED_COLUMNS)
        with (output_dir / name).open("w", newline="", encoding="utf-8") as target:
            writer = csv.DictWriter(target, fieldnames=fields)
            writer.writeheader(); writer.writerows(records)
    total = len(valid) + len(quarantine)
    report = {"records_received": total, "records_valid": len(valid), "records_quarantined": len(quarantine), "quality_score": round(len(valid) / total, 4) if total else 1.0, "failure_counts": dict(reasons)}
    (output_dir / "quality_report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(run(args.input, args.output_dir), indent=2))
