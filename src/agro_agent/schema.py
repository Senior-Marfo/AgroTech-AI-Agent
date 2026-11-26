"""Input schema and validation for the plantain advisory agent.

Inputs are fixed choices or bounded numbers; free text is not accepted.
Bounds below are plausibility checks for malformed data, not agronomic thresholds.
"""
from dataclasses import dataclass
from typing import Optional

STAGES = ("pre_planting", "planting", "nurturing", "harvesting", "socket_replacement")
RAINFALL_7D = ("none", "light", "moderate", "heavy")
# One observation from a fixed list. Most values map to a farmer task of the matching stage
# ("socket" = sucker used as planting material).
OBSERVATIONS = (
    "none",
    "land_not_cleared",  # pre_planting
    "sockets_to_import",  # pre_planting
    "holes_not_dug",  # planting
    "sockets_not_planted",  # planting
    "weeds_present",  # nurturing
    "bare_soil_no_humus",  # nurturing
    "plant_leaning_or_bending",  # nurturing
    "weevil_damage_at_base",  # any stage
    "flower_emerged",  # harvesting
    "bunch_looks_mature",  # harvesting
    "harvested_stalk_standing",  # socket_replacement
    "sockets_available",  # socket_replacement
    "sockets_ready_to_harvest",  # socket_replacement
    "wilting_or_leaf_rolling",
    "yellowing",
    "other",
)
SUPPORTED_CROP = "plantain"

SOIL_MOISTURE_RANGE = (0.0, 100.0)  # percent
TEMPERATURE_RANGE = (0.0, 60.0)  # degrees Celsius, plausibility only

# Fields whose absence leads to CLARIFY (ask the farmer), not REJECT.
CLARIFIABLE = ("soil_moisture_pct", "temperature_c", "rainfall_7d", "observation")


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
    observation: Optional[str]

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
            observation=text("observation"),
        )

    def missing_fields(self) -> list:
        return [f for f in CLARIFIABLE if getattr(self, f) is None]


def validate(obs: Observation) -> None:
    """Strict check of scope and ranges. Raises ValidationError on any problem."""
    if not obs.case_id:
        raise ValidationError("case_id is required")
    if obs.crop != SUPPORTED_CROP:
        raise ValidationError(f"crop '{obs.crop}' is out of scope; only plantain is supported")
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
    if obs.observation is not None and obs.observation not in OBSERVATIONS:
        raise ValidationError(f"observation must be one of {OBSERVATIONS}")
