"""Baseline B0: independent single-threshold alerts.

Each reading is compared with one fixed threshold; every breach raises a general alert.
The crop stage is ignored. There is no CLARIFY or REFER, and input is not validated
(missing values simply raise no alert).

The cut-offs below are the illustrative values from the Milestone 1 pitch. They are NOT
yet sourced and must be replaced by sourced values and frozen before the test set is opened.
"""
from .decision import RECOMMEND, Decision
from .schema import Observation

THRESHOLDS = {
    "low_soil_moisture_pct": 20.0,  # illustrative (M1), unsourced
    "high_temperature_c": 34.0,  # illustrative (M1), unsourced
}


def decide(raw: dict, thresholds=None) -> Decision:
    t = THRESHOLDS if thresholds is None else thresholds
    obs = Observation.from_raw(raw if isinstance(raw, dict) else {})
    alerts = []
    if isinstance(obs.soil_moisture_pct, float) and obs.soil_moisture_pct < t["low_soil_moisture_pct"]:
        alerts.append("Soil moisture is low: check the soil.")
    if isinstance(obs.temperature_c, float) and obs.temperature_c > t["high_temperature_c"]:
        alerts.append("Temperature is high: consider irrigation.")
    if obs.rainfall_7d == "none":
        alerts.append("No rain this week: monitor the field.")
    if obs.observation not in (None, "none"):
        alerts.append("An observation was reported: inspect the crop.")
    message = " ".join(alerts) if alerts else "No alert."
    return Decision(
        obs.case_id or "UNKNOWN",
        RECOMMEND,
        message,
        reasons=tuple(alerts) or ("no threshold breached",),
    )
