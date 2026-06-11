from backend.core.types import PoseDetection, RuleResult
from backend.evaluation.geometry import angle_degrees, mid_point
from backend.evaluation.rules.base import EvaluationRule

class BackPostureRule(EvaluationRule):
    name = "Back Posture"
    def __init__(self, min_angle, max_angle):
        self.min_angle = min_angle
        self.max_angle = max_angle

    def evaluate(self, detection: PoseDetection) -> RuleResult:
        k = detection.keypoints
        # Ear (3, 4), Shoulder (5, 6), Hip (11, 12)
        if min(k[3, 2], k[4, 2], k[5, 2], k[6, 2], k[11, 2], k[12, 2]) < 0.5:
            return RuleResult(self.name, "not_evaluable", None, "Posture keypoints not reliable.")
            
        ear_center = mid_point(k[3, :2], k[4, :2])
        shoulder_center = mid_point(k[5, :2], k[6, :2])
        hip_center = mid_point(k[11, :2], k[12, :2])
        
        angle = angle_degrees(ear_center, shoulder_center, hip_center)
        # angle_degrees in geometry.py returns an interior angle (0-180).
        # The original code used 0-360. If the person is straight, Ear, Shoulder, Hip forms a vertical line, 
        # so interior angle is ~180. The original code checked 160-200 or 160-210.
        
        # We will use interior angle 0-180, so 160-180.
        score = 0.0
        if 160 <= angle <= 180:
            score = 100.0
        elif 130 <= angle < 160:
            score = ((angle - 130) / 30.0) * 100.0
            
        smoothed = self.smooth_score(detection, score)
        if isinstance(smoothed, RuleResult):
            return smoothed
            
        status = "pass" if smoothed >= 80 else "fail"
        return RuleResult(self.name, status, round(smoothed, 1), f"Angle: {angle:.1f} (Ideal: 160-180)")

class BodyPostureRule(EvaluationRule):
    name = "Body Posture"
    def __init__(self, min_angle, max_angle):
        self.min_angle = min_angle
        self.max_angle = max_angle

    def evaluate(self, detection: PoseDetection) -> RuleResult:
        k = detection.keypoints
        # Shoulder (5, 6), Hip (11, 12), Knee (13, 14)
        if min(k[5, 2], k[6, 2], k[11, 2], k[12, 2], k[13, 2], k[14, 2]) < 0.5:
            return RuleResult(self.name, "not_evaluable", None, "Body posture keypoints not reliable.")
            
        shoulder_center = mid_point(k[5, :2], k[6, :2])
        hip_center = mid_point(k[11, :2], k[12, :2])
        knee_center = mid_point(k[13, :2], k[14, :2])
        
        angle = angle_degrees(shoulder_center, hip_center, knee_center)
        
        score = 0.0
        if 160 <= angle <= 180:
            score = 100.0
        elif 130 <= angle < 160:
            score = ((angle - 130) / 30.0) * 100.0
            
        smoothed = self.smooth_score(detection, score)
        if isinstance(smoothed, RuleResult):
            return smoothed
            
        status = "pass" if smoothed >= 80 else "fail"
        return RuleResult(self.name, status, round(smoothed, 1), f"Angle: {angle:.1f} (Ideal: 160-180)")
