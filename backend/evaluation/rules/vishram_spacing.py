from backend.core.types import PoseDetection, RuleResult
from backend.evaluation.rules.base import EvaluationRule


class VishramSpacingRule(EvaluationRule):
    name = "Foot spacing"

    def evaluate(self, detection: PoseDetection) -> RuleResult:
        geometry = detection.foot_geometry or {}
        heel_spacing = geometry.get("heel_to_heel_in")
        toe_spacing = geometry.get("toe_to_toe_in")
        if heel_spacing is None or toe_spacing is None:
            return RuleResult(
                self.name,
                "not_evaluable",
                None,
                "Official 12-inch heel and 18-inch toe spacing require calibrated ground-plane geometry.",
            )
        heel_error = abs(heel_spacing - 12.0)
        toe_error = abs(toe_spacing - 18.0)
        score = max(0.0, 100.0 - heel_error * 6.0 - toe_error * 4.0)
        status = "pass" if heel_error <= 1.5 and toe_error <= 2.0 else "fail"
        return RuleResult(
            self.name,
            status,
            round(score, 1),
            f"Heels {heel_spacing:.1f} in, toes {toe_spacing:.1f} in.",
        )
