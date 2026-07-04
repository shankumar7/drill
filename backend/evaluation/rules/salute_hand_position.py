from backend.core.types import PoseDetection, RuleResult
from backend.evaluation.geometry import segment_length
from backend.evaluation.rules.base import EvaluationRule

class SaluteHandPositionRule(EvaluationRule):
    name = "Saluting Hand Position"

    def evaluate(self, detection: PoseDetection) -> RuleResult:
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
        
        # When saluting, wrist is near the eyebrow.
        # Since spine length is much longer than shoulder width, the normalized distance is smaller.
        # Let's say ideal is < 0.2 of spine length.
        score = 0.0
        if norm_dist <= 0.2:
            score = 100.0
        elif norm_dist < 0.4:
            score = 100.0 - ((norm_dist - 0.2) * 500)
            
        score = max(0.0, score)
        
        smoothed = self.smooth_score(detection, score)
        if isinstance(smoothed, RuleResult):
            return smoothed
            
        status = "pass" if smoothed >= 80 else "fail"
        return RuleResult(self.name, status, round(smoothed, 1), f"Right Wrist-Eye Distance: {norm_dist:.2f} (Ideal: < 0.2)")
