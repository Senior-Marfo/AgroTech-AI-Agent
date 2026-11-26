"""Shared decision record and action names."""
from dataclasses import dataclass, field

RECOMMEND = "RECOMMEND"
CLARIFY = "CLARIFY"
REFER = "REFER"
REJECT = "REJECT"
ACTIONS = (RECOMMEND, CLARIFY, REFER, REJECT)

NON_AUTHORITATIVE = (
    "Preliminary guidance only, not a diagnosis. Check with your agricultural "
    "extension officer before acting."
)


@dataclass(frozen=True)
class Decision:
    case_id: str
    action: str
    message: str
    rule_ids: tuple = field(default_factory=tuple)
    reasons: tuple = field(default_factory=tuple)
    sources: tuple = field(default_factory=tuple)
