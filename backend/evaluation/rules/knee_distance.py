from backend.core.types import PoseDetection, RuleResult
from backend.evaluation.geometry import segment_length
from backend.evaluation.rules.base import EvaluationRule

class KneeDistanceRule(EvaluationRule):
    name = "Knee distance"

    def __init__(self, target: str):
        # target can be "close" (savdhan) or "relaxed" (salute)
        self.target = target

    def evaluate(self, detection: PoseDetection) -> RuleResult:
        k = detection.keypoints
        if min(k[13, 2], k[14, 2], k[5, 2], k[6, 2]) < 0.5:
            return RuleResult(self.name, "not_evaluable", None, "Knee or shoulder keypoints are not reliable.")
            
        knee_dist = segment_length(k[13, :2], k[14, :2])
        shoulder_width = segment_length(k[5, :2], k[6, :2])
        
        if shoulder_width < 10:
            return RuleResult(self.name, "not_evaluable", None, "Shoulder width too small for scaling.")
            
        # Normalize distance relative to shoulder width.
        # Original: 20-40 pixels (close). Usually knees touch in Savdhan, so < 0.3 * shoulder width
        norm_dist = knee_dist / shoulder_width
        
        score = 0.0
        if self.target == "close":
            if norm_dist <= 0.3:
                score = 100.0
            elif norm_dist < 0.6:
                score = 100.0 - ((norm_dist - 0.3) * 333.3)
            msg = f"Knees should be close together (norm_dist: {norm_dist:.2f})"
        else:
            # Salute is slightly more relaxed, 20-80 pixels -> norm_dist up to 0.7
            if norm_dist <= 0.7:
                score = 100.0
            elif norm_dist < 1.0:
                score = 100.0 - ((norm_dist - 0.7) * 333.3)
            msg = f"Knees should be relatively close (norm_dist: {norm_dist:.2f})"
            
        smoothed = self.smooth_score(detection, score)
        if isinstance(smoothed, RuleResult):
            return smoothed
            
        status = "pass" if smoothed >= 80 else "fail"
        return RuleResult(self.name, status, round(smoothed, 1), msg)
