from backend.core.types import PoseDetection, RuleResult
from backend.evaluation.utils import angular_velocity
from .base import EvaluationRule

class TurnLeftRule(EvaluationRule):
    name = "Turn Left"

    def evaluate(self, detection: PoseDetection) -> RuleResult:
        vel = angular_velocity(detection, axis="y")
        if vel is None:
            return RuleResult(self.name, "partial_pass", None, "Insufficient pose history for turn detection")
        score = max(0, min(100, 100 - vel * 5))
        return RuleResult(self.name, "pass", round(score, 1), f"Angular velocity {vel:.2f}°/s")

class TurnRightRule(EvaluationRule):
    name = "Turn Right"

    def evaluate(self, detection: PoseDetection) -> RuleResult:
        vel = angular_velocity(detection, axis="y")
        if vel is None:
            return RuleResult(self.name, "partial_pass", None, "Insufficient pose history for turn detection")
        score = max(0, min(100, 100 + vel * 5))
        return RuleResult(self.name, "pass", round(score, 1), f"Angular velocity {vel:.2f}°/s")

class Pivot180Rule(EvaluationRule):
    name = "Pivot 180"

    def evaluate(self, detection: PoseDetection) -> RuleResult:
        vel = angular_velocity(detection, axis="y")
        if vel is None:
            return RuleResult(self.name, "partial_pass", None, "Insufficient pose history for pivot detection")
        if abs(vel) > 30:
            return RuleResult(self.name, "pass", 100, f"Pivot detected ({vel:.2f}°/s)")
        return RuleResult(self.name, "fail", 0, f"No pivot (vel {vel:.2f}°/s)")
