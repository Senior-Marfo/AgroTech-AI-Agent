"""Append-only JSONL log. Only whitelisted, non-personal fields are written."""
import json
from pathlib import Path

from .decision import Decision

LOG_FIELDS = ("case_id", "system", "action", "rule_ids", "reasons")


def log_decision(decision: Decision, system: str, path: Path) -> dict:
    record = {
        "case_id": decision.case_id,
        "system": system,
        "action": decision.action,
        "rule_ids": list(decision.rule_ids),
        "reasons": list(decision.reasons),
    }
    assert tuple(record) == LOG_FIELDS
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as handle:
        handle.write(json.dumps(record) + "\n")
    return record
