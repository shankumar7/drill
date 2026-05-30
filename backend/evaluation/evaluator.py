from backend.core.types import CadetEvaluation, PoseDetection
from backend.evaluation.rules.head_alignment import HeadAlignmentRule
from backend.evaluation.rules.knee_lock import KneeLockRule
from backend.evaluation.rules.savdhan_arm_position import SavdhanArmPositionRule
from backend.evaluation.rules.savdhan_foot_angle import SavdhanFootAngleRule
from backend.evaluation.rules.savdhan_heel_contact import SavdhanHeelContactRule
from backend.evaluation.rules.shoulder_level import ShoulderLevelRule
from backend.evaluation.rules.vishram_hand_position import VishramHandPositionRule
from backend.evaluation.rules.vishram_spacing import VishramSpacingRule


class StaticPostureEvaluator:
    def __init__(self, mode: str) -> None:
        self.mode = mode.upper()
        shared = [KneeLockRule(), ShoulderLevelRule(), HeadAlignmentRule()]
        self.rules = (
            [SavdhanHeelContactRule(), SavdhanFootAngleRule(), SavdhanArmPositionRule(), *shared]
            if self.mode == "SAVDHAN"
            else [VishramSpacingRule(), VishramHandPositionRule(), *shared]
        )
        self.histories: dict[int, dict[str, list[float]]] = {}

    def evaluate(self, detection: PoseDetection) -> CadetEvaluation:
        detection.posture_history = self.histories.setdefault(detection.track_id, {})
        results = [rule.evaluate(detection) for rule in self.rules]
        scored = [result.score for result in results if result.score is not None]
        overall = round(sum(scored) / len(scored), 1) if scored else None
        if not scored:
            status = "not_evaluable"
        elif any(result.status == "fail" for result in results):
            status = "needs_attention"
        elif any(result.status == "not_evaluable" for result in results):
            status = "partial_pass"
        else:
            status = "pass"
        return CadetEvaluation(self.mode, overall, status, results)
