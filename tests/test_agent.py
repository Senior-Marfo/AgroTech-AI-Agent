"""Automated checks: normal, boundary and failure cases (Handbook section 6.1)."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "evaluation"))

from agro_agent import agent, baseline  # noqa: E402
from agro_agent.schema import STAGES  # noqa: E402
from agro_agent.decision import CLARIFY, RECOMMEND, REFER, REJECT  # noqa: E402
from agro_agent.logger import LOG_FIELDS, log_decision  # noqa: E402
import generate_scenarios  # noqa: E402


def case(**overrides):
    base = {
        "case_id": "T",
        "crop": "plantain",
        "stage": "nurturing",
        "soil_moisture_pct": 40,
        "temperature_c": 30,
        "rainfall_7d": "light",
        "observation": "none",
    }
    base.update(overrides)
    return base


def test_normal_weevil_sign_recommends_sanitation_with_source():
    d = agent.decide(case(observation="weevil_damage_at_base"))
    assert d.action == RECOMMEND
    assert "R-WEEVIL-01" in d.rule_ids
    assert d.sources and "Nkakwa" in d.sources[0]
    assert "not a diagnosis" in d.message.lower()


def test_no_concern_gives_monitoring_advice():
    assert agent.decide(case()).rule_ids == ("R-MONITOR-00",)


def test_missing_value_triggers_clarify():
    raw = case()
    del raw["temperature_c"]
    d = agent.decide(raw)
    assert d.action == CLARIFY and "temperature_c" in d.message


def test_other_crop_is_rejected():
    assert agent.decide(case(crop="maize")).action == REJECT


def test_impossible_temperature_is_rejected():
    assert agent.decide(case(temperature_c=999)).action == REJECT


def test_unknown_stage_is_rejected():
    assert agent.decide(case(stage="unknown")).action == REJECT


def test_non_dict_input_is_rejected_not_crashed():
    assert agent.decide("not a report").action == REJECT


# One farmer task per row: (stage, observation, expected rule id).
STAGE_TASKS = [
    ("pre_planting", "land_not_cleared", "R-CLEAR-01"),
    ("planting", "holes_not_dug", "R-HOLES-01"),
    ("planting", "sockets_not_planted", "R-PLANT-01"),
    ("nurturing", "weeds_present", "R-WEED-01"),
    ("nurturing", "bare_soil_no_humus", "R-HUMUS-01"),
    ("nurturing", "plant_leaning_or_bending", "R-PROP-01"),
    ("harvesting", "flower_emerged", "R-FLOWER-01"),
    ("harvesting", "bunch_looks_mature", "R-HARVEST-01"),
    ("socket_replacement", "harvested_stalk_standing", "R-STALK-01"),
    ("socket_replacement", "sockets_available", "R-SOCKET-PROP-01"),
    ("socket_replacement", "sockets_ready_to_harvest", "R-SOCKET-HARVEST-01"),
]


def test_every_stage_task_has_a_rule():
    for stage, observation, rule_id in STAGE_TASKS:
        d = agent.decide(case(stage=stage, observation=observation))
        assert d.action == RECOMMEND and d.rule_ids[0] == rule_id, (stage, observation)


def test_all_five_stages_are_covered_by_tasks():
    assert {s for s, _, _ in STAGE_TASKS} == set(STAGES)


def test_watering_if_rains_fail_in_nurturing_and_socket_replacement():
    assert agent.decide(case(rainfall_7d="none")).rule_ids[0] == "R-WATER-NURT-01"
    d = agent.decide(case(stage="socket_replacement", rainfall_7d="none"))
    assert d.rule_ids[0] == "R-WATER-SOCKET-01"


def test_importing_sockets_is_referred_to_an_officer():
    d = agent.decide(case(stage="pre_planting", observation="sockets_to_import"))
    assert d.action == REFER and d.rule_ids[0] == "R-IMPORT-01"


def test_task_in_the_wrong_stage_is_referred_not_guessed():
    d = agent.decide(case(stage="harvesting", observation="weeds_present"))
    assert d.action == REFER and d.rule_ids == ()


def test_unexplained_sign_is_referred():
    d = agent.decide(case(observation="yellowing"))
    assert d.action == REFER and d.rule_ids[0] == "R-UNMATCHED-OBS-01"


def test_priority_ranking_puts_stage_critical_concern_first():
    d = agent.decide(case(rainfall_7d="none", observation="weevil_damage_at_base"))
    assert d.rule_ids[:2] == ("R-WATER-NURT-01", "R-WEEVIL-01")


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
