import math

import numpy as np

from backend.core.types import PoseDetection


class OneEuroFilter:
    def __init__(self, frequency: float, min_cutoff: float, beta: float, d_cutoff: float = 1.0) -> None:
        self.frequency = frequency
        self.min_cutoff = min_cutoff
        self.beta = beta
        self.d_cutoff = d_cutoff
        self.previous_value: np.ndarray | None = None
        self.previous_derivative: np.ndarray | None = None

    def __call__(self, value: np.ndarray, dt: float | None = None) -> np.ndarray:
        dt = dt or 1.0 / self.frequency
        if self.previous_value is None:
            self.previous_value = value
            self.previous_derivative = np.zeros_like(value)
            return value
        derivative = (value - self.previous_value) / dt
        smoothed_derivative = self._low_pass(
            derivative, self.previous_derivative, self._alpha(dt, self.d_cutoff)
        )
        cutoff = self.min_cutoff + self.beta * np.abs(smoothed_derivative)
        smoothed_value = self._low_pass(value, self.previous_value, self._alpha(dt, cutoff))
        self.previous_value = smoothed_value
        self.previous_derivative = smoothed_derivative
        return smoothed_value

    @staticmethod
    def _low_pass(value: np.ndarray, previous: np.ndarray, alpha: np.ndarray | float) -> np.ndarray:
        return alpha * value + (1.0 - alpha) * previous

    @staticmethod
    def _alpha(dt: float, cutoff: np.ndarray | float) -> np.ndarray | float:
        tau = 1.0 / (2.0 * math.pi * cutoff)
        return 1.0 / (1.0 + tau / dt)


class PoseSmoother:
    def __init__(self, min_cutoff: float, beta: float, confidence_threshold: float) -> None:
        self.min_cutoff = min_cutoff
        self.beta = beta
        self.confidence_threshold = confidence_threshold
        self.filters: dict[int, list[OneEuroFilter]] = {}

    def apply(self, detections: list[PoseDetection], dt: float) -> list[PoseDetection]:
        for detection in detections:
            filters = self.filters.setdefault(
                detection.track_id,
                [OneEuroFilter(30.0, self.min_cutoff, self.beta) for _ in range(len(detection.keypoints))],
            )
            for index, keypoint in enumerate(detection.keypoints):
                if keypoint[2] >= self.confidence_threshold:
                    detection.keypoints[index, :2] = filters[index](keypoint[:2], dt)
        return detections
