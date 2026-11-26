"""Automated checks: normal, boundary and failure cases (Handbook section 6.1)."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "evaluation"))

from agro_agent import agent, baseline  # noqa: E402
from agro_agent.decision import CLARIFY, RECOMMEND, REFER, REJECT  # noqa: E402
from agro_agent.logger import LOG_FIELDS, log_decision  # noqa: E402
import generate_scenarios  # noqa: E402


def case(**overrides):
    base = {
        "case_id": "T",
        "crop": "maize",
        "stage": "vegetative",
        "soil_moisture_pct": 40,
        "temperature_c": 30,
        "rainfall_7d": "light",
        "symptom": "none",
    }
    base.update(overrides)
    return base


def test_normal_pest_sign_recommends_scouting_with_source():
    d = agent.decide(case(symptom="windowpane_holes_and_frass"))
    assert d.action == RECOMMEND
    assert "R-FAW-01" in d.rule_ids
    assert d.sources and "IITA" in d.sources[0]
    assert "not a diagnosis" in d.message.lower()


def test_no_concern_gives_monitoring_advice():
    assert agent.decide(case()).rule_ids == ("R-MONITOR-00",)


def test_missing_value_triggers_clarify():
    raw = case()
    del raw["temperature_c"]
    d = agent.decide(raw)
    assert d.action == CLARIFY and "temperature_c" in d.message


def test_other_crop_is_rejected():
    assert agent.decide(case(crop="sorghum")).action == REJECT


def test_impossible_temperature_is_rejected():
    assert agent.decide(case(temperature_c=999)).action == REJECT


def test_non_dict_input_is_rejected_not_crashed():
    assert agent.decide("not a report").action == REJECT


def test_flowering_without_rain_is_referred_until_cutoff_is_sourced():
    d = agent.decide(case(stage="flowering", rainfall_7d="none"))
    assert d.action == REFER and d.rule_ids[0] == "R-FLOW-WATER-01"


def test_priority_ranking_puts_stage_critical_concern_first():
    d = agent.decide(case(stage="flowering", rainfall_7d="none", symptom="yellowing"))
    assert d.rule_ids[:2] == ("R-FLOW-WATER-01", "R-UNMATCHED-SYMPTOM-01")


def test_baseline_alerts_on_single_thresholds_and_never_abstains():
    d = baseline.decide(case(soil_moisture_pct=15, temperature_c=36, rainfall_7d="none"))
    assert d.action == RECOMMEND and "Soil moisture is low" in d.message
    raw = case()
    del raw["temperature_c"]
    assert baseline.decide(raw).action == RECOMMEND  # no CLARIFY in B0


def test_log_contains_only_whitelisted_fields(tmp_path):
    record = log_decision(agent.decide(case()), "P1", tmp_path / "log.jsonl")
    assert tuple(record) == LOG_FIELDS
    line = (tmp_path / "log.jsonl").read_text().strip()
    assert set(json.loads(line)) == set(LOG_FIELDS)


def test_scenario_generator_is_seeded_and_matches_plan():
    a, b = generate_scenarios.generate(), generate_scenarios.generate()
    assert a == b
    assert len(a) == 90
    assert sum(r["split"] == "test" for r in a) == 60
    assert all(r["reference_action"] == "" for r in a)
