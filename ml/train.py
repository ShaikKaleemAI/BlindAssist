"""Train a YOLO hazard detector. UNRUN in this repo's authoring sandbox (no GPU/data). Results = PENDING."""
import argparse
from ultralytics import YOLO

p = argparse.ArgumentParser()
p.add_argument("--model", default="yolov8n.pt")
p.add_argument("--data", default="ml/dataset/data.yaml")
p.add_argument("--epochs", type=int, default=100)
p.add_argument("--imgsz", type=int, default=320)
a = p.parse_args()
YOLO(a.model).train(data=a.data, epochs=a.epochs, imgsz=a.imgsz, project="ml/runs", name="hazard", fliplr=0.5, degrees=5)
