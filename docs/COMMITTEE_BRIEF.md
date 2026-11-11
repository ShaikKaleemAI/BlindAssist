# Committee brief — Blind Assist prototype v0.3.0
**One line:** an offline, pocket-worn obstacle-alert assistant for blind pedestrians (English, Hindi, Telugu) that supplements a cane or guide dog and never replaces one.
**Status in one sentence:** working prototype that builds and passes automated logic tests in CI; NOT yet measured on real streets and NOT tested with blind users.

## Honest self-assessment (use this instead of a headline score)
| Criterion | What we can show live | Evidence | Gap |
|---|---|---|---|
| Innovation | Pocket-worn, fully offline, cane-first design; range fusion + time-to-collision; open-data training pipeline | design docs, code | no comparison with other systems |
| Accuracy | simulated scenarios with known truth | unit tests | real distance error and hazard recall PENDING (tools exist) |
| Speed | — | metrics logger built | latency/fps on phones PENDING |
| Safety design | never says "clear"; limited-mode and failure warnings; local fall alarm | unit tests, code | no field validation |
| User experience | earphone-button control, spoken output, readiness check | demo | no blind-user feedback |
| Reliability | thermal throttling, wake-lock refresh, crash notice | code | OEM screen-off and 2 h runs PENDING |
| Privacy | on-device processing | readiness check reports INTERNET permission | verify merged manifest |
| Engineering | CI builds and runs unit tests | GitHub Actions | lint status: check |
We deliberately do not claim a numeric score above what the evidence supports.

## Live demo run-sheet (5 minutes, earphones plugged in)
1. Open the app. Read the banner: prototype, supplements a cane.
2. Tap **Run readiness check**: it speaks and lists camera, sensors, detector (hazard model / COCO only / limited mode), battery exemption, INTERNET permission. Point out any WARN honestly.
3. Tap **Run simulated demo** and play each scenario (person, car, pole, stairs). The app first says it is simulated. Explain: real ranging, tracking and alert code, synthetic detections.
4. (Optional) Press START with the phone held upright, camera facing a person or chair; hear live alerts. Only do this if the detector line shows a model (not "limited mode").
5. Show docs/SCORECARD.md and the evidence-status slide.
Do NOT: say the app "keeps users safe", show any number that is not in the repo, or demo "limited mode" as if it were detecting.

## Likely questions and honest answers
- **How accurate is it?** Not yet measured. The tape-measure benchmark and hazard evaluation are built and pending a run; open-data results will be labelled as such.
- **Has it been tested with blind people?** No. We will not do so before an O&M instructor reviews the safety design.
- **Why not just use Seeing AI / Lookout / Be My Eyes?** Those recognise and describe; this is a continuous obstacle-warning layer that works offline in a pocket. It is complementary, and it is not proven better.
- **What if the model misses something?** It can. The cane stays primary, the app never says the path is clear, and unknown objects are not detected.
- **Does data leave the phone?** Core processing is on-device; the readiness check shows whether the build declares INTERNET. Face memory and SOS delivery are not built.
- **What does it cost to run?** Free libraries and open datasets; licences are tracked in docs/generated/DATA_LICENSES.md (after the data pipeline runs).
- **What is the fall alarm?** Local sound and vibration after a suspected fall; no message or call is sent.
- **Hindi/Telugu quality?** Machine-drafted, flagged NEEDS NATIVE REVIEW.

## Pre-demo checklist
- [ ] Latest GitHub Actions run is green (otherwise the demo build may not match the repo).
- [ ] Debug APK installed from that run; readiness check shows no FAIL you did not expect.
- [ ] Phone charged, volume up, earphones tested, TTS voices for the chosen language installed.
- [ ] Deck test count updated to the number shown on the Actions run.
- [ ] Open-data results added to the deck if you have run the Colab notebook.
