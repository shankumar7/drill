from backend.core.types import CadetEvaluation, PoseDetection
from backend.evaluation.rules.head_alignment import HeadAlignmentRule
from backend.evaluation.rules.knee_lock import KneeLockRule
from backend.evaluation.rules.savdhan_arm_position import SavdhanArmPositionRule
from backend.evaluation.rules.savdhan_foot_angle import SavdhanFootAngleRule
from backend.evaluation.rules.savdhan_heel_contact import SavdhanHeelContactRule
from backend.evaluation.rules.shoulder_level import ShoulderLevelRule
from backend.evaluation.rules.vishram_hand_position import VishramHandPositionRule
from backend.evaluation.rules.vishram_spacing import VishramSpacingRule

from backend.evaluation.rules.posture import BackPostureRule, BodyPostureRule
from backend.evaluation.rules.knee_distance import KneeDistanceRule
from backend.evaluation.rules.salute_arm_angle import SaluteRightArmAngleRule, StraightLeftArmAngleRule
from backend.evaluation.rules.salute_head_direction import HeadDirectionRule
from backend.evaluation.rules.salute_hand_position import SaluteHandPositionRule


class StaticPostureEvaluator:
    def __init__(self, mode: str) -> None:
        self.mode = mode.upper()
        
        shared = [
            BackPostureRule(160, 210), 
            BodyPostureRule(160, 200),
            ShoulderLevelRule()
        ]
        
        if self.mode == "SAVDHAN":
            self.rules = [
                SavdhanHeelContactRule(),
                SavdhanFootAngleRule(),
                SavdhanArmPositionRule(),
                KneeDistanceRule("close"),
                HeadAlignmentRule(),
                *shared
            ]
        elif self.mode == "VISHRAM":
            self.rules = [
                VishramSpacingRule(),
                VishramHandPositionRule(),
                KneeLockRule(),
                HeadAlignmentRule(),
                *shared
            ]
        elif self.mode == "FRONT_SALUTE":
            self.rules = [
                KneeDistanceRule("relaxed"),
                SaluteRightArmAngleRule(),
                StraightLeftArmAngleRule(),
                SaluteHandPositionRule(),
                HeadDirectionRule("front"),
                *shared
            ]
        elif self.mode == "BAYE_SALUTE":
            self.rules = [
                KneeDistanceRule("relaxed"),
                SaluteRightArmAngleRule(),
                StraightLeftArmAngleRule(),
                SaluteHandPositionRule(),
                HeadDirectionRule("left"),
                *shared
            ]
        elif self.mode == "DAINE_SALUTE":
            self.rules = [
                KneeDistanceRule("relaxed"),
                SaluteRightArmAngleRule(),
                StraightLeftArmAngleRule(),
                SaluteHandPositionRule(),
                HeadDirectionRule("right"),
                *shared
            ]
        else:
            self.rules = []
            
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
