# evaluation/

Planned protocol (full detail in the M2 proposal):

- 90 synthetic scenarios: 30 development, 60 frozen test (20 normal, 20 ambiguous, 20 failure).
- Same cases, inputs and scoring for B0, P1 and the two ablations (P1-a no ranking, P1-b no evidence gate).
- Metrics: action agreement (also on normal cases alone), unsafe-recommendation rate,
  precision/recall of CLARIFY and REFER, runtime per case.
- Statistics: counts with 95% Wilson intervals; exact McNemar test for B0 vs P1.
- Freeze rule: the test split is frozen before final tuning; any later change is logged with a reason.
- Leakage checks: no identical reading combination in both splits; every threshold has a cited source.

`generate_scenarios.py` produces an unlabelled draft only. The frozen case list, reference labels
and scoring script are Milestone 3 deliverables.
