from backend.core.types import PoseDetection, RuleResult
from backend.evaluation.rules.base import EvaluationRule


class SavdhanHeelContactRule(EvaluationRule):
    name = "Heel contact"

    def evaluate(self, detection: PoseDetection, camera_type: str = "front", **kwargs) -> RuleResult:
        if camera_type != "front":
            return RuleResult(self.name, "not_evaluable", None, "Requires front camera view.")
            
        geometry = detection.foot_geometry
        if not geometry:
            return RuleResult(self.name, "not_evaluable", None, "Foot geometry is unavailable.")
        gap = geometry.get("true_heel_dist")
        scale = geometry.get("spine_length")  # Changed from pose_scale (shoulder width) to spine_length
        if gap is None or scale in (None, 0, 100):
            return RuleResult(self.name, "not_evaluable", None, "Heel geometry is not reliable enough.")
            
        # Heels should be touching. Based on calibration, gap up to ~0.25 spine_length is normal due to perspective/pose variations.
        normalized_gap = gap / (scale + 1e-6)
        
        if normalized_gap <= 0.345:
            score = 100.0
        else:
            score = max(0.0, 100.0 - (normalized_gap - 0.345) * 500.0)
            
        status = "pass" if score >= 90 else "fail"
        return RuleResult(self.name, status, round(score, 1), f"Official rule requires both heels together. Gap ratio: {normalized_gap:.2f} (Threshold: 0.345)")
