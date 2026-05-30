import numpy as np


def angle_degrees(a: np.ndarray, b: np.ndarray, c: np.ndarray) -> float:
    ba = a - b
    bc = c - b
    denominator = (np.linalg.norm(ba) * np.linalg.norm(bc)) + 1e-6
    cosine = np.clip(np.dot(ba, bc) / denominator, -1.0, 1.0)
    return float(np.degrees(np.arccos(cosine)))


def segment_length(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.linalg.norm(a - b))


def mid_point(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    return (a + b) / 2.0
