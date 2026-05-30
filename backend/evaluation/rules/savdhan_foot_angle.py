from backend.core.types import PoseDetection, RuleResult
from backend.evaluation.rules.base import EvaluationRule


class SavdhanFootAngleRule(EvaluationRule):
    name = "Foot angle"

    def evaluate(self, detection: PoseDetection) -> RuleResult:
        geometry = detection.foot_geometry
        if not geometry:
            return RuleResult(self.name, "not_evaluable", None, "Foot geometry is unavailable.")
        angle = geometry.get("ground_plane_angle")
        if angle is None:
            return RuleResult(
                self.name,
                "not_evaluable",
                None,
                "Official 30-degree angle requires calibrated ground-plane geometry; image angle is not valid.",
            )
        deviation = abs(float(angle) - 30.0)
        score = max(0.0, 100.0 - deviation * 4.0)
        status = "pass" if 25.0 <= angle <= 35.0 else "fail"
        return RuleResult(self.name, status, round(score, 1), f"Measured toe angle {angle:.1f}°; official target is 30°.")
