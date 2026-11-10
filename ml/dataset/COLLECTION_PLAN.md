# Collection + labeling plan (status: PLAN ONLY — no data collected; dataset size = PENDING FIELD DATA)
- Capture with the target phone at pocket height (85 cm trouser / 120 cm shirt), walking, portrait, 640x480+; video at 10 fps extraction.
- Cover: day/dusk/night, rain, indoor/outdoor, Indian street scenes, multiple phones, motion blur from walking.
- Per class aim for diverse sites, not many frames from one site. Split by SITE (not by frame) to avoid leakage: `python ml/dataset/split_dataset.py`.
- Label in CVAT / Label Studio, YOLO format. Two annotators on a 10% subset; report agreement.
- Hard negatives: shadows, painted lines, puddles, tiles, reflections (these drive false alarms).
- Privacy: blur faces/plates before sharing; get consent; keep raw video on-device/private.
- Safety-critical classes (stairs_down, open_drain, pothole) need the most data; report per-class recall, never just mAP.
