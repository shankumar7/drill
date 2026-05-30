import numpy as np
import cv2

from backend.core.types import PoseDetection
from backend.inference.segmentation_estimator import SegmentationDetection


def box_iou(box_a: np.ndarray, box_b: np.ndarray) -> float:
    x1 = max(float(box_a[0]), float(box_b[0]))
    y1 = max(float(box_a[1]), float(box_b[1]))
    x2 = min(float(box_a[2]), float(box_b[2]))
    y2 = min(float(box_a[3]), float(box_b[3]))
    intersection = max(0.0, x2 - x1) * max(0.0, y2 - y1)
    if intersection == 0.0:
        return 0.0
    area_a = max(0.0, float(box_a[2] - box_a[0])) * max(0.0, float(box_a[3] - box_a[1]))
    area_b = max(0.0, float(box_b[2] - box_b[0])) * max(0.0, float(box_b[3] - box_b[1]))
    union = area_a + area_b - intersection
    return intersection / union if union > 0.0 else 0.0


class PoseSegmentationFusion:
    def __init__(self, min_iou_for_match: float) -> None:
        self.min_iou_for_match = min_iou_for_match

    def apply(
        self,
        poses: list[PoseDetection],
        segments: list[SegmentationDetection],
        frame_shape: tuple[int, int] | None = None,
    ) -> list[PoseDetection]:
        used_segments: set[int] = set()
        for pose in poses:
            best_index = None
            best_iou = 0.0
            for index, segment in enumerate(segments):
                if index in used_segments:
                    continue
                overlap = box_iou(pose.bbox, segment.bbox)
                if overlap > best_iou:
                    best_iou = overlap
                    best_index = index
            if best_index is not None and best_iou >= self.min_iou_for_match:
                matched = segments[best_index]
                mask = matched.mask
                if frame_shape is not None and mask.shape[:2] != frame_shape:
                    mask = cv2.resize(mask, (frame_shape[1], frame_shape[0]), interpolation=cv2.INTER_NEAREST)
                pose.mask = mask
                pose.mask_confidence = matched.confidence
                used_segments.add(best_index)
        return poses
