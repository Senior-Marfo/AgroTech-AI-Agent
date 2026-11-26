"""Seeded generator for DRAFT synthetic plantain scenarios (no reference labels).

Plan (Milestone 2 proposal, section 8): 90 scenarios = 30 development + 60 test, split evenly
into normal, ambiguous/incomplete and failure/out-of-scope categories. Reference actions are
assigned later by two independent team members from the cited sources, with a third resolving
disagreements; this script leaves those columns blank on purpose.

All rows are SIMULATED. Results on synthetic cases may not hold on real farms.

Usage (from the repository root):
    python evaluation/generate_scenarios.py            # writes evaluation/scenarios_draft.csv
"""
import csv
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from agro_agent.schema import OBSERVATIONS, RAINFALL_7D, STAGES  # noqa: E402

SEED = 313
PLAN = {"dev": 10, "test": 20}  # cases per category in each split
CATEGORIES = ("normal", "ambiguous", "failure")
COLUMNS = [
    "case_id", "split", "category", "crop", "stage", "soil_moisture_pct",
    "temperature_c", "rainfall_7d", "observation",
    "reference_action", "labeller_a", "labeller_b", "resolved_by",
]


def _normal(rng):
    return {
        "crop": "plantain",
        "stage": rng.choice(STAGES),
        "soil_moisture_pct": round(rng.uniform(10, 60), 1),
        "temperature_c": round(rng.uniform(22, 38), 1),
        "rainfall_7d": rng.choice(RAINFALL_7D),
        "observation": rng.choice(OBSERVATIONS),
    }


def _ambiguous(rng):
    row = _normal(rng)
    row[rng.choice(("soil_moisture_pct", "temperature_c", "rainfall_7d", "observation"))] = ""
    return row


def _failure(rng):
    row = _normal(rng)
    kind = rng.choice(("other_crop", "bad_stage", "impossible_value"))
    if kind == "other_crop":
        row["crop"] = rng.choice(("maize", "cassava", "tomato"))
    elif kind == "bad_stage":
        row["stage"] = "unknown"
    else:
        row["temperature_c"] = 999
    return row


MAKERS = {"normal": _normal, "ambiguous": _ambiguous, "failure": _failure}


def generate(seed: int = SEED) -> list:
    rng = random.Random(seed)
    rows, n = [], 0
    for split, per_category in PLAN.items():
        for category in CATEGORIES:
            for _ in range(per_category):
                n += 1
                row = {c: "" for c in COLUMNS}
                row.update(MAKERS[category](rng))
                row.update(case_id=f"S{n:03d}", split=split, category=category)
                rows.append(row)
    return rows


def main() -> None:
    out = Path(__file__).with_name("scenarios_draft.csv")
    rows = generate()
    with open(out, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} draft scenarios to {out}")


if __name__ == "__main__":
    main()
