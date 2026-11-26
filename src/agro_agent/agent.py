"""Proposed agent P1 (stub): validate -> fire stage rules -> rank -> choose one action.

Decision order:
1. Malformed or out-of-scope input        -> REJECT
2. A required observation is missing      -> CLARIFY (ask for it)
3. Rules whose `when` conditions hold fire; the lowest priority number wins
4. Nothing fires                          -> REFER (no supported rule)
"""
import json
from pathlib import Path

from .decision import CLARIFY, NON_AUTHORITATIVE, REFER, REJECT, Decision
from .schema import Observation, ValidationError, validate

RULES_PATH = Path(__file__).with_name("rules.json")


def load_rules(path: Path = RULES_PATH) -> list:
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)["rules"]


def _fires(rule: dict, obs: Observation) -> bool:
    return all(getattr(obs, key) in allowed for key, allowed in rule["when"].items())


def decide(raw: dict, rules=None) -> Decision:
    rules = load_rules() if rules is None else rules
    obs = Observation.from_raw(raw if isinstance(raw, dict) else {})
    case_id = obs.case_id or "UNKNOWN"

    try:
        validate(obs)
    except ValidationError as err:
        return Decision(case_id, REJECT, f"Input not accepted: {err}", reasons=(str(err),))

    missing = obs.missing_fields()
    if missing:
        return Decision(
            case_id,
            CLARIFY,
            "Please provide: " + ", ".join(missing) + ".",
            reasons=("missing required observation(s): " + ", ".join(missing),),
        )

    fired = sorted((r for r in rules if _fires(r, obs)), key=lambda r: r["priority"])
    if not fired:
        return Decision(
            case_id,
            REFER,
            "No supported rule matches this report. Please ask your extension officer. "
            + NON_AUTHORITATIVE,
            reasons=("no rule fired",),
        )

    top = fired[0]
    return Decision(
        case_id,
        top["action"],
        f"{top['message']} {NON_AUTHORITATIVE}",
        rule_ids=tuple(r["id"] for r in fired),
        reasons=(f"top concern: {top['concern']}",)
        + tuple(f"also fired: {r['id']}" for r in fired[1:]),
        sources=(top["source"],),
    )
