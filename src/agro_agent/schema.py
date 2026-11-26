"""Input schema and validation for the maize advisory agent.

Inputs are fixed choices or bounded numbers; free text is not accepted.
Bounds below are plausibility checks for malformed data, not agronomic thresholds.
"""
from dataclasses import dataclass
from typing import Optional

STAGES = ("establishment", "vegetative", "flowering", "grain_filling", "ripening")
RAINFALL_7D = ("none", "light", "moderate", "heavy")
SYMPTOMS = (
    "none",
    "wilting_or_leaf_rolling",
    "windowpane_holes_and_frass",
    "yellowing",
    "brown_leaf_edges",
    "other",
)
SUPPORTED_CROP = "maize"

SOIL_MOISTURE_RANGE = (0.0, 100.0)  # percent
TEMPERATURE_RANGE = (0.0, 60.0)  # degrees Celsius, plausibility only

# Fields whose absence leads to CLARIFY (ask the farmer), not REJECT.
CLARIFIABLE = ("soil_moisture_pct", "temperature_c", "rainfall_7d", "symptom")


class ValidationError(ValueError):
    """Raised for malformed or out-of-scope input (the agent answers REJECT)."""


@dataclass(frozen=True)
class Observation:
    case_id: Optional[str]
    crop: Optional[str]
    stage: Optional[str]
    soil_moisture_pct: Optional[float]
    temperature_c: Optional[float]
    rainfall_7d: Optional[str]
    symptom: Optional[str]

    @classmethod
    def from_raw(cls, raw: dict) -> "Observation":
        """Lenient parse: copies fields, does no checking. Used by the baseline."""
        def num(key):
            value = raw.get(key)
            if value in (None, ""):
                return None
            try:
                return float(value)
            except (TypeError, ValueError):
                return value  # kept as-is so validate() can reject it

        def text(key):
            value = raw.get(key)
            return None if value in (None, "") else value

        return cls(
            case_id=text("case_id"),
            crop=text("crop"),
            stage=text("stage"),
            soil_moisture_pct=num("soil_moisture_pct"),
            temperature_c=num("temperature_c"),
            rainfall_7d=text("rainfall_7d"),
            symptom=text("symptom"),
        )

    def missing_fields(self) -> list:
        return [f for f in CLARIFIABLE if getattr(self, f) is None]


def validate(obs: Observation) -> None:
    """Strict check of scope and ranges. Raises ValidationError on any problem."""
    if not obs.case_id:
        raise ValidationError("case_id is required")
    if obs.crop != SUPPORTED_CROP:
        raise ValidationError(f"crop '{obs.crop}' is out of scope; only maize is supported")
    if obs.stage not in STAGES:
        raise ValidationError(f"stage '{obs.stage}' is not one of {STAGES}")
    for name, (low, high) in (
        ("soil_moisture_pct", SOIL_MOISTURE_RANGE),
        ("temperature_c", TEMPERATURE_RANGE),
    ):
        value = getattr(obs, name)
        if value is None:
            continue
        if not isinstance(value, float) or not (low <= value <= high):
            raise ValidationError(f"{name} must be a number between {low} and {high}")
    if obs.rainfall_7d is not None and obs.rainfall_7d not in RAINFALL_7D:
        raise ValidationError(f"rainfall_7d must be one of {RAINFALL_7D}")
    if obs.symptom is not None and obs.symptom not in SYMPTOMS:
        raise ValidationError(f"symptom must be one of {SYMPTOMS}")
