from backend.core.types import PoseDetection, RuleResult
from backend.evaluation.geometry import angle_degrees
from backend.evaluation.rules.base import EvaluationRule


class KneeLockRule(EvaluationRule):
    """Official Rule: 'donon ghutne kase hue' (both knees locked tight)
    
    Checks that Hip-Knee-Ankle angle is close to 180° (straight leg).
    Used in Vishram to verify legs are straight even with feet apart.
    """
    name = "Knee lock"

    def evaluate(self, detection: PoseDetection) -> RuleResult:
        k = detection.keypoints
        
        l_visible = min(k[11, 2], k[13, 2], k[15, 2]) >= 0.2
        r_visible = min(k[12, 2], k[14, 2], k[16, 2]) >= 0.2
        
        if not (l_visible or r_visible):
            return RuleResult(self.name, "not_evaluable", None, "Lower-limb keypoints are not reliable enough on either side.")
        
        scores = []
        msg_parts = []
        
        if l_visible:
            left = angle_degrees(k[11, :2], k[13, :2], k[15, :2])
            left_dev = abs(180 - left)
            scores.append(max(0.0, 100.0 - (left_dev * 1.5)))
            msg_parts.append(f"L: {left:.0f}°")
            
        if r_visible:
            right = angle_degrees(k[12, :2], k[14, :2], k[16, :2])
            right_dev = abs(180 - right)
            scores.append(max(0.0, 100.0 - (right_dev * 1.5)))
            msg_parts.append(f"R: {right:.0f}°")
            
        score = min(scores) # Worst visible knee dictates score
        
        history = detection.posture_history.setdefault(self.name, []) if detection.posture_history is not None else []
        history.append(score)
        del history[:-10]
        if len(history) < 3:
            return RuleResult(self.name, "not_evaluable", None, "Collecting stable knee evidence.")
        
        stable_score = sum(history) / len(history)
        status = "pass" if stable_score >= 90 else "fail"
        return RuleResult(
            self.name, 
            status, 
            round(stable_score, 1), 
            f"Knees should be locked. {', '.join(msg_parts)} (Ideal: 180°)"
        )
