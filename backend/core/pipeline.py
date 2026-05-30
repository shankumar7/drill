import logging
import time
from queue import Empty, Queue
from threading import Event, Thread

import cv2

from backend.core.config import AppConfig
from backend.core.types import PipelineResult
from backend.inference.pose_estimator import YoloPoseEstimator
from backend.inference.segmentation_estimator import YoloSegmentationEstimator
from backend.evaluation.evaluator import StaticPostureEvaluator
from backend.engine.foot_analyzer import FootGeometryAnalyzer
from backend.calibration.ground_plane import GroundPlaneMapper
from backend.io.camera import CameraReader
from backend.monitoring.performance import PerformanceMonitor
from backend.processing.smoothing import PoseSmoother
from backend.processing.fusion import PoseSegmentationFusion
from backend.visualization.debug_view import render_debug_view


LOGGER = logging.getLogger(__name__)


class Phase1Pipeline:
    def __init__(self, config: AppConfig) -> None:
        self.config = config
        self.frame_queue = Queue(maxsize=config.runtime.queue_size)
        self.result_queue: Queue[PipelineResult] = Queue(maxsize=config.runtime.queue_size)
        self.stop_event = Event()
        self.camera = CameraReader(config.runtime.source, self.frame_queue)
        self.estimator = YoloPoseEstimator(
            model_path=config.inference.model_path,
            confidence=config.inference.confidence,
            image_size=config.inference.image_size,
            prefer_half_precision=config.inference.prefer_half_precision,
            tracking_enabled=config.inference.tracking_enabled,
            tracker_config=config.inference.tracker_config,
        )
        self.segmentation_estimator = (
            YoloSegmentationEstimator(
                model_path=config.segmentation.model_path,
                confidence=config.segmentation.confidence,
                image_size=config.segmentation.image_size,
                prefer_half_precision=config.inference.prefer_half_precision,
            )
            if config.segmentation.enabled
            else None
        )
        self.fusion = PoseSegmentationFusion(config.segmentation.min_iou_for_match)
        self.last_segments = []
        self.evaluator = StaticPostureEvaluator(config.evaluation.mode) if config.evaluation.enabled else None
        self.foot_geometry = FootGeometryAnalyzer()
        self.ground_mapper = (
            GroundPlaneMapper.load(config.calibration.homography_path)
            if config.calibration.enabled and config.calibration.validated
            else GroundPlaneMapper()
        )
        self.smoother = PoseSmoother(
            min_cutoff=config.smoothing.min_cutoff,
            beta=config.smoothing.beta,
            confidence_threshold=config.smoothing.confidence_threshold,
        )
        self.monitor = PerformanceMonitor()
        self.worker: Thread | None = None

    def start(self) -> None:
        self.camera.start()
        self.worker = Thread(target=self._process_loop, name="pose-worker", daemon=True)
        self.worker.start()

    def stop(self) -> None:
        self.stop_event.set()
        self.camera.stop()
        if self.worker is not None:
            self.worker.join(timeout=1.0)
        cv2.destroyAllWindows()

    def run_forever(self) -> None:
        self.start()
        try:
            while not self.stop_event.is_set() and not self.camera.stop_event.is_set():
                try:
                    result = self.result_queue.get(timeout=0.1)
                except Empty:
                    continue
                if self.config.runtime.display:
                    cv2.imshow(
                        "Military Drill Intelligence - Phase 3",
                        render_debug_view(result, show_foot_debug=self.config.visualization.show_foot_debug),
                    )
                    if cv2.waitKey(1) & 0xFF == ord("q"):
                        break
        finally:
            self.stop()

    def _process_loop(self) -> None:
        previous_timestamp: float | None = None
        while not self.stop_event.is_set():
            try:
                packet = self.frame_queue.get(timeout=0.1)
            except Empty:
                continue
            started = time.perf_counter()
            detections = self.estimator.infer(packet.image)
            if self.segmentation_estimator is not None:
                if packet.frame_id % self.config.segmentation.interval == 0 or not self.last_segments:
                    self.last_segments = self.segmentation_estimator.infer(packet.image)
                detections = self.fusion.apply(detections, self.last_segments, frame_shape=packet.image.shape[:2])
            dt = 1.0 / 30.0 if previous_timestamp is None else max(packet.timestamp - previous_timestamp, 1e-3)
            previous_timestamp = packet.timestamp
            if self.config.smoothing.enabled:
                detections = self.smoother.apply(detections, dt)
            if self.evaluator is not None:
                for detection in detections:
                    detection.foot_geometry = self.foot_geometry.analyze_geometry(
                        packet.image,
                        detection.keypoints,
                        ground_mapper=self.ground_mapper,
                    )
                    detection.evaluation = self.evaluator.evaluate(detection)
            completed = time.perf_counter()
            result = PipelineResult(
                packet=packet,
                detections=detections,
                fps=self.monitor.tick(),
                inference_ms=(completed - started) * 1000.0,
                queue_latency_ms=(started - packet.timestamp) * 1000.0,
                dropped_frames=self.camera.dropped_frames,
            )
            if self.result_queue.full():
                try:
                    self.result_queue.get_nowait()
                except Empty:
                    pass
            self.result_queue.put_nowait(result)
