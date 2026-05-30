from backend.core.types import PoseDetection, RuleResult
from backend.evaluation.rules.base import EvaluationRule


class VishramHandPositionRule(EvaluationRule):
    name = "Hands behind back"

    def evaluate(self, detection: PoseDetection) -> RuleResult:
        return RuleResult(
            self.name,
            "not_evaluable",
            None,
            "Single frontal 2D view cannot reliably confirm hand order behind the back.",
        )
