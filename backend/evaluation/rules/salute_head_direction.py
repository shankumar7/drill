from backend.core.types import PoseDetection, RuleResult
from backend.evaluation.rules.base import EvaluationRule

class HeadDirectionRule(EvaluationRule):
    name = "Head Direction"

    def __init__(self, target_direction: str):
        # 'front', 'left' (baye), 'right' (daine)
        self.target_direction = target_direction.lower()

    def evaluate(self, detection: PoseDetection) -> RuleResult:
        k = detection.keypoints
        # Nose (0), L Ear (3), R Ear (4)
        if min(k[0, 2], k[3, 2], k[4, 2]) < 0.5:
            return RuleResult(self.name, "not_evaluable", None, "Head keypoints not reliable.")
            
        nose_x = k[0, 0]
        l_ear_x = k[3, 0] # Person's left ear, image right
        r_ear_x = k[4, 0] # Person's right ear, image left
        
        # Calculate ratio of nose position between ears
        ear_width = l_ear_x - r_ear_x
        if ear_width < 1:
            return RuleResult(self.name, "not_evaluable", None, "Ears too close or missing.")
            
        ratio = (nose_x - r_ear_x) / ear_width
        
        score = 0.0
        msg = ""
        if self.target_direction == "front":
            # Ideal is 0.5
            dist = abs(ratio - 0.5)
            score = max(0.0, 100 - (dist * 400)) # 0.5 is 100, 0.25 is 0
            msg = "Head should face front"
        elif self.target_direction == "left":
            # Baye Salute, head turned left (ratio > 0.7)
            if ratio >= 0.65:
                score = 100.0
            else:
                score = max(0.0, 100 - ((0.65 - ratio) * 400))
            msg = "Head should be turned left (Baye)"
        elif self.target_direction == "right":
            # Daine Salute, head turned right (ratio < 0.35)
            if ratio <= 0.35:
                score = 100.0
            else:
                score = max(0.0, 100 - ((ratio - 0.35) * 400))
            msg = "Head should be turned right (Daine)"
            
        smoothed = self.smooth_score(detection, score)
        if isinstance(smoothed, RuleResult):
            return smoothed
            
        status = "pass" if smoothed >= 80 else "fail"
        return RuleResult(self.name, status, round(smoothed, 1), f"{msg} (ratio: {ratio:.2f})")
