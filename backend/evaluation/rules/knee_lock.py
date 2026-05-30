from backend.core.types import PoseDetection, RuleResult
from backend.evaluation.geometry import angle_degrees
from backend.evaluation.rules.base import EvaluationRule


class KneeLockRule(EvaluationRule):
    name = "Knee lock"

    def evaluate(self, detection: PoseDetection) -> RuleResult:
        k = detection.keypoints
        if min(k[11, 2], k[13, 2], k[15, 2], k[12, 2], k[14, 2], k[16, 2]) < 0.25:
            return RuleResult(self.name, "not_evaluable", None, "Lower-limb keypoints are not reliable enough.")
        left = angle_degrees(k[11, :2], k[13, :2], k[15, :2])
        right = angle_degrees(k[12, :2], k[14, :2], k[16, :2])
        score = max(0.0, 100.0 - ((abs(180 - left) + abs(180 - right)) * 2.0))
        history = detection.posture_history.setdefault(self.name, []) if detection.posture_history is not None else []
        history.append(score)
        del history[:-10]
        if len(history) < 5:
            return RuleResult(self.name, "not_evaluable", None, "Collecting stable knee evidence.")
        stable_score = sum(history) / len(history)
        if stable_score >= 84:
            return RuleResult(self.name, "pass", round(stable_score, 1), "Both knees should remain locked.")
        if stable_score <= 60:
            return RuleResult(self.name, "fail", round(stable_score, 1), "Both knees should remain locked.")
        return RuleResult(
            self.name,
            "not_evaluable",
            None,
            "Knee straightness remains ambiguous over the recent frame window.",
        )
