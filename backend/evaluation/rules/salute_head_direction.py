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
        # Nose (0), L Ear (3), R Ear (4), L Eye (1), R Eye (2)
        # Use nose and ears for head direction detection
        # Also try eyes as fallback if ears are occluded (e.g., head turned)
        
        nose_conf = k[0, 2]
        l_ear_conf = k[3, 2]
        r_ear_conf = k[4, 2]
        
        # For head direction, we need at least the nose
        if nose_conf < 0.3:
            return RuleResult(self.name, "not_evaluable", None, "Nose keypoint not reliable.")
        
        nose_x = k[0, 0]
        
        # If both ears are visible, use ear-based ratio
        if l_ear_conf >= 0.3 and r_ear_conf >= 0.3:
            l_ear_x = k[3, 0]  # Person's left ear (image right for front-facing)
            r_ear_x = k[4, 0]  # Person's right ear (image left for front-facing)
            
            ear_width = abs(l_ear_x - r_ear_x)
            if ear_width < 1:
                return RuleResult(self.name, "not_evaluable", None, "Ears too close.")
                
            # Ratio: 0 = nose at right ear, 0.5 = centered, 1.0 = nose at left ear
            ratio = (nose_x - min(l_ear_x, r_ear_x)) / ear_width
        else:
            # One ear hidden = head is turned. Determine which ear is hidden.
            # If right ear hidden (low conf), head is turned to the left (person's left)
            # If left ear hidden, head is turned to the right (person's right)
            if r_ear_conf < 0.3 and l_ear_conf >= 0.3:
                # Right ear hidden - head turned right (dahine direction)
                ratio = 0.1  # Simulated strong right turn
            elif l_ear_conf < 0.3 and r_ear_conf >= 0.3:
                # Left ear hidden - head turned left (bayen direction)
                ratio = 0.9  # Simulated strong left turn
            else:
                # Both ears hidden - use eyes as fallback
                l_eye_conf = k[1, 2]
                r_eye_conf = k[2, 2]
                if l_eye_conf >= 0.3 and r_eye_conf >= 0.3:
                    eye_width = abs(k[1, 0] - k[2, 0])
                    if eye_width < 1:
                        return RuleResult(self.name, "not_evaluable", None, "Eyes too close.")
                    ratio = (nose_x - min(k[1, 0], k[2, 0])) / eye_width
                    ratio = max(0, min(1, ratio * 0.5 + 0.25))  # Normalize to 0-1 range
                else:
                    return RuleResult(self.name, "not_evaluable", None, "Head keypoints not reliable.")
        
        score = 0.0
        msg = ""
        if self.target_direction == "front":
            # Official: 'nigah samne' - eyes straight ahead. Ideal ratio = 0.5
            dist = abs(ratio - 0.5)
            score = max(0.0, 100 - (dist * 300))  # More lenient than before
            msg = "Head should face front (nigah samne)"
        elif self.target_direction == "left":
            # Official: 'nigah puri bayen taraf' - eyes fully left. Ratio > 0.7
            if ratio >= 0.6:
                score = min(100.0, 50 + (ratio - 0.6) * 125)
            else:
                score = max(0.0, ratio * 83)
            msg = "Head should be turned left - Bayen (nigah puri bayen taraf)"
        elif self.target_direction == "right":
            # Official: 'nigah puri dahine taraf' - eyes fully right. Ratio < 0.3
            if ratio <= 0.4:
                score = min(100.0, 50 + (0.4 - ratio) * 125)
            else:
                score = max(0.0, (1.0 - ratio) * 83)
            msg = "Head should be turned right - Dahine (nigah puri dahine taraf)"
            
        smoothed = self.smooth_score(detection, score)
        if isinstance(smoothed, RuleResult):
            return smoothed
            
        status = "pass" if smoothed >= 80 else "fail"
        return RuleResult(self.name, status, round(smoothed, 1), f"{msg} (ratio: {ratio:.2f})")
