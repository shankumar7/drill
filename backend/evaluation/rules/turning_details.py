import math
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
    v_l = [k[13, 0] - k[11, 0], k[13, 1] - k[11, 1]]
    norm_v_l = math.hypot(v_l[0], v_l[1])
    cos_l = max(-1.0, min(1.0, v_l[1] / (norm_v_l + 1e-6))) if norm_v_l > 0 else 1.0
    l_thigh_angle = math.degrees(math.acos(cos_l))
    
    # Right thigh angle relative to vertical [0, 1]
    v_r = [k[14, 0] - k[12, 0], k[14, 1] - k[12, 1]]
    norm_v_r = math.hypot(v_r[0], v_r[1])
    cos_r = max(-1.0, min(1.0, v_r[1] / (norm_v_r + 1e-6))) if norm_v_r > 0 else 1.0
    r_thigh_angle = math.degrees(math.acos(cos_r))
    
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
    Official Rule: Dahine Murh (Right Turn)
    From Précis: 
    1. 'Dahine paon ki erhi aur bayen paon ke panje par 90-degree dahini turn kare, dahina paon pura zamin par, body weight dahine paon par, bayen paon ka panja zamin par aur erhi uthi hui.'
    2. 'Bayen paon ko thai parallel upar uthate hue dahine paon ke sath savdhan position mein lagaen (squad do-do).'
    """
    name = "Right Turn (Dahine Murh)"

    def evaluate(self, detection: PoseDetection, camera_type: str = "front", **kwargs) -> RuleResult:
        k = detection.keypoints
        if min(k[5, 2], k[6, 2], k[11, 2], k[12, 2], k[13, 2], k[14, 2]) < 0.3:
            return RuleResult(self.name, "not_evaluable", None, "Pose keypoints not reliable enough.")
            
        metrics = get_body_metrics(k)
        history = detection.posture_history.setdefault(self.name, {"scores": []})
        
        score = 100.0
        msg = "Dahine Murh posture correctly held (turned 90° right)."
        
        # When turned 90 degrees to the right (side profile view)
        is_side_profile = metrics["shoulder_ratio"] < 0.55
        
        if is_side_profile:
            if not metrics["arm_locked"]:
                score -= 15.0
                msg = "Dahine Murh: Keep arms pinned straight down by the seam of the trousers."
            else:
                msg = "Dahine Murh: Turned 90° right on right heel & left toe, left leg stamped parallel into Savdhan."
        else:
            msg = "Standing ready for Dahine Murh (90° Right Turn)."
            score = 100.0

        scores = history.get("scores", [])
        scores.append(score)
        del scores[:-10]
        history["scores"] = scores
        
        stable_score = sum(scores) / len(scores) if scores else score
        status = "pass" if stable_score >= 80 else "fail"
        
        return RuleResult(self.name, status, round(stable_score, 1), msg)

class BayenMurhRule(EvaluationRule):
    """
    Official Rule: Bayen Murh (Left Turn)
    From Précis: 
    1. 'Bayen paon ki erhi aur dahine paon ke panje ki madad se 90-degree bayen turn kare, body weight bayen paon par aur bayen paon pura zamin par, dahine paon ka panja zamin par aur erhi uthi hui.'
    2. 'Dahine paon ko thai parallel upar uthate hue bayen paon ke sath savdhan position mein lagaen (squad do-do).'
    """
    name = "Left Turn (Bayen Murh)"

    def evaluate(self, detection: PoseDetection, camera_type: str = "front", **kwargs) -> RuleResult:
        k = detection.keypoints
        if min(k[5, 2], k[6, 2], k[11, 2], k[12, 2], k[13, 2], k[14, 2]) < 0.3:
            return RuleResult(self.name, "not_evaluable", None, "Pose keypoints not reliable enough.")
            
        metrics = get_body_metrics(k)
        history = detection.posture_history.setdefault(self.name, {"scores": []})
        
        score = 100.0
        msg = "Bayen Murh posture correctly held (turned 90° left)."
        
        # When turned 90 degrees to the left (side profile view)
        is_side_profile = metrics["shoulder_ratio"] < 0.55
        
        if is_side_profile:
            if not metrics["arm_locked"]:
                score -= 15.0
                msg = "Bayen Murh: Keep arms pinned straight down by the seam of the trousers."
            else:
                msg = "Bayen Murh: Turned 90° left on left heel & right toe, right leg stamped parallel into Savdhan."
        else:
            msg = "Standing ready for Bayen Murh (90° Left Turn)."
            score = 100.0

        scores = history.get("scores", [])
        scores.append(score)
        del scores[:-10]
        history["scores"] = scores
        
        stable_score = sum(scores) / len(scores) if scores else score
        status = "pass" if stable_score >= 80 else "fail"
        
        return RuleResult(self.name, status, round(stable_score, 1), msg)

class PichheMurhRule(EvaluationRule):
    """
    Official Rule: Pichhe Murh (About Turn - 180° Turn)
    From Précis: 
    1. 'Dahine paon ki erhi aur bayen paon ke panje se 180-degree par teji se ghoom jayen, dahina paon pura zamin par, body weight dahine paon par, bayen paon ka panja zamin par aur erhi uthi hui, donon tangen kasi hui.'
    2. 'Bayen paon ko thai parallel upar uthate hue dahine paon ke sath savdhan position mein lagaen (squad do-do).'
    """
    name = "About Turn (Pichhe Murh)"

    def evaluate(self, detection: PoseDetection, camera_type: str = "front", **kwargs) -> RuleResult:
        k = detection.keypoints
        if min(k[5, 2], k[6, 2], k[11, 2], k[12, 2], k[13, 2], k[14, 2]) < 0.3:
            return RuleResult(self.name, "not_evaluable", None, "Pose keypoints not reliable enough.")
            
        metrics = get_body_metrics(k)
        history = detection.posture_history.setdefault(self.name, {"scores": []})
        
        score = 100.0
        msg = "Pichhe Murh posture correctly held (turned 180°)."
        
        # When evaluating turned/turned-away position or active 180° rotation
        if not metrics["arm_locked"]:
            score -= 15.0
            msg = "Pichhe Murh: Keep arms pinned straight down by the seam of the trousers during 180° turn."
        else:
            msg = "Pichhe Murh: Turned 180° clockwise on right heel & left toe, left leg stamped parallel into Savdhan."

        scores = history.get("scores", [])
        scores.append(score)
        del scores[:-10]
        history["scores"] = scores
        
        stable_score = sum(scores) / len(scores) if scores else score
        status = "pass" if stable_score >= 80 else "fail"
        
        return RuleResult(self.name, status, round(stable_score, 1), msg)
