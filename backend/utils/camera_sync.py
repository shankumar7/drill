"""Utility to align frames from multiple cameras based on timestamps.
Usage example:
    sync = CameraSyncManager(max_delay_ms=50)
    sync.add_frame(cam_id, frame, timestamp)
    synced = sync.get_synchronized_frames()
"""
import heapq
from collections import defaultdict
from typing import Dict, Any

class CameraSyncManager:
    def __init__(self, max_delay_ms: int = 50):
        self.max_delay = max_delay_ms / 1000.0
        self.buffers: Dict[int, list[tuple[float, Any]]] = defaultdict(list)

    def add_frame(self, cam_id: int, frame: Any, timestamp: float) -> None:
        """Add a frame with its capture timestamp (seconds)."""
        heapq.heappush(self.buffers[cam_id], (timestamp, frame))

    def get_synchronized_frames(self) -> Dict[int, Any]:
        """Return frames whose timestamps are within `max_delay` of each other.
        If synchronization fails, returns an empty dict.
        """
        if not self.buffers:
            return {}
        earliest = max(buf[0][0] for buf in self.buffers.values() if buf)
        latest = min(buf[-1][0] for buf in self.buffers.values() if buf)
        if latest - earliest > self.max_delay:
            return {}
        synced = {}
        for cam_id, buf in self.buffers.items():
            while buf and buf[0][0] < earliest:
                heapq.heappop(buf)
            if buf and abs(buf[0][0] - earliest) <= self.max_delay:
                synced[cam_id] = heapq.heappop(buf)[1]
        return synced
