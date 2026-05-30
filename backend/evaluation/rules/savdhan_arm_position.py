import numpy as np

from backend.core.types import PoseDetection, RuleResult
from backend.evaluation.rules.base import EvaluationRule


class SavdhanArmPositionRule(EvaluationRule):
    name = "Arms at sides"

    def evaluate(self, detection: PoseDetection) -> RuleResult:
        k = detection.keypoints
        if detection.mask is None:
            return RuleResult(self.name, "not_evaluable", None, "Segmentation mask is required for arm-side assessment.")
        if min(k[9, 2], k[10, 2]) < 0.25:
            return RuleResult(self.name, "not_evaluable", None, "Wrist keypoints are not reliable enough.")

        mask = detection.mask > 0.5
        if not np.any(mask):
            return RuleResult(self.name, "not_evaluable", None, "Segmentation mask is empty.")

        distances = []
        for wrist_index, side in ((9, "left"), (10, "right")):
            wx, wy = k[wrist_index, :2]
            row = mask[int(round(wy))] if 0 <= int(round(wy)) < mask.shape[0] else None
            if row is None or not np.any(row):
                return RuleResult(self.name, "not_evaluable", None, "Silhouette boundary is unavailable at wrist height.")
            xs = np.where(row)[0]
            boundary_x = xs[0] if side == "left" else xs[-1]
            distances.append(abs(float(wx) - float(boundary_x)))

        body_width = max(1.0, float(np.where(mask)[1].max() - np.where(mask)[1].min()))
        normalized_distance = sum(distances) / (2.0 * body_width)
        score = max(0.0, 100.0 - normalized_distance * 220.0)

        history = detection.posture_history.setdefault(self.name, []) if detection.posture_history is not None else []
        history.append(score)
        del history[:-10]
        if len(history) < 5:
            return RuleResult(self.name, "not_evaluable", None, "Collecting stable arm-position evidence.")
        stable_score = sum(history) / len(history)
        if stable_score >= 80:
            return RuleResult(self.name, "pass", round(stable_score, 1), "Arms should remain close to the trouser seams.")
        if stable_score <= 55:
            return RuleResult(self.name, "fail", round(stable_score, 1), "Arms appear visibly away from the body.")
        return RuleResult(self.name, "not_evaluable", None, "Arm position remains ambiguous over the recent frame window.")
