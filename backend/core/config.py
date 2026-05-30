from pathlib import Path
from typing import Union

import yaml
from pydantic import BaseModel, Field


class RuntimeConfig(BaseModel):
    source: Union[int, str] = 0
    queue_size: int = Field(default=2, ge=1, le=8)
    display: bool = True


class InferenceConfig(BaseModel):
    backend: str = "yolo"
    model_path: str = "yolo11n-pose.pt"
    confidence: float = Field(default=0.4, ge=0.0, le=1.0)
    image_size: int = Field(default=480, ge=128)
    prefer_half_precision: bool = True
    tracking_enabled: bool = True
    tracker_config: str = "bytetrack.yaml"


class SegmentationConfig(BaseModel):
    enabled: bool = True
    model_path: str = "yolo11n-seg.pt"
    confidence: float = Field(default=0.4, ge=0.0, le=1.0)
    image_size: int = Field(default=480, ge=128)
    interval: int = Field(default=4, ge=1)
    min_iou_for_match: float = Field(default=0.1, ge=0.0, le=1.0)


class SmoothingConfig(BaseModel):
    enabled: bool = True
    min_cutoff: float = Field(default=0.5, gt=0.0)
    beta: float = Field(default=0.01, ge=0.0)
    confidence_threshold: float = Field(default=0.25, ge=0.0, le=1.0)


class LoggingConfig(BaseModel):
    level: str = "INFO"


class EvaluationConfig(BaseModel):
    enabled: bool = True
    mode: str = "SAVDHAN"


class VisualizationConfig(BaseModel):
    show_foot_debug: bool = False


class CalibrationConfig(BaseModel):
    enabled: bool = False
    validated: bool = False
    homography_path: str = "calibration/floor_homography.yaml"


class AppConfig(BaseModel):
    runtime: RuntimeConfig = RuntimeConfig()
    inference: InferenceConfig = InferenceConfig()
    segmentation: SegmentationConfig = SegmentationConfig()
    smoothing: SmoothingConfig = SmoothingConfig()
    evaluation: EvaluationConfig = EvaluationConfig()
    visualization: VisualizationConfig = VisualizationConfig()
    calibration: CalibrationConfig = CalibrationConfig()
    logging: LoggingConfig = LoggingConfig()


def load_config(path: str | Path) -> AppConfig:
    with Path(path).open("r", encoding="utf-8") as handle:
        raw = yaml.safe_load(handle) or {}
    return AppConfig.model_validate(raw)
