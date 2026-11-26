# Smart Agricultural Advisory Agent for Maize Smallholders (Team AgroTech)

DCIT 313, Semester 1, 2026/2027, University of Ghana. Route A: rule-based agent.
Status: **Milestone 2 preliminary repository.** No evaluation results exist yet.

## Purpose
A rule-based agent turns a farmer's fixed-choice report (growth stage, soil moisture, temperature,
rainfall, one symptom) into a preliminary action: `RECOMMEND`, `CLARIFY`, `REFER` to an extension
officer, or `REJECT`. It is **non-authoritative**: it never confirms a diagnosis and never gives
chemical or dosage advice. Research question and plan: see `docs/` and the M2 proposal.

## Compare
- `B0` (`src/agro_agent/baseline.py`): independent single-threshold alerts, no abstention.
- `P1` (`src/agro_agent/agent.py`): stage-aware rules, priority ranking, clarify/refer/reject.
  Rules live in `src/agro_agent/rules.json`; each cites its source. **Cut-offs without a source are
  deliberately absent**; the M1 example values used by B0 are illustrative and must be replaced
  before the test set is opened.

## Setup and run
Python 3.10+ is enough; the agent uses only the standard library.

```
pip install -r requirements.txt        # pytest only
python -m pytest                       # automated checks
PYTHONPATH=src python -m agro_agent.cli examples/case_normal.json
PYTHONPATH=src python -m agro_agent.cli examples/case_ambiguous.json
PYTHONPATH=src python -m agro_agent.cli examples/case_failure.json
python evaluation/generate_scenarios.py   # seeded DRAFT scenarios, no labels (seed 313)
```

The three example cases are the normal, ambiguous and failure traces that will be extended into
the three end-to-end traced cases required by the Handbook.

## Layout
```
src/agro_agent/    schema, baseline B0, agent P1, rules.json, logger, cli
tests/             automated checks (normal, boundary, failure)
evaluation/        seeded scenario generator; frozen case list arrives at Milestone 3
data/README.md     provenance, licence and permission status of every source
results/           empty until Milestone 3
docs/              source list and ethics/permission tracker
ai_use_log.md      AI assistance and verification record
```

## Safety and privacy
No personal data is collected or stored. Logs hold only case ID, system, action, rule IDs and
reasons. No API keys or tokens belong in this repository.
