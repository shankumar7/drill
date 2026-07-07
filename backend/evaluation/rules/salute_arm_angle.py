from backend.core.types import PoseDetection, RuleResult
from backend.evaluation.geometry import angle_degrees
from backend.evaluation.rules.base import EvaluationRule

class SaluteRightArmAngleRule(EvaluationRule):
    name = "Saluting Arm Angle"

    def evaluate(self, detection: PoseDetection, camera_type: str = "front", **kwargs) -> RuleResult:
        if camera_type == "back":
            return RuleResult(self.name, "not_evaluable", None, "Back camera cannot evaluate salute properly.")
        k = detection.keypoints
        # Strict NCC rule: Right arm MUST be the saluting arm.
        # Right: Wrist (10), Elbow (8), Shoulder (6)
        
        right_conf = min(k[10, 2], k[8, 2], k[6, 2])
        
        if right_conf < 0.25:
            return RuleResult(self.name, "not_evaluable", None, "Right arm keypoints not reliable enough.")
            
        wrist, elbow, shoulder = k[10, :2], k[8, :2], k[6, :2]
        
        # Check if the wrist is raised above the elbow (saluting position)
        if wrist[1] > elbow[1]:  # y increases downward, so wrist below elbow means not saluting
            return RuleResult(self.name, "fail", 20.0, "Right arm is not raised for salute.")
            
        geometry = detection.foot_geometry or {}
        spine_length = geometry.get("spine_length", 100)
        
        # Check if the elbow is properly raised out to the side. 
        # If elbow is significantly below shoulder, the person is just putting their hand in front of their chest.
        elbow_drop = (elbow[1] - shoulder[1]) / (spine_length + 1e-6)
        if elbow_drop > 0.2:
            return RuleResult(self.name, "fail", 40.0, "Right elbow must be raised out, not tucked down.")
            
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
            
        status = "pass" if smoothed >= 90 else "fail"
        return RuleResult(self.name, status, round(smoothed, 1), f"Right Arm Angle: {angle:.1f}° (Ideal: 25-120)")


class StraightLeftArmAngleRule(EvaluationRule):
    name = "Straight Arm Angle"

    def evaluate(self, detection: PoseDetection, camera_type: str = "front", **kwargs) -> RuleResult:
        k = detection.keypoints
        # Strict NCC rule: Left arm MUST be straight at the side during salute.
        # Left: Wrist (9), Elbow (7), Shoulder (5)
        
        left_conf = min(k[9, 2], k[7, 2], k[5, 2])
        
        if left_conf < 0.25:
            return RuleResult(self.name, "not_evaluable", None, "Left arm keypoints not reliable enough.")
            
        wrist, elbow, shoulder = k[9, :2], k[7, :2], k[5, :2]
            
        angle = angle_degrees(wrist, elbow, shoulder)
        
        # Ideal straight arm is roughly 145 to 180 degrees
        score = 0.0
        if 145 <= angle <= 180:
            score = 100.0
        elif 120 <= angle < 145:
            score = 100.0 - ((145 - angle) * 4.0)
            
        score = max(0.0, score)
        
        smoothed = self.smooth_score(detection, score)
        if isinstance(smoothed, RuleResult):
            return smoothed
            
        status = "pass" if smoothed >= 90 else "fail"
        return RuleResult(self.name, status, round(smoothed, 1), f"Left Arm Angle: {angle:.1f}° (Ideal: 145-180)")
