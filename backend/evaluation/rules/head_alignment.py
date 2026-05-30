import numpy as np

from backend.core.types import PoseDetection, RuleResult
from backend.evaluation.geometry import mid_point
from backend.evaluation.rules.base import EvaluationRule


class HeadAlignmentRule(EvaluationRule):
    name = "Head alignment"

    def evaluate(self, detection: PoseDetection) -> RuleResult:
        k = detection.keypoints
        if min(k[0, 2], k[5, 2], k[6, 2]) < 0.25:
            return RuleResult(self.name, "not_evaluable", None, "Head/shoulder keypoints are not reliable enough.")
        shoulder_mid = mid_point(k[5, :2], k[6, :2])
        nose = k[0, :2]
        horizontal_delta = abs(float(nose[0] - shoulder_mid[0]))
        shoulder_width = np.linalg.norm(k[5, :2] - k[6, :2])
        score = max(0.0, 100.0 - ((horizontal_delta / (shoulder_width + 1e-6)) * 250.0))
        status = "pass" if score >= 80 else "fail"
        return RuleResult(self.name, status, round(score, 1), "Chin and gaze should remain forward.")
