# Evidence files (the ONLY way scores in docs/generated/SCORE.md go up)
`python tools/score.py` reads these files. Missing file = criterion stays low. Do not hand-edit generated files.
| File | Produced by | Needed for |
|---|---|---|
| `ci/build.json`, `ci/junit/*.xml` | `.github/workflows/evidence.yml` (automatic) | engineering, privacy, safety guard test |
| `ml/runs/eval.json` | `ml/eval.py` (Colab/GPU) | accuracy (open-data tier) |
| `docs/evidence/distance/*.csv` | tape-measure test, template tools/benchmark/distance_template.csv (>= 30 trials) | accuracy (distance tier) |
| `docs/evidence/metrics/*.csv` | the app's metrics.csv from a real walk (>= 10 min; 2 h for thermal) | speed, reliability |
| `docs/evidence/latency_endtoend.json` | external high-speed-camera test: `{"p95_ms": 120, "method": "...", "date": "YYYY-MM-DD"}` | speed (top tier) |
| `docs/evidence/field_hazard_eval.json` | labelled field walks: `{"recall": {"stairs": 0.93, ...}, "false_alarms_per_5min": 0.6, "minutes": 120, "n_sites": 6, "date": "..."}` | accuracy/safety (top tiers) |
| `docs/evidence/user_study.json` | study per docs/USER_STUDY_PROTOCOL.md: `{"participants": 8, "om_instructor_review": true, "sus_mean": 78, "languages_tested": ["en","hi","te"], "date": "..."}` | safety, UX, languages |
| `docs/evidence/native_review.json` | `{"hi": {"reviewer": "name", "approved": true, "date": "..."}, "te": {...}}` | languages |
| `docs/evidence/oem_tests.json` | `{"samsung": {"minutes": 30, "pass": true, "model": "..."}, "xiaomi": {...}, "oppo": {...}, "vivo": {...}}` | reliability |
| `docs/evidence/field_hours.json` | `{"hours": 25, "crashes": 0}` | reliability (top tier) |
| `docs/evidence/expert_review.json` | `{"reviewers": 2, "scores": {"innovation": 8}}` from 2+ independent experts | innovation (never self-scored) |
| `docs/evidence/independent_replication.json` | `{"replicated_by": "...", "date": "..."}` | any score of 10 |
| `docs/evidence/code_review.json` | `{"reviewer": "...", "approved": true}` | engineering top tier |
| `docs/evidence/features.json` | maintained by hand, honestly | assistant features |
Every JSON needs a `date`. Raw files stay in the repo so reviewers can inspect them.
