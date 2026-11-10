# Scorecard (updated each stage). Scores 1-10; no 9/10 without field data.
| Area | Score | Evidence | Tag |
|---|---|---|---|
| Innovation | 4 | Pocket-mode design + range fusion + TTC are in the original code; nothing new measured | ASSUMED |
| Accuracy | 2 | No tape-measure data, no hazard model, COCO only | UNVERIFIED |
| Speed | ? | Metrics CSV logger exists (docs/ARCHITECTURE.md); no device run | UNVERIFIED |
| Safety | 3 | Cane-first wording, never "clear", limited-mode warning, unit-test guard; no field test | UNVERIFIED |
| Assistant quality | 1 | Only earphone-button "what's around me"; no voice, OCR, navigation | VERIFIED (by absence) |

## Targets
| Target | Status | Procedure |
|---|---|---|
| Distance error <10% at 1-5 m | UNVERIFIED | tools/benchmark/analyze_distance.py with tape-measure CSV |
| Hazard recall >90%, <1 false alarm / 5 min | UNVERIFIED | ml/eval.py on site-held-out test set + 30-min walk logs |
| Latency <150 ms, 15+ fps | UNVERIFIED | metrics.csv from app (internal filesDir); true photon-to-alert needs 240 fps camera test |
| 2 h without overheating | UNVERIFIED | 2 h walk with metrics.csv temp column |
| Build green | NOT COMPILED LOCALLY | CI run of android-ci.yml |

## Stage status
Stage 0 done. Stage 1 done in code, not built. Stage 2: dataset plan + scripts only, no runtime hazard detector. Stages 3-9: NOT STARTED.
