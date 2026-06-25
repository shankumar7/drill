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
        # Lower confidence threshold
        if min(k[11, 2], k[13, 2], k[15, 2], k[12, 2], k[14, 2], k[16, 2]) < 0.2:
            return RuleResult(self.name, "not_evaluable", None, "Lower-limb keypoints are not reliable enough.")
        
        left = angle_degrees(k[11, :2], k[13, :2], k[15, :2])
        right = angle_degrees(k[12, :2], k[14, :2], k[16, :2])
        
        # Both legs should be straight (~180°). More lenient threshold.
        left_deviation = abs(180 - left)
        right_deviation = abs(180 - right)
        score = max(0.0, 100.0 - ((left_deviation + right_deviation) * 1.5))
        
        history = detection.posture_history.setdefault(self.name, []) if detection.posture_history is not None else []
        history.append(score)
        del history[:-10]
        if len(history) < 3:  # Reduced from 5 to 3 for faster feedback
            return RuleResult(self.name, "not_evaluable", None, "Collecting stable knee evidence.")
        
        stable_score = sum(history) / len(history)
        status = "pass" if stable_score >= 75 else "fail"
        return RuleResult(
            self.name, 
            status, 
            round(stable_score, 1), 
            f"Knees should be locked (donon ghutne kase hue). L: {left:.0f}°, R: {right:.0f}° (Ideal: 180°)"
        )
