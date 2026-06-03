"""Real‑time MediaPipe (RTM) pose estimator.
Implements the same `infer` signature as the existing YOLO estimator.
"""
import cv2
import mediapipe as mp
import numpy as np
from backend.core.types import PoseDetection

class RTMPoseEstimator:
    def __init__(self):
        self.pose = mp.solutions.pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            enable_segmentation=False,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        )

    def infer(self, frame: np.ndarray) -> list[PoseDetection]:
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = self.pose.process(rgb)
        if not result.pose_landmarks:
            return []
        h, w, _ = frame.shape
        detections = []
        for lm in result.pose_landmarks.landmark:
            detections.append(
                PoseDetection(
                    x=int(lm.x * w),
                    y=int(lm.y * h),
                    confidence=lm.visibility,
                )
            )
        return detections
