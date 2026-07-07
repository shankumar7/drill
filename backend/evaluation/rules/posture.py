from backend.core.types import PoseDetection, RuleResult
from backend.evaluation.geometry import angle_degrees, mid_point
from backend.evaluation.rules.base import EvaluationRule

class BackPostureRule(EvaluationRule):
    """Official Rule: 'Chhati uthi hui, kandhe pichhe khinche hue, gardan collar ke sath mili hui, chin upar'
    (Chest raised, shoulders pulled back, neck aligned with collar, chin up)
    
    Checks the alignment of Ear-Shoulder-Hip to verify upright posture.
    """
    name = "Back Posture"
    def __init__(self, min_angle=160, max_angle=210):
        self.min_angle = min_angle
        self.max_angle = max_angle

    def evaluate(self, detection: PoseDetection, camera_type: str = "front", **kwargs) -> RuleResult:
        if camera_type != "side":
            return RuleResult(self.name, "not_evaluable", None, "Requires side camera view.")
            
        k = detection.keypoints
        # Ear (3, 4), Shoulder (5, 6), Hip (11, 12)
        l_visible = min(k[3, 2], k[5, 2], k[11, 2]) >= 0.25
        r_visible = min(k[4, 2], k[6, 2], k[12, 2]) >= 0.25
        
        if not (l_visible or r_visible):
            # If neither side has all 3 points, fallback to using whatever is available as midpoints
            if min(max(k[3,2], k[4,2]), max(k[5,2], k[6,2]), max(k[11,2], k[12,2])) < 0.2:
                return RuleResult(self.name, "not_evaluable", None, "Posture keypoints not reliable.")
                
        # Calculate angles for visible sides
        angles = []
        if l_visible:
            angles.append(angle_degrees(k[3, :2], k[5, :2], k[11, :2]))
        if r_visible:
            angles.append(angle_degrees(k[4, :2], k[6, :2], k[12, :2]))
            
        if not angles:
            # Fallback to midpoint if neither strict side is fully visible but individual points exist
            ear_center = k[3, :2] if k[3,2] > k[4,2] else k[4, :2]
            shoulder_center = k[5, :2] if k[5,2] > k[6,2] else k[6, :2]
            hip_center = k[11, :2] if k[11,2] > k[12,2] else k[12, :2]
            angles.append(angle_degrees(ear_center, shoulder_center, hip_center))
            
        angle = sum(angles) / len(angles)
        
        # For erect posture (chest up, shoulders back), Ear-Shoulder-Hip should be ~180°
        # Official: chest raised (chhati uthi hui), shoulders pulled back
        score = 0.0
        if 155 <= angle <= 180:
            score = 100.0
        elif 130 <= angle < 155:
            score = ((angle - 130) / 25.0) * 100.0
            
        smoothed = self.smooth_score(detection, score)
        if isinstance(smoothed, RuleResult):
            return smoothed
            
        status = "pass" if smoothed >= 90 else "fail"
        return RuleResult(self.name, status, round(smoothed, 1), 
                         f"Ear-Shoulder-Hip angle: {angle:.1f}° (Ideal: 155-180°). "
                         f"Chest should be raised, shoulders pulled back.")

class BodyPostureRule(EvaluationRule):
    """Official Rule: 'Pet andar ki taraf' (Stomach pulled in)
    
    Checks the Shoulder-Hip-Knee alignment for straight body posture.
    """
    name = "Body Posture"
    def __init__(self, min_angle=160, max_angle=200):
        self.min_angle = min_angle
        self.max_angle = max_angle

    def evaluate(self, detection: PoseDetection, camera_type: str = "front", **kwargs) -> RuleResult:
        k = detection.keypoints
        # Shoulder (5, 6), Hip (11, 12), Knee (13, 14)
        l_visible = min(k[5, 2], k[11, 2], k[13, 2]) >= 0.25
        r_visible = min(k[6, 2], k[12, 2], k[14, 2]) >= 0.25
        
        if not (l_visible or r_visible):
            if min(max(k[5,2], k[6,2]), max(k[11,2], k[12,2]), max(k[13,2], k[14,2])) < 0.2:
                return RuleResult(self.name, "not_evaluable", None, "Body posture keypoints not reliable.")
                
        angles = []
        if l_visible:
            angles.append(angle_degrees(k[5, :2], k[11, :2], k[13, :2]))
        if r_visible:
            angles.append(angle_degrees(k[6, :2], k[12, :2], k[14, :2]))
            
        if not angles:
            shoulder_center = k[5, :2] if k[5,2] > k[6,2] else k[6, :2]
            hip_center = k[11, :2] if k[11,2] > k[12,2] else k[12, :2]
            knee_center = k[13, :2] if k[13,2] > k[14,2] else k[14, :2]
            angles.append(angle_degrees(shoulder_center, hip_center, knee_center))
            
        angle = sum(angles) / len(angles)
        
        # Official: Stomach pulled in, body straight. Shoulder-Hip-Knee ~180°
        score = 0.0
        if 155 <= angle <= 180:
            score = 100.0
        elif 130 <= angle < 155:
            score = ((angle - 130) / 25.0) * 100.0
            
        smoothed = self.smooth_score(detection, score)
        if isinstance(smoothed, RuleResult):
            return smoothed
            
        status = "pass" if smoothed >= 90 else "fail"
        return RuleResult(self.name, status, round(smoothed, 1), 
                         f"Shoulder-Hip-Knee angle: {angle:.1f}° (Ideal: 155-180°). "
                         f"Stomach should be pulled in, body straight.")
