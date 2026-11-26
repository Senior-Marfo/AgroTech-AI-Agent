"""Run one case through the baseline and the proposed agent and log both.

Usage (from the repository root):
    python -m agro_agent.cli examples/case_normal.json
"""
import argparse
import json
import sys
from pathlib import Path

from . import agent, baseline
from .logger import log_decision


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("case_file", help="JSON file with one farmer report")
    parser.add_argument("--log", default="results/decision_log.jsonl")
    args = parser.parse_args(argv)

    try:
        raw = json.loads(Path(args.case_file).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as err:
        print(f"Could not read case file: {err}", file=sys.stderr)
        return 2

    for name, system in (("B0", baseline), ("P1", agent)):
        decision = system.decide(raw)
        log_decision(decision, name, Path(args.log))
        print(f"[{name}] {decision.action}: {decision.message}")
        if decision.reasons:
            print(f"      why: {'; '.join(decision.reasons)}")
        if decision.sources:
            print(f"      source: {'; '.join(decision.sources)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
