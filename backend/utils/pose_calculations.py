"""Utility functions for height and joint‑angle calculations.
All functions accept a NumPy array of MediaPipe landmarks (N, 3).
"""
import numpy as np

def compute_height(keypoints: np.ndarray, scale_factor: float) -> float:
    """Height in inches derived from pixel distance between head (0) and foot (32)."""
    head_y = keypoints[0, 1]
    foot_y = keypoints[32, 1]
    return abs(foot_y - head_y) * scale_factor

def _angle(a: np.ndarray, b: np.ndarray, c: np.ndarray) -> float:
    ba = a - b
    bc = c - b
    cos_val = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc) + 1e-6)
    return np.degrees(np.arccos(np.clip(cos_val, -1, 1)))

def knee_angle(keypoints: np.ndarray) -> float:
    # hip (23), knee (25), ankle (27)
    return _angle(keypoints[23], keypoints[25], keypoints[27])

def hip_angle(keypoints: np.ndarray) -> float:
    # shoulder (12), hip (23), knee (25)
    return _angle(keypoints[12], keypoints[23], keypoints[25])

def shoulder_angle(keypoints: np.ndarray) -> float:
    # elbow (14), shoulder (12), hip (23)
    return _angle(keypoints[14], keypoints[12], keypoints[23])
