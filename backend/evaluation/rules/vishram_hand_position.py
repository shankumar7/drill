from backend.core.types import PoseDetection, RuleResult
from backend.evaluation.rules.base import EvaluationRule


class VishramHandPositionRule(EvaluationRule):
    name = "Hands behind back"

    def evaluate(self, detection: PoseDetection) -> RuleResult:
        k = detection.keypoints
        # Heuristic: If wrists (indices 9 and 10) are hidden/low confidence, assume they are behind the back
        lw_conf = k[9, 2]
        rw_conf = k[10, 2]
        
        score = 100.0 if (lw_conf < 0.3 and rw_conf < 0.3) else 40.0
        status = "pass" if score > 80.0 else "fail"
        
        return RuleResult(
            self.name,
            status,
            score,
            "Wrists should be clasped behind the back (left below, right above).",
        )
