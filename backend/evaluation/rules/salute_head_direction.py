from backend.core.types import PoseDetection, RuleResult
from backend.evaluation.rules.base import EvaluationRule

class HeadDirectionRule(EvaluationRule):
    """Official Rule: 
    - Samne Salute: 'nigah samne' (eyes looking straight ahead)
    - Dahine Salute: 'nigah puri dahine taraf' (eyes fully to the right)
    - Bayen Salute: 'nigah puri bayen taraf' (eyes fully to the left)
    """
    name = "Head Direction"

    def __init__(self, target_direction: str):
        # 'front', 'left' (baye), 'right' (dahine)
        self.target_direction = target_direction.lower()

    def evaluate(self, detection: PoseDetection) -> RuleResult:
        k = detection.keypoints
        # Nose (0), L Ear (3), R Ear (4)
        nose_conf = k[0, 2]
        l_ear_conf = k[3, 2]
        r_ear_conf = k[4, 2]
        
        # We need the nose and BOTH ears to accurately determine head direction.
        # If an ear is missing, the camera is looking at a profile, meaning it cannot 
        # accurately judge left/right pan relative to the shoulders.
        # By returning not_evaluable here, we allow the max-fusion system in api.py 
        # to organically select the camera that CAN see both ears!
        if nose_conf < 0.25 or l_ear_conf < 0.25 or r_ear_conf < 0.25:
            return RuleResult(self.name, "not_evaluable", None, "Full face not visible from this camera angle.")
            
        nose_x = k[0, 0]
        l_ear_x = k[3, 0]  # Person's left ear
        r_ear_x = k[4, 0]  # Person's right ear
        
        ear_width = abs(l_ear_x - r_ear_x)
        if ear_width < 10:
            return RuleResult(self.name, "not_evaluable", None, "Ears too close (perspective squash).")
            
        # Ratio: 0 = nose at right ear, 0.5 = centered, 1.0 = nose at left ear
        ratio = (nose_x - min(l_ear_x, r_ear_x)) / ear_width
        
        score = 0.0
        msg = ""
        if self.target_direction == "front":
            # Official: 'nigah samne' - eyes straight ahead. Ideal ratio = 0.5
            dist = abs(ratio - 0.5)
            score = max(0.0, 100 - (dist * 400))
            msg = "Head should face front (nigah samne)"
        elif self.target_direction == "left":
            # Official: 'nigah puri bayen taraf' - eyes fully left. Ratio > 0.7
            if ratio >= 0.7:
                score = 100.0
            else:
                score = max(0.0, 100.0 - ((0.7 - ratio) * 300))
            msg = "Head should be turned left - Bayen (nigah puri bayen taraf)"
        elif self.target_direction == "right":
            # Official: 'nigah puri dahine taraf' - eyes fully right. Ratio < 0.3
            if ratio <= 0.3:
                score = 100.0
            else:
                score = max(0.0, 100.0 - ((ratio - 0.3) * 300))
            msg = "Head should be turned right - Dahine (nigah puri dahine taraf)"
            
        smoothed = self.smooth_score(detection, score)
        if isinstance(smoothed, RuleResult):
            return smoothed
            
        status = "pass" if smoothed >= 90 else "fail"
        return RuleResult(self.name, status, round(smoothed, 1), f"{msg} (ratio: {ratio:.2f})")
