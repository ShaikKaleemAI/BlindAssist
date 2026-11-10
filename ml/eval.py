"""Per-class recall + confusion matrix on the held-out TEST split. Never report overall mAP alone for safety."""
import argparse
from ultralytics import YOLO

p = argparse.ArgumentParser()
p.add_argument("--weights", default="ml/runs/hazard/weights/best.pt")
p.add_argument("--data", default="ml/dataset/data.yaml")
a = p.parse_args()
m = YOLO(a.weights).val(data=a.data, split="test", plots=True, conf=0.25)
names = m.names
for i, r in zip(m.box.ap_class_index, m.box.r):
    print(f"{names[int(i)]}: recall@conf0.25={r:.3f}")
print("confusion matrix saved in the run directory (confusion_matrix.png)")
