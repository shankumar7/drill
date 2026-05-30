from pathlib import Path

import cv2
import numpy as np
import yaml


class GroundPlaneMapper:
    def __init__(self, homography: np.ndarray | None = None) -> None:
        self.homography = homography

    @property
    def is_ready(self) -> bool:
        return self.homography is not None

    @classmethod
    def load(cls, path: str | Path) -> "GroundPlaneMapper":
        file_path = Path(path)
        if not file_path.exists():
            return cls()
        with file_path.open("r", encoding="utf-8") as handle:
            data = yaml.safe_load(handle) or {}
        matrix = np.asarray(data["homography"], dtype=float) if "homography" in data else None
        return cls(matrix)

    @staticmethod
    def estimate(image_points: np.ndarray, floor_points: np.ndarray) -> "GroundPlaneMapper":
        homography, _ = cv2.findHomography(image_points.astype(np.float32), floor_points.astype(np.float32))
        if homography is None:
            raise RuntimeError("Unable to estimate floor homography from provided points.")
        return GroundPlaneMapper(homography)

    def save(self, path: str | Path) -> None:
        if self.homography is None:
            raise RuntimeError("Cannot save an empty homography.")
        file_path = Path(path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with file_path.open("w", encoding="utf-8") as handle:
            yaml.safe_dump({"homography": self.homography.tolist()}, handle)

    def transform_points(self, points: np.ndarray) -> np.ndarray:
        if self.homography is None:
            raise RuntimeError("Ground-plane mapper is not calibrated.")
        points = points.astype(np.float32).reshape(-1, 1, 2)
        return cv2.perspectiveTransform(points, self.homography).reshape(-1, 2)
