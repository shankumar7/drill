from backend.core.types import PoseDetection, RuleResult
from backend.evaluation.geometry import angle_degrees
from backend.evaluation.rules.base import EvaluationRule

class SaluteRightArmAngleRule(EvaluationRule):
    name = "Saluting Arm Angle"

    def evaluate(self, detection: PoseDetection) -> RuleResult:
        k = detection.keypoints
        # Right Arm: Wrist (10), Elbow (8), Shoulder (6)
        if min(k[10, 2], k[8, 2], k[6, 2]) < 0.5:
            return RuleResult(self.name, "not_evaluable", None, "Right arm keypoints not reliable.")
            
        angle = angle_degrees(k[10, :2], k[8, :2], k[6, :2])
        
        # Ideal saluting interior angle is roughly 35 to 100 degrees
        score = 0.0
        if 35 <= angle <= 100:
            score = 100.0
        elif 20 <= angle < 35:
            score = 100.0 - ((35 - angle) * 6.6)
        elif 100 < angle <= 120:
            score = 100.0 - ((angle - 100) * 5.0)
            
        score = max(0.0, score)
        
        smoothed = self.smooth_score(detection, score)
        if isinstance(smoothed, RuleResult):
            return smoothed
            
        status = "pass" if smoothed >= 80 else "fail"
        return RuleResult(self.name, status, round(smoothed, 1), f"Arm Angle: {angle:.1f} (Ideal: 35-100)")


class StraightLeftArmAngleRule(EvaluationRule):
    name = "Straight Arm Angle"

    def evaluate(self, detection: PoseDetection) -> RuleResult:
        k = detection.keypoints
        # Left Arm: Wrist (9), Elbow (7), Shoulder (5)
        if min(k[9, 2], k[7, 2], k[5, 2]) < 0.5:
            return RuleResult(self.name, "not_evaluable", None, "Left arm keypoints not reliable.")
            
        angle = angle_degrees(k[9, :2], k[7, :2], k[5, :2])
        
        # Ideal straight arm is roughly 160 to 180 degrees
        score = 0.0
        if 160 <= angle <= 180:
            score = 100.0
        elif 140 <= angle < 160:
            score = 100.0 - ((160 - angle) * 5.0)
            
        score = max(0.0, score)
        
        smoothed = self.smooth_score(detection, score)
        if isinstance(smoothed, RuleResult):
            return smoothed
            
        status = "pass" if smoothed >= 80 else "fail"
        return RuleResult(self.name, status, round(smoothed, 1), f"Arm Angle: {angle:.1f} (Ideal: 160-180)")
