import numpy as np
from backend.core.types import PoseDetection

def angular_velocity(detection: PoseDetection, axis: str = "y") -> float | None:
    """
    Approximate angular velocity (deg/s) around the given axis using the last two
    pose entries stored in ``detection.posture_history``.
    Returns ``None`` when there is not enough history.
    """
    if not detection.posture_history:
        return None
        
    history = detection.posture_history.get("angular_velocity", [])
    if len(history) < 2:
        return None

    prev, cur = history[-2], history[-1]

    prev_yaw = prev.get("yaw")
    cur_yaw = cur.get("yaw")
    if prev_yaw is None or cur_yaw is None:
        return None

    dt = cur.get("timestamp", 0) - prev.get("timestamp", 0)
    if dt <= 0:
        return None

    return (cur_yaw - prev_yaw) / dt
