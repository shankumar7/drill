from backend.core.types import PoseDetection, RuleResult
from backend.evaluation.geometry import segment_length
from backend.evaluation.rules.base import EvaluationRule

class KneeDistanceRule(EvaluationRule):
    """Official Rule: 'donon ghutne kase hue' (both knees locked tight)
    
    In Savdhan and Vishram, knees should be tightly locked together.
    During salute, knees should be together with legs straight.
    """
    name = "Knee distance"

    def __init__(self, target: str):
        # target can be "close" (savdhan/vishram) or "relaxed" (salute)
        self.target = target

    def evaluate(self, detection: PoseDetection, camera_type: str = "front", **kwargs) -> RuleResult:
        if camera_type == "side":
            return RuleResult(self.name, "not_evaluable", None, "Requires front or back camera view.")
        k = detection.keypoints
        # Lower confidence threshold from 0.5 to 0.3
        if min(k[13, 2], k[14, 2], k[5, 2], k[6, 2]) < 0.3:
            return RuleResult(self.name, "not_evaluable", None, "Knee or shoulder keypoints are not reliable.")
            
        knee_dist = segment_length(k[13, :2], k[14, :2])
        geometry = detection.foot_geometry or {}
        spine_length = geometry.get("spine_length", 100)
        
        if spine_length < 20 or spine_length == 100:
            return RuleResult(self.name, "not_evaluable", None, "Spine length too small or unreliable for scaling.")
            
        # Normalize knee distance relative to spine length.
        norm_dist = knee_dist / spine_length
        
        score = 0.0
        if self.target == "close":
            # Official: 'donon ghutne kase hue' - both knees locked tight
            # Since spine length is larger than shoulder width, we tighten the thresholds (~0.7 instead of 0.9)
            if norm_dist <= 0.7:
                score = 100.0
            elif norm_dist < 1.0:
                score = max(0.0, 100.0 - ((norm_dist - 0.7) * 333.0))
            msg = f"Knees should be locked tight (donon ghutne kase hue). Distance: {norm_dist:.2f}"
        else:
            # Salute position - still requires knees to be close per official rules
            if norm_dist <= 0.8:
                score = 100.0
            elif norm_dist < 1.1:
                score = max(0.0, 100.0 - ((norm_dist - 0.8) * 333.0))
            msg = f"Knees should be together during salute. Distance: {norm_dist:.2f}"
            
        smoothed = self.smooth_score(detection, score)
        if isinstance(smoothed, RuleResult):
            return smoothed
            
        status = "pass" if smoothed >= 90 else "fail"
        return RuleResult(self.name, status, round(smoothed, 1), msg)
