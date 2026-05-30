import logging
import time
from queue import Full, Queue
from threading import Event, Thread

import cv2

from backend.core.types import FramePacket


LOGGER = logging.getLogger(__name__)


class CameraReader:
    def __init__(self, source: int | str, output_queue: Queue[FramePacket]) -> None:
        self.source = source
        self.output_queue = output_queue
        self.stop_event = Event()
        self.thread: Thread | None = None
        self.capture: cv2.VideoCapture | None = None
        self.dropped_frames = 0

    def start(self) -> None:
        self.capture = cv2.VideoCapture(self.source)
        if not self.capture.isOpened():
            raise RuntimeError(f"Unable to open video source: {self.source}")
        self.thread = Thread(target=self._loop, name="camera-reader", daemon=True)
        self.thread.start()

    def stop(self) -> None:
        self.stop_event.set()
        if self.thread is not None:
            self.thread.join(timeout=1.0)
        if self.capture is not None:
            self.capture.release()

    def _loop(self) -> None:
        frame_id = 0
        assert self.capture is not None
        while not self.stop_event.is_set():
            ok, frame = self.capture.read()
            if not ok:
                LOGGER.info("Video source ended or frame read failed")
                self.stop_event.set()
                break
            packet = FramePacket(frame_id=frame_id, timestamp=time.perf_counter(), image=frame)
            frame_id += 1
            try:
                self.output_queue.put_nowait(packet)
            except Full:
                self.dropped_frames += 1
