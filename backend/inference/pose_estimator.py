from abc import ABC, abstractmethod

import numpy as np
import torch
from ultralytics import YOLO

from backend.core.types import PoseDetection


class PoseEstimator(ABC):
    @abstractmethod
    def infer(self, frame: np.ndarray) -> list[PoseDetection]:
        raise NotImplementedError


class YoloPoseEstimator(PoseEstimator):
    def __init__(
        self,
        model_path: str,
        confidence: float,
        image_size: int,
        prefer_half_precision: bool,
        tracking_enabled: bool = True,
        tracker_config: str = "bytetrack.yaml",
    ) -> None:
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.use_half = prefer_half_precision and self.device == "cuda"
        self.confidence = confidence
        self.image_size = image_size
        self.tracking_enabled = tracking_enabled
        self.tracker_config = tracker_config
        self.model = YOLO(model_path).to(self.device)

    def infer(self, frame: np.ndarray) -> list[PoseDetection]:
        common_args = dict(
            source=frame,
            conf=self.confidence,
            imgsz=self.image_size,
            device=self.device,
            verbose=False,
        )
        if self.use_half:
            common_args["half"] = True
            
        results = (
            self.model.track(**common_args, persist=True, tracker=self.tracker_config)
            if self.tracking_enabled
            else self.model.predict(**common_args)
        )
        detections: list[PoseDetection] = []
        for result in results:
            if result.keypoints is None:
                continue
            keypoints = result.keypoints.data.detach().cpu().numpy()
            boxes = result.boxes.data.detach().cpu().numpy()
            ids = (
                result.boxes.id.detach().cpu().numpy()
                if result.boxes.id is not None
                else np.arange(len(boxes))
            )
            confs = result.boxes.conf.detach().cpu().numpy()
            for index, points in enumerate(keypoints):
                detections.append(
                    PoseDetection(
                        track_id=int(ids[index]),
                        bbox=boxes[index, :4],
                        confidence=float(confs[index]),
                        keypoints=points,
                    )
                )
        return detections
