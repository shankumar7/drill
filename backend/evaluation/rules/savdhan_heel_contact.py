from backend.core.types import PoseDetection, RuleResult
from backend.evaluation.rules.base import EvaluationRule


class SavdhanHeelContactRule(EvaluationRule):
    name = "Heel contact"

    def evaluate(self, detection: PoseDetection) -> RuleResult:
        geometry = detection.foot_geometry
        if not geometry:
            return RuleResult(self.name, "not_evaluable", None, "Foot geometry is unavailable.")
        gap = geometry.get("true_heel_dist")
        scale = geometry.get("pose_scale")
        if gap is None or scale in (None, 0):
            return RuleResult(self.name, "not_evaluable", None, "Heel geometry is not reliable enough.")
        normalized_gap = gap / (scale + 1e-6)
        score = max(0.0, 100.0 - normalized_gap * 220.0)
        status = "pass" if score >= 80 else "fail"
        return RuleResult(self.name, status, round(score, 1), "Official rule requires both heels together.")
