from dataclasses import dataclass
import numpy as np


@dataclass(slots=True)
class FramePacket:
    frame_id: int
    timestamp: float
    image: np.ndarray


@dataclass(slots=True)
class PoseDetection:
    track_id: int
    bbox: np.ndarray
    confidence: float
    keypoints: np.ndarray
    mask: np.ndarray | None = None
    mask_confidence: float | None = None
    foot_geometry: dict | None = None
    evaluation: "CadetEvaluation | None" = None
    posture_history: dict[str, list[float]] | None = None


@dataclass(slots=True)
class PipelineResult:
    packet: FramePacket
    detections: list[PoseDetection]
    fps: float
    inference_ms: float
    queue_latency_ms: float
    dropped_frames: int


@dataclass(slots=True)
class RuleResult:
    name: str
    status: str
    score: float | None
    message: str


@dataclass(slots=True)
class CadetEvaluation:
    mode: str
    overall_score: float | None
    status: str
    rules: list[RuleResult]
