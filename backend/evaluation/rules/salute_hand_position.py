from backend.core.types import PoseDetection, RuleResult
from backend.evaluation.geometry import segment_length
from backend.evaluation.rules.base import EvaluationRule

class SaluteHandPositionRule(EvaluationRule):
    name = "Saluting Hand Position"

    def evaluate(self, detection: PoseDetection) -> RuleResult:
        k = detection.keypoints
        # Right Wrist (10), Right Eye (2), Shoulders (5, 6)
        if min(k[10, 2], k[2, 2], k[5, 2], k[6, 2]) < 0.5:
            return RuleResult(self.name, "not_evaluable", None, "Hand or eye keypoints not reliable.")
            
        r_wrist = k[10, :2]
        r_eye = k[2, :2]
        
        wrist_eye_dist = segment_length(r_wrist, r_eye)
        shoulder_width = segment_length(k[5, :2], k[6, :2])
        
        if shoulder_width < 10:
            return RuleResult(self.name, "not_evaluable", None, "Shoulder width too small")
            
        # Normalize distance relative to shoulder width.
        # When saluting, right wrist is near the right eyebrow, so distance should be very small.
        # Say, < 0.3 * shoulder_width
        norm_dist = wrist_eye_dist / shoulder_width
        
        score = 0.0
        if norm_dist <= 0.35:
            score = 100.0
        elif norm_dist < 0.6:
            score = 100.0 - ((norm_dist - 0.35) * 400)
            
        score = max(0.0, score)
        
        smoothed = self.smooth_score(detection, score)
        if isinstance(smoothed, RuleResult):
            return smoothed
            
        status = "pass" if smoothed >= 80 else "fail"
        return RuleResult(self.name, status, round(smoothed, 1), f"Wrist-Eye Distance: {norm_dist:.2f} (Ideal: < 0.35)")
