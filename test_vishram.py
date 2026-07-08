import sys
import os
import cv2
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend.inference.pose_estimator import YoloPoseEstimator
from backend.evaluation.evaluator import StaticPostureEvaluator

estimator = YoloPoseEstimator(
    model_path="backend/yolo11n-pose.pt",
    confidence=0.5,
    image_size=640,
    prefer_half_precision=True
)
image_path = sys.argv[1]

img = cv2.imread(image_path)
if img is None:
    print(f"Failed to load {image_path}")
    sys.exit(1)

detections = estimator.infer(img)
if not detections:
    print("No pose detected")
    sys.exit(1)

evaluator = StaticPostureEvaluator("VISHRAM")
res = evaluator.evaluate(detections[0], camera_type="front")

print(f"Mode: {res.mode}, Status: {res.status}, Score: {res.overall_score}")
for r in res.rules:
    print(f"Rule: {r.name}, Status: {r.status}, Score: {r.score}, Message: {r.message}")
