import numpy as np
from backend.core.types import PoseDetection, RuleResult
from backend.evaluation.geometry import segment_length, mid_point
from backend.evaluation.rules.base import EvaluationRule
from backend.evaluation.rules.turning_details import get_body_metrics

class KhuliLineChalRule(EvaluationRule):
    """
    Khuli Line Chal (Open Line March / Move):
    Cadet moves 1.5 steps forward (total 45 inches).
    Step 1: Left foot moves 30 inches forward.
    Step 2: Right foot moves 15 inches forward, lifting the right thigh parallel to the ground, and stamps next to left.
    """
    name = "Open Line Chal (Khuli Line)"

    def evaluate(self, detection: PoseDetection, camera_type: str = "front", **kwargs) -> RuleResult:
        if camera_type != "side":
            return RuleResult(self.name, "not_evaluable", None, "Requires side camera view to measure step distances accurately.")
        k = detection.keypoints
        if min(k[5, 2], k[6, 2], k[11, 2], k[12, 2], k[13, 2], k[14, 2], k[15, 2], k[16, 2]) < 0.3:
            return RuleResult(self.name, "not_evaluable", None, "Pose keypoints not reliable enough.")
            
        metrics = get_body_metrics(k)
        
        # Normalized distance between ankles
        ankle_dist = segment_length(k[15, :2], k[16, :2])
        norm_ankle_dist = ankle_dist / (metrics["spine_length"] + 1e-6)
        
        history = detection.posture_history.setdefault(self.name, {"state": 0, "max_step_dist": 0.0, "max_thigh_lift": 0.0, "scores": []})
        state = history.get("state", 0)
        
        score = 100.0
        msg = "Cadet standing in Savdhan, waiting to start Open Line."
        
        if state == 0:
            # Stand in Savdhan, waiting for a wide forward step
            if norm_ankle_dist > 0.45:
                state = 1
                history["state"] = 1
                history["max_step_dist"] = norm_ankle_dist
                history["max_thigh_lift"] = 0.0
                msg = "First step detected (left foot moving forward)."
            else:
                msg = "Waiting for first step."
                
        if state == 1:
            history["max_step_dist"] = max(history["max_step_dist"], norm_ankle_dist)
            # Trace the thigh lift of the right leg on the second step
            history["max_thigh_lift"] = max(history["max_thigh_lift"], metrics["r_thigh_angle"])
            
            # Verify if arms remain locked at sides
            if not metrics["arm_locked"]:
                score -= 15.0
                msg = "Arms not locked at sides during step!"
            else:
                msg = f"Step 1 active. Right thigh lift: {metrics['r_thigh_angle']:.1f}°"
                
            # If the ankles are close again, we assume the cadet completed the close
            if norm_ankle_dist < 0.25:
                state = 2
                history["state"] = 2
                
        if state == 2:
            max_step = history["max_step_dist"]
            max_lift = history["max_thigh_lift"]
            
            # Check step distance (must be wide, representing 30 inches)
            if max_step < 0.5:
                score -= 25.0
                msg = f"First step length was too short. Stride distance ratio: {max_step:.2f}"
            # Check thigh lift of closing leg
            elif max_lift < 60.0:
                score -= 35.0
                msg = f"Right thigh lift during close insufficient ({max_lift:.1f}°). Target is parallel to ground (>=60°)."
            else:
                msg = "Open Line Chal completed successfully!"
                
            if norm_ankle_dist < 0.2:
                history["state"] = 0

        history["scores"].append(score)
        del history["scores"][:-10]
        stable_score = sum(history["scores"]) / len(history["scores"])
        status = "pass" if stable_score >= 90 else "fail"
        
        return RuleResult(self.name, status, round(stable_score, 1), msg)

class NikatLineChalRule(EvaluationRule):
    """
    Nikat Line Chal (Close Line March / Move):
    Cadet moves 1.5 steps backward (total 45 inches).
    Step 1: Left foot moves 30 inches backward.
    Step 2: Right foot moves 15 inches backward, lifting the right thigh parallel to ground, and stamps next to left.
    """
    name = "Close Line Chal (Nikat Line)"

    def evaluate(self, detection: PoseDetection, camera_type: str = "front", **kwargs) -> RuleResult:
        if camera_type != "side":
            return RuleResult(self.name, "not_evaluable", None, "Requires side camera view to measure step distances accurately.")
        k = detection.keypoints
        if min(k[5, 2], k[6, 2], k[11, 2], k[12, 2], k[13, 2], k[14, 2], k[15, 2], k[16, 2]) < 0.3:
            return RuleResult(self.name, "not_evaluable", None, "Pose keypoints not reliable enough.")
            
        metrics = get_body_metrics(k)
        
        # Normalized distance between ankles
        ankle_dist = segment_length(k[15, :2], k[16, :2])
        norm_ankle_dist = ankle_dist / (metrics["spine_length"] + 1e-6)
        
        history = detection.posture_history.setdefault(self.name, {"state": 0, "max_step_dist": 0.0, "max_thigh_lift": 0.0, "scores": []})
        state = history.get("state", 0)
        
        score = 100.0
        msg = "Cadet standing in Savdhan, waiting to start Close Line."
        
        if state == 0:
            if norm_ankle_dist > 0.45:
                state = 1
                history["state"] = 1
                history["max_step_dist"] = norm_ankle_dist
                history["max_thigh_lift"] = 0.0
                msg = "First backward step detected (left foot moving)."
            else:
                msg = "Waiting for first backward step."
                
        if state == 1:
            history["max_step_dist"] = max(history["max_step_dist"], norm_ankle_dist)
            history["max_thigh_lift"] = max(history["max_thigh_lift"], metrics["r_thigh_angle"])
            
            if not metrics["arm_locked"]:
                score -= 15.0
                msg = "Arms not locked at sides during step!"
            else:
                msg = f"Step 1 active. Right thigh lift: {metrics['r_thigh_angle']:.1f}°"
                
            if norm_ankle_dist < 0.25:
                state = 2
                history["state"] = 2
                
        if state == 2:
            max_step = history["max_step_dist"]
            max_lift = history["max_thigh_lift"]
            
            if max_step < 0.5:
                score -= 25.0
                msg = f"First step length was too short. Stride distance ratio: {max_step:.2f}"
            elif max_lift < 60.0:
                score -= 35.0
                msg = f"Right thigh lift during close insufficient ({max_lift:.1f}°). Target is parallel to ground (>=60°)."
            else:
                msg = "Close Line Chal completed successfully!"
                
            if norm_ankle_dist < 0.2:
                history["state"] = 0

        history["scores"].append(score)
        del history["scores"][:-10]
        stable_score = sum(history["scores"]) / len(history["scores"])
        status = "pass" if stable_score >= 90 else "fail"
        
        return RuleResult(self.name, status, round(stable_score, 1), msg)
