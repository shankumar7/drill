import logging
import time
from queue import Full, Queue
from threading import Event, Thread

import cv2

from backend.core.types import FramePacket


LOGGER = logging.getLogger(__name__)


class CameraReader:
    def __init__(self, source: int | str, output_queue: Queue[FramePacket], raw_frames_dict: dict | None = None) -> None:
        self.source = source
        self.output_queue = output_queue
        self.raw_frames_dict = raw_frames_dict
        self.stop_event = Event()
        self.thread: Thread | None = None
        self.capture: cv2.VideoCapture | None = None
        self.dropped_frames = 0

    def start(self) -> None:
        if isinstance(self.source, int):
            # Prefer DirectShow on Windows for zero-latency camera access
            self.capture = cv2.VideoCapture(self.source, cv2.CAP_DSHOW)
            if not self.capture.isOpened():
                self.capture = cv2.VideoCapture(self.source)
        else:
            self.capture = cv2.VideoCapture(self.source)

        if not self.capture.isOpened():
            raise RuntimeError(f"Unable to open video source: {self.source}")

        # Optimize camera driver buffer size to prevent input lag
        try:
            self.capture.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        except Exception:
            pass

        self.thread = Thread(target=self._loop, name=f"camera-reader-{self.source}", daemon=True)
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

            # Instantly store raw frame for zero-latency preview
            if self.raw_frames_dict is not None:
                self.raw_frames_dict[self.source] = frame

            packet = FramePacket(frame_id=frame_id, timestamp=time.perf_counter(), image=frame)
            frame_id += 1

            # Keep only the newest frame in output queue to avoid queue latency
            try:
                self.output_queue.put_nowait(packet)
            except Full:
                try:
                    self.output_queue.get_nowait()
                except Exception:
                    pass
                try:
                    self.output_queue.put_nowait(packet)
                except Exception:
                    pass
                self.dropped_frames += 1
