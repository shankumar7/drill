from backend.core.types import PoseDetection, RuleResult
from backend.evaluation.rules.base import EvaluationRule
import time

CALIBRATION_STATE = {
    "step": 1, # 1: Right Hand, 2: Left Hand, 3: Turn Right
    "front_cam_id": None,
    "side_cam_id": None,
    "back_cam_id": None,
    "locked_track_id": None,
    "completed": False,
    "last_success_time": 0
}

class AutoCalibrationRule(EvaluationRule):
    name = "Auto Calibration"

    def evaluate(self, detection: PoseDetection, camera_type: str = "front", **kwargs) -> RuleResult:
        if CALIBRATION_STATE["completed"]:
            return RuleResult(self.name, "pass", 100, "Calibration complete")

        # Allow 2 seconds between steps so the user doesn't accidentally trigger the next step with an old pose
        if time.time() - CALIBRATION_STATE["last_success_time"] < 2.0:
            return RuleResult(self.name, "partial_pass", 50, "Preparing next step...")

        k = detection.keypoints
        # 5: L Shoulder, 6: R Shoulder, 7: L Elbow, 8: R Elbow, 9: L Wrist, 10: R Wrist
        # YOLO pose keypoints: left/right are from the person's perspective.
        
        msg = f"Step {CALIBRATION_STATE['step']}: "
        
        # We use a step-specific history key to avoid carryover between steps.
        step = CALIBRATION_STATE["step"]
        history_key = f"{self.name}_step_{step}"
        history = detection.posture_history.setdefault(history_key, []) if detection.posture_history is not None else []
        
        is_passing = False
        
        if step == 1:
            msg += "Raise your RIGHT hand"
            # Right wrist (10) should be above right shoulder (6). (y goes down, so y should be smaller)
            if k[10, 2] > 0.4 and k[6, 2] > 0.4:
                if k[10, 1] < k[6, 1] - 30: # significantly above
                    is_passing = True

        elif step == 2:
            msg += "Raise your LEFT hand"
            if k[9, 2] > 0.4 and k[5, 2] > 0.4:
                if k[9, 1] < k[5, 1] - 30:
                    is_passing = True
            
        elif step == 3:
            msg += "Turn to your RIGHT side"
            # When a person turns to their right side, they face the left of the image (from front camera's perspective).
            # So the right shoulder (6) is closer to the camera, and left shoulder (5) is hidden or behind.
            # Also, from the "front" camera, the width between shoulders drops significantly.
            shoulder_dist = abs(k[5, 0] - k[6, 0])
            if shoulder_dist < 40 and k[6, 2] > 0.5: # Shoulders overlap, right shoulder visible
                is_passing = True

        history.append(100 if is_passing else 0)
        del history[:-10]  # Keep last 10 frames (~0.5s at 20fps)
        
        stable_score = sum(history) / len(history) if history else 0
        
        if stable_score >= 80 and len(history) >= 5:
            # Clear this history list on success so it doesn't linger if evaluated again
            history.clear()
            return RuleResult(self.name, "pass", 100, f"Step {step} conditions met!")
        else:
            return RuleResult(self.name, "fail", 0, msg)
