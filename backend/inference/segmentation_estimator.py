from dataclasses import dataclass

import numpy as np
import torch
from ultralytics import YOLO


@dataclass(slots=True)
class SegmentationDetection:
    bbox: np.ndarray
    confidence: float
    mask: np.ndarray


class YoloSegmentationEstimator:
    def __init__(
        self,
        model_path: str,
        confidence: float,
        image_size: int,
        prefer_half_precision: bool,
    ) -> None:
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.use_half = prefer_half_precision and self.device == "cuda"
        self.confidence = confidence
        self.image_size = image_size
        self.model = YOLO(model_path).to(self.device)

    def infer(self, frame: np.ndarray) -> list[SegmentationDetection]:
        common_args = dict(
            source=frame,
            conf=self.confidence,
            classes=[0],
            imgsz=self.image_size,
            device=self.device,
            verbose=False,
        )
        if self.use_half:
            common_args["half"] = True
            
        results = self.model.predict(**common_args)
        detections: list[SegmentationDetection] = []
        for result in results:
            if result.masks is None:
                continue
            boxes = result.boxes.data.detach().cpu().numpy()
            masks = result.masks.data.detach().cpu().numpy()
            for index, mask in enumerate(masks):
                detections.append(
                    SegmentationDetection(
                        bbox=boxes[index, :4],
                        confidence=float(boxes[index, 4]),
                        mask=mask,
                    )
                )
        return detections
