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
- Stage 0: done. Stage 1: done in code, not built.
- Stage 2: dataset plan + train/export/eval scripts only; no runtime hazard detector. NOT RUN.
- Stage 1 addendum: replay-from-video (debug-only receiver -> tape) + JVM ReplayRunner + ablation switches implemented, tests written, NOT run; video orientation handling UNVERIFIED.
- Stage 3 (depth/free space): NOT STARTED (needs a quantized depth model + device).
- Stage 4: step detector, orientation/roll helper, sway estimator, height-from-walking math = library + unit tests (not run). NOT wired into the service: roll is not applied to frames, sway is not fed to range fusion, no calibration UI. Thresholds ASSUMED.
- Stage 8 (partial): thermal frame-skipping + spoken hot warning wired in the service (thresholds ASSUMED, UNVERIFIED on device). OEM survival, battery-optimization prompt, crash recovery: NOT STARTED.
- Stage 5 (partial): text-to-command parser (en/hi/te) + unit tests (not run). No wake word, no speech recognition, no actions wired. Hindi/Telugu phrases NEEDS NATIVE REVIEW.
- Stage 9 (partial): Python tools for metrics.csv summary, distance benchmark, confusion matrix/per-class recall, ablation plan; 5 Python unit tests PASSED locally (VERIFIED, tooling only; says nothing about the app). Ablation runner = tools/ablation/run_gradle.sh (needs a tape + Gradle; never run). Paper/slides/protocol hold PENDING FIELD DATA.
- Stage 7 (partial, logic only, NOT wired into the service, tests not run): fall detector, SOS countdown, adaptive verbosity (critical never suppressed; quiet only suggested, never auto-applied), on-device place store, daily summary. NOT implemented: face memory (needs consent UI + biometric-privacy review), caregiver link and SOS delivery (needs SMS/network permission and explicit opt-in), GPS capture, low-battery alerts, UI, persistence. Fall thresholds ASSUMED.
- Stage 6 (navigation/OCR): NOT STARTED.
