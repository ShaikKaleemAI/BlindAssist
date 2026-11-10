# Architecture
camera (CameraX 640x480 RGBA) -> rotate (gravity/upside-down) -> `Detector` (MediaPipe EfficientDet-Lite0 | `NullDetector` limited mode)
-> `estimateRange` (width/height/ground cues, inverse-variance fusion) -> `Tracker` (IoU + 1-D Kalman + looming TTC)
-> `AlertEngine` + `Avoidance` -> `Speech` (priority TTS) / `Earcons` (panned beeps) / vibration. `MetricsLogger` writes metrics.csv to app-private storage.
Pure-Kotlin logic (everything except Detector, Audio, Sensors, AssistService, MainActivity) is JVM-unit-tested.
Replay-from-video mode: NOT IMPLEMENTED (Stage 1 TODO(user)/next run).
