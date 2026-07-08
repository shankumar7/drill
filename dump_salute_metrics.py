import sys
import os
import cv2
import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend.inference.pose_estimator import YoloPoseEstimator
from backend.evaluation.geometry import angle_degrees, segment_length

estimator = YoloPoseEstimator(
    model_path="backend/yolo11n-pose.pt",
    confidence=0.5,
    image_size=640,
    prefer_half_precision=True
)
image_path = sys.argv[1]
img = cv2.imread(image_path)
detections = estimator.infer(img)
k = detections[0].keypoints

# Left arm: 5, 7, 9 (Shoulder, Elbow, Wrist)
left_angle = angle_degrees(k[9, :2], k[7, :2], k[5, :2])
print(f"Left Arm Angle (Shoulder-Elbow-Wrist): {left_angle:.1f} degrees")

# Right arm: 6, 8, 10
right_angle = angle_degrees(k[10, :2], k[8, :2], k[6, :2])
print(f"Right Arm Angle (Shoulder-Elbow-Wrist): {right_angle:.1f} degrees")

# Spine length: from neck(midpoint of shoulders) to hip(midpoint of hips)
neck = (k[5, :2] + k[6, :2]) / 2
hip = (k[11, :2] + k[12, :2]) / 2
spine_len = segment_length(neck, hip)
print(f"Spine length: {spine_len:.1f} pixels")

# Elbow drop
elbow_drop = (k[8, 1] - k[6, 1]) / spine_len
print(f"Right Elbow Drop: {elbow_drop:.3f}")
r_wrist = k[10, :2]
r_eye = k[2, :2]
dist = segment_length(r_wrist, r_eye)
norm_dist = dist / spine_len
print(f"Right Wrist to Right Eye (normalized by spine): {norm_dist:.3f}")
