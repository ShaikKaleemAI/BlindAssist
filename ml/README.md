# ml/ — hazard model pipeline (status: scripts written, NOT RUN; no dataset, no GPU in authoring sandbox)
1. Collect + label: ml/dataset/COLLECTION_PLAN.md  2. `python ml/dataset/split_dataset.py <raw>`
3. `python ml/train.py`  4. `python ml/export_tflite_int8.py`  5. `python ml/eval.py`
6. Copy `hazard_yolo_int8.tflite` to `app/src/main/assets/models/`. The app does NOT yet load it (Stage 2 runtime = TODO; app uses COCO EfficientDet-Lite0 or limited mode).
