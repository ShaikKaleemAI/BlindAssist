# Blind Assist (Android) ![android-ci](https://github.com/<you>/BlindAssist/actions/workflows/android-ci.yml/badge.svg)
Offline, on-device obstacle alerts for a phone in a pocket (English/Hindi/Telugu). **Prototype. Not field-tested. NOT COMPILED LOCALLY.**

> **Safety: this app supplements a white cane or guide dog and never replaces one. It never says the path is clear or safe.**

Status: see docs/SCORECARD.md. Build: `tools/fetch_models.sh` then `./gradlew assembleDebug testDebugUnitTest lintDebug` (see docs/DEPLOY.md for wrapper). No model? The app starts in loud "limited mode" and cannot see obstacles.
Hindi/Telugu text: NEEDS NATIVE REVIEW. Original README: docs/original/README_original.md.

## Status snapshot
Hazard-model runtime, free-space logic, OCR "read this" (earphone next button), thermal/OEM handling exist in code; trained hazard model, depth model, voice recognition, GPS, face memory, SOS delivery do not. See docs/SCORECARD.md. Nothing here has been compiled or field-tested.

## How this project is verified and rated
Verification is automated, not claimed: `.github/workflows/evidence.yml` builds, runs the unit tests, lint and an emulator smoke test, checks the merged manifest for INTERNET, then `tools/score.py` writes `docs/generated/SCORE.md`. Field evidence files (docs/evidence/README.md) are what raise the scores; nothing is self-assigned.
