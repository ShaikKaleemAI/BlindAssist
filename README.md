# Blind Assist (Android) ![android-ci](https://github.com/<you>/BlindAssist/actions/workflows/android-ci.yml/badge.svg)
Offline, on-device obstacle alerts for a phone in a pocket (English/Hindi/Telugu). **Prototype. Not field-tested. NOT COMPILED LOCALLY.**

> **Safety: this app supplements a white cane or guide dog and never replaces one. It never says the path is clear or safe.**

Status: see docs/SCORECARD.md. Build: `tools/fetch_models.sh` then `./gradlew assembleDebug testDebugUnitTest lintDebug` (see docs/DEPLOY.md for wrapper). No model? The app starts in loud "limited mode" and cannot see obstacles.
Hindi/Telugu text: NEEDS NATIVE REVIEW. Original README: docs/original/README_original.md.
