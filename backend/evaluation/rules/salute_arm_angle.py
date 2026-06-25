from backend.core.types import PoseDetection, RuleResult
from backend.evaluation.geometry import angle_degrees
from backend.evaluation.rules.base import EvaluationRule

class SaluteRightArmAngleRule(EvaluationRule):
    name = "Saluting Arm Angle"

    def evaluate(self, detection: PoseDetection) -> RuleResult:
        k = detection.keypoints
        # Try right arm first: Wrist (10), Elbow (8), Shoulder (6)
        # Then fall back to left arm: Wrist (9), Elbow (7), Shoulder (5)
        # This handles mirrored webcam feeds where the saluting arm may appear on either side
        
        right_conf = min(k[10, 2], k[8, 2], k[6, 2])
        left_conf = min(k[9, 2], k[7, 2], k[5, 2])
        
        if right_conf >= 0.3:
            wrist, elbow, shoulder = k[10, :2], k[8, :2], k[6, :2]
            arm_label = "Right"
        elif left_conf >= 0.3:
            wrist, elbow, shoulder = k[9, :2], k[7, :2], k[5, :2]
            arm_label = "Left"
        else:
            return RuleResult(self.name, "not_evaluable", None, "Arm keypoints not reliable.")
        
        # Check if the wrist is raised above the elbow (saluting position)
        if wrist[1] > elbow[1]:  # y increases downward, so wrist below elbow means not saluting
            return RuleResult(self.name, "fail", 20.0, f"{arm_label} arm is not raised for salute.")
            
        angle = angle_degrees(wrist, elbow, shoulder)
        
        # Ideal saluting interior angle is roughly 25 to 120 degrees (widened for real-world tolerance)
        score = 0.0
        if 25 <= angle <= 120:
            score = 100.0
        elif 15 <= angle < 25:
            score = 100.0 - ((25 - angle) * 10.0)
        elif 120 < angle <= 145:
            score = 100.0 - ((angle - 120) * 4.0)
            
        score = max(0.0, score)
        
        smoothed = self.smooth_score(detection, score)
        if isinstance(smoothed, RuleResult):
            return smoothed
            
        status = "pass" if smoothed >= 80 else "fail"
        return RuleResult(self.name, status, round(smoothed, 1), f"{arm_label} Arm Angle: {angle:.1f}° (Ideal: 25-120)")


class StraightLeftArmAngleRule(EvaluationRule):
    name = "Straight Arm Angle"

    def evaluate(self, detection: PoseDetection) -> RuleResult:
        k = detection.keypoints
        # Try left arm first: Wrist (9), Elbow (7), Shoulder (5)
        # Then fall back to right arm: Wrist (10), Elbow (8), Shoulder (6)
        
        left_conf = min(k[9, 2], k[7, 2], k[5, 2])
        right_conf = min(k[10, 2], k[8, 2], k[6, 2])
        
        if left_conf >= 0.3:
            wrist, elbow, shoulder = k[9, :2], k[7, :2], k[5, :2]
            arm_label = "Left"
        elif right_conf >= 0.3:
            wrist, elbow, shoulder = k[10, :2], k[8, :2], k[6, :2]
            arm_label = "Right"
        else:
            return RuleResult(self.name, "not_evaluable", None, "Arm keypoints not reliable.")
            
        angle = angle_degrees(wrist, elbow, shoulder)
        
        # Ideal straight arm is roughly 145 to 180 degrees (relaxed lower bound)
        score = 0.0
        if 145 <= angle <= 180:
            score = 100.0
        elif 120 <= angle < 145:
            score = 100.0 - ((145 - angle) * 4.0)
            
        score = max(0.0, score)
        
        smoothed = self.smooth_score(detection, score)
        if isinstance(smoothed, RuleResult):
            return smoothed
            
        status = "pass" if smoothed >= 80 else "fail"
        return RuleResult(self.name, status, round(smoothed, 1), f"{arm_label} Arm Angle: {angle:.1f}° (Ideal: 145-180)")
