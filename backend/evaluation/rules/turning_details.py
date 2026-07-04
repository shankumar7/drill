import numpy as np
from backend.core.types import PoseDetection, RuleResult
from backend.evaluation.geometry import segment_length, mid_point
from backend.evaluation.rules.base import EvaluationRule

def get_body_metrics(k):
    # k is keypoints of shape (17, 3) or (17, 2)
    shoulder_mid = mid_point(k[5, :2], k[6, :2])
    hip_mid = mid_point(k[11, :2], k[12, :2])
    spine_length = segment_length(shoulder_mid, hip_mid)
    shoulder_width = segment_length(k[5, :2], k[6, :2])
    ratio = shoulder_width / (spine_length + 1e-6)
    
    # Left thigh angle relative to vertical [0, 1]
    v_l = k[13, :2] - k[11, :2]
    norm_v_l = np.linalg.norm(v_l)
    cos_l = v_l[1] / (norm_v_l + 1e-6) if norm_v_l > 0 else 1.0
    l_thigh_angle = np.degrees(np.arccos(np.clip(cos_l, -1.0, 1.0)))
    
    # Right thigh angle relative to vertical [0, 1]
    v_r = k[14, :2] - k[12, :2]
    norm_v_r = np.linalg.norm(v_r)
    cos_r = v_r[1] / (norm_v_r + 1e-6) if norm_v_r > 0 else 1.0
    r_thigh_angle = np.degrees(np.arccos(np.clip(cos_r, -1.0, 1.0)))
    
    # Normalized wrist-to-hip distances to check if arms remain locked
    l_wrist_hip = segment_length(k[9, :2], k[11, :2])
    r_wrist_hip = segment_length(k[10, :2], k[12, :2])
    
    # Use spine_length (rotation-invariant) instead of shoulder_width
    norm_l = l_wrist_hip / (spine_length + 1e-6)
    norm_r = r_wrist_hip / (spine_length + 1e-6)
    
    # Adjusted threshold for spine_length. Spine is usually longer than shoulders,
    # so the normalized distance will be smaller. Using 0.5 instead of 0.65.
    arm_locked = (norm_l < 0.5) and (norm_r < 0.5)
    
    return {
        "shoulder_ratio": ratio,
        "shoulder_width": shoulder_width,
        "spine_length": spine_length,
        "l_thigh_angle": l_thigh_angle,
        "r_thigh_angle": r_thigh_angle,
        "arm_locked": arm_locked,
        "norm_l": norm_l,
        "norm_r": norm_r
    }

class DahineMurhRule(EvaluationRule):
    """
    Dahine Murh (Right Turn): 90-degree turn to the right.
    Pivots on right heel, lifts left leg (thigh parallel to ground) and stamps left foot.
    """
    name = "Right Turn (Dahine Murh)"

    def evaluate(self, detection: PoseDetection) -> RuleResult:
        k = detection.keypoints
        # Check keypoint reliability
        if min(k[5, 2], k[6, 2], k[11, 2], k[12, 2], k[13, 2], k[14, 2]) < 0.3:
            return RuleResult(self.name, "not_evaluable", None, "Pose keypoints not reliable enough.")
            
        metrics = get_body_metrics(k)
        
        # Initialize state-machine history
        history = detection.posture_history.setdefault(self.name, {"state": 0, "max_thigh_lift": 0.0, "scores": []})
        state = history.get("state", 0)
        
        score = 100.0
        msg = "Cadet is standing in Savdhan posture."
        
        if state == 0:
            # Stand in Savdhan, waiting for rotation (profile view)
            if metrics["shoulder_ratio"] < 0.45:
                # Pivot detected! Move to Pivot/Lift state
                state = 1
                history["state"] = 1
                history["max_thigh_lift"] = 0.0
                msg = "Pivot rotation detected; tracing leg lift phase."
            else:
                msg = "Standing in Savdhan, waiting to pivot."
                
        if state == 1:
            # Pivot phase: check if left leg lift is occurring
            history["max_thigh_lift"] = max(history["max_thigh_lift"], metrics["l_thigh_angle"])
            
            # Verify if arms are kept locked
            if not metrics["arm_locked"]:
                score -= 15.0
                msg = "Arms not locked at sides during pivot!"
            else:
                msg = f"Rotating right. Left thigh angle: {metrics['l_thigh_angle']:.1f}°"
                
            # If the shoulder width ratio returns to facing profile/back or close, check close
            if metrics["shoulder_ratio"] > 0.6:
                # Cadet finished/closed the turn
                state = 2
                history["state"] = 2
                
        if state == 2:
            # Completed: Evaluate overall performance
            max_lift = history["max_thigh_lift"]
            if max_lift < 60.0:
                score -= 40.0
                msg = f"Left thigh lift insufficient ({max_lift:.1f}°). Target is parallel to ground (>=60°)."
            else:
                msg = f"Turn completed successfully! Max left thigh angle was {max_lift:.1f}°."
                
            # Reset state for subsequent turns
            if metrics["shoulder_ratio"] > 0.65:
                history["state"] = 0

        # Smooth the score
        history["scores"].append(score)
        del history["scores"][:-10]
        stable_score = sum(history["scores"]) / len(history["scores"])
        status = "pass" if stable_score >= 80 else "fail"
        
        return RuleResult(self.name, status, round(stable_score, 1), msg)

class BayenMurhRule(EvaluationRule):
    """
    Bayen Murh (Left Turn): 90-degree turn to the left.
    Pivots on left heel, lifts right leg (thigh parallel to ground) and stamps right foot.
    """
    name = "Left Turn (Bayen Murh)"

    def evaluate(self, detection: PoseDetection) -> RuleResult:
        k = detection.keypoints
        if min(k[5, 2], k[6, 2], k[11, 2], k[12, 2], k[13, 2], k[14, 2]) < 0.3:
            return RuleResult(self.name, "not_evaluable", None, "Pose keypoints not reliable enough.")
            
        metrics = get_body_metrics(k)
        history = detection.posture_history.setdefault(self.name, {"state": 0, "max_thigh_lift": 0.0, "scores": []})
        state = history.get("state", 0)
        
        score = 100.0
        msg = "Cadet is standing in Savdhan posture."
        
        if state == 0:
            if metrics["shoulder_ratio"] < 0.45:
                state = 1
                history["state"] = 1
                history["max_thigh_lift"] = 0.0
                msg = "Pivot rotation detected; tracing leg lift phase."
            else:
                msg = "Standing in Savdhan, waiting to pivot."
                
        if state == 1:
            history["max_thigh_lift"] = max(history["max_thigh_lift"], metrics["r_thigh_angle"])
            if not metrics["arm_locked"]:
                score -= 15.0
                msg = "Arms not locked at sides during pivot!"
            else:
                msg = f"Rotating left. Right thigh angle: {metrics['r_thigh_angle']:.1f}°"
                
            if metrics["shoulder_ratio"] > 0.6:
                state = 2
                history["state"] = 2
                
        if state == 2:
            max_lift = history["max_thigh_lift"]
            if max_lift < 60.0:
                score -= 40.0
                msg = f"Right thigh lift insufficient ({max_lift:.1f}°). Target is parallel to ground (>=60°)."
            else:
                msg = f"Turn completed successfully! Max right thigh angle was {max_lift:.1f}°."
                
            if metrics["shoulder_ratio"] > 0.65:
                history["state"] = 0

        history["scores"].append(score)
        del history["scores"][:-10]
        stable_score = sum(history["scores"]) / len(history["scores"])
        status = "pass" if stable_score >= 80 else "fail"
        
        return RuleResult(self.name, status, round(stable_score, 1), msg)

class PichheMurhRule(EvaluationRule):
    """
    Pichhe Murh (About Turn): 180-degree turn to the right (clockwise).
    Pivots on right heel, lifts left leg (thigh parallel to ground) and stamps left foot.
    """
    name = "About Turn (Pichhe Murh)"

    def evaluate(self, detection: PoseDetection) -> RuleResult:
        k = detection.keypoints
        if min(k[5, 2], k[6, 2], k[11, 2], k[12, 2], k[13, 2], k[14, 2]) < 0.3:
            return RuleResult(self.name, "not_evaluable", None, "Pose keypoints not reliable enough.")
            
        metrics = get_body_metrics(k)
        history = detection.posture_history.setdefault(self.name, {"state": 0, "max_thigh_lift": 0.0, "scores": []})
        state = history.get("state", 0)
        
        score = 100.0
        msg = "Cadet is standing in Savdhan posture."
        
        if state == 0:
            if metrics["shoulder_ratio"] < 0.4:
                state = 1
                history["state"] = 1
                history["max_thigh_lift"] = 0.0
                msg = "Pivot rotation detected; tracing leg lift phase."
            else:
                msg = "Standing in Savdhan, waiting to pivot."
                
        if state == 1:
            history["max_thigh_lift"] = max(history["max_thigh_lift"], metrics["l_thigh_angle"])
            if not metrics["arm_locked"]:
                score -= 15.0
                msg = "Arms not locked at sides during pivot!"
            else:
                msg = f"Rotating 180°. Left thigh angle: {metrics['l_thigh_angle']:.1f}°"
                
            # For a 180 turn, the ratio becomes wide again once they face the back
            if metrics["shoulder_ratio"] > 0.6:
                state = 2
                history["state"] = 2
                
        if state == 2:
            max_lift = history["max_thigh_lift"]
            if max_lift < 60.0:
                score -= 40.0
                msg = f"Left thigh lift insufficient ({max_lift:.1f}°). Target is parallel to ground (>=60°)."
            else:
                msg = f"About turn completed successfully! Max left thigh angle was {max_lift:.1f}°."
                
            if metrics["shoulder_ratio"] > 0.65:
                history["state"] = 0

        history["scores"].append(score)
        del history["scores"][:-10]
        stable_score = sum(history["scores"]) / len(history["scores"])
        status = "pass" if stable_score >= 80 else "fail"
        
        return RuleResult(self.name, status, round(stable_score, 1), msg)
