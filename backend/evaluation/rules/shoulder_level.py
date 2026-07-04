from backend.core.types import PoseDetection, RuleResult
from backend.evaluation.geometry import segment_length
from backend.evaluation.rules.base import EvaluationRule


class ShoulderLevelRule(EvaluationRule):
    name = "Shoulder level"

    def evaluate(self, detection: PoseDetection) -> RuleResult:
        k = detection.keypoints
        if min(k[5, 2], k[6, 2]) < 0.25:
            return RuleResult(self.name, "not_evaluable", None, "Shoulder keypoints are not reliable enough.")
        geometry = detection.foot_geometry or {}
        spine_length = geometry.get("spine_length", 100)
        
        if spine_length < 20 or spine_length == 100:
            return RuleResult(self.name, "not_evaluable", None, "Spine length not reliable enough.")
            
        vertical_delta = abs(float(k[5, 1] - k[6, 1]))
        # We scale by spine_length, meaning the normalized tilt will be smaller than if we used width.
        # Adjusted multiplier from 400.0 to 500.0 to maintain similar strictness.
        score = max(0.0, 100.0 - ((vertical_delta / (spine_length + 1e-6)) * 500.0))
        history = detection.posture_history.setdefault(self.name, []) if detection.posture_history is not None else []
        history.append(score)
        del history[:-10]
        if len(history) < 5:
            return RuleResult(self.name, "not_evaluable", None, "Collecting stable shoulder evidence.")
        stable_score = sum(history) / len(history)
        if stable_score >= 82:
            return RuleResult(self.name, "pass", round(stable_score, 1), "Shoulders should remain level and pulled back.")
        if stable_score <= 60:
            return RuleResult(self.name, "fail", round(stable_score, 1), "Shoulders should remain level and pulled back.")
        return RuleResult(
            self.name,
            "not_evaluable",
            None,
            "Shoulder level remains ambiguous over the recent frame window.",
        )
