from backend.core.types import PoseDetection, RuleResult
from backend.evaluation.geometry import segment_length
from backend.evaluation.rules.base import EvaluationRule

class SaluteHandPositionRule(EvaluationRule):
    name = "Saluting Hand Position"

    def evaluate(self, detection: PoseDetection, camera_type: str = "front", **kwargs) -> RuleResult:
        if camera_type == "back":
            return RuleResult(self.name, "not_evaluable", None, "Back camera cannot evaluate salute hand position.")
        k = detection.keypoints
        # Strict NCC rule: Right hand salutes to the right eye/forehead
        # Right: Wrist (10), Eye (2)
        
        right_ok = min(k[10, 2], k[2, 2]) >= 0.25
        
        if not right_ok:
            return RuleResult(self.name, "not_evaluable", None, "Right hand or right eye keypoints not reliable.")
        
        geometry = detection.foot_geometry or {}
        spine_length = geometry.get("spine_length", 100)
        
        if spine_length < 20 or spine_length == 100:
            return RuleResult(self.name, "not_evaluable", None, "Spine length too small or unreliable for scaling.")
        
        r_wrist = k[10, :2]
        r_eye = k[2, :2]
        
        # Distance from right wrist to right eye, normalized by spine length
        norm_dist = segment_length(r_wrist, r_eye) / spine_length
        
        nose_y = k[0, 1]
        # Strict vertical check: Hand MUST be at the forehead level.
        # If the wrist is significantly below the nose, they are holding it in front of their face/chest.
        if r_wrist[1] > nose_y:
            drop = (r_wrist[1] - nose_y) / spine_length
            if drop > 0.05:
                return RuleResult(self.name, "fail", 30.0, "Hand must be at forehead level, not in front of face.")
                
        # When saluting, fingertips touch the eyebrow. The wrist is a full hand-length away.
        score = 0.0
        if norm_dist <= 0.517:
            score = 100.0
        elif norm_dist < 0.717:
            score = 100.0 - ((norm_dist - 0.517) * 500)
            
        score = max(0.0, score)
        
        smoothed = self.smooth_score(detection, score)
        if isinstance(smoothed, RuleResult):
            return smoothed
            
        status = "pass" if smoothed >= 90 else "fail"
        return RuleResult(self.name, status, round(smoothed, 1), f"Right Wrist-Eye Distance: {norm_dist:.2f} (Ideal: <= 0.55)")
