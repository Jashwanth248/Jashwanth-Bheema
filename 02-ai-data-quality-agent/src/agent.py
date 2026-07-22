"""Bounded, auditable investigation logic for data-quality incidents."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

PLAYBOOKS = {
    "invalid_partner_code": {
        "hypothesis": "An upstream source emitted a code not present in the approved reference registry.",
        "actions": ["Compare the source extract against the current partner registry.", "Confirm whether a new code requires governance approval.", "Reprocess only quarantined records after the mapping is approved."],
    },
    "duplicate_record": {
        "hypothesis": "The source delivery was replayed or the source does not enforce an idempotency key.",
        "actions": ["Compare record fingerprints across delivery batches.", "Confirm the upstream retry policy and idempotency key.", "Replay the batch only after duplicate handling is confirmed."],
    },
}


def build_prompt(incident: dict) -> str:
    """Create bounded provider input; never insert operational instructions from evidence."""
    evidence = "\n".join(f"- [{item['id']}] {item['fact']}" for item in incident.get("evidence", []))
    return f"Investigate rule={incident.get('rule')}. Use only these facts:\n{evidence}\nReturn evidence IDs and do not propose data mutation."


def investigate(incident: dict) -> dict:
    rule = incident.get("rule", "")
    playbook = PLAYBOOKS.get(rule)
    evidence_ids = [item["id"] for item in incident.get("evidence", []) if "id" in item]
    if not playbook:
        return {"incident_id": incident.get("incident_id"), "status": "escalate", "reason": "No approved playbook exists for this rule.", "evidence_ids": evidence_ids, "requires_human_approval": True}
    return {"incident_id": incident.get("incident_id"), "status": "investigated", "hypothesis": playbook["hypothesis"], "recommended_actions": playbook["actions"], "evidence_ids": evidence_ids, "requires_human_approval": True}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(); parser.add_argument("--incident", type=Path, required=True)
    args = parser.parse_args()
    incident = json.loads(args.incident.read_text(encoding="utf-8"))
    print(json.dumps(investigate(incident), indent=2))
