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
from backend.evaluation.rules.turning_details import DahineMurhRule, BayenMurhRule, PichheMurhRule
from backend.evaluation.rules.line_movements import KhuliLineChalRule, NikatLineChalRule
from backend.evaluation.rules.saj_alignment import SajAlignmentRule
from backend.evaluation.sequence import VisarjanSequence, TejChalSequence, ThaamSequence


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
        elif self.mode == "AARAM_SE":
            self.rules = [
                VishramSpacingRule() # Feet must stay in Vishram position, upper body is relaxed
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
        elif self.mode == "DAHINE_MURH":
            self.rules = [
                DahineMurhRule(),
                *shared
            ]
        elif self.mode == "BAYEN_MURH":
            self.rules = [
                BayenMurhRule(),
                *shared
            ]
        elif self.mode == "PICHHE_MURH":
            self.rules = [
                PichheMurhRule(),
                *shared
            ]
        elif self.mode == "KHULI_LINE_CHAL":
            self.rules = [
                KhuliLineChalRule(),
                *shared
            ]
        elif self.mode == "NIKAT_LINE_CHAL":
            self.rules = [
                NikatLineChalRule(),
                *shared
            ]
        elif self.mode == "SAJ":
            self.rules = [
                SajAlignmentRule(),
                *shared
            ]
        elif self.mode == "VISARJAN":
            self.rules = [
                VisarjanSequence(),
                *shared
            ]
        elif self.mode == "TEJ_CHAL":
            self.rules = [
                TejChalSequence(),
                *shared
            ]
        elif self.mode == "THAAM":
            self.rules = [
                ThaamSequence(),
                *shared
            ]
        else:
            self.rules = []
            
        self.histories: dict[int, dict[str, list[float]]] = {}

    def evaluate(self, detection: PoseDetection, all_detections: list[PoseDetection] = None) -> CadetEvaluation:
        detection.posture_history = self.histories.setdefault(detection.track_id, {})
        
        results = []
        for rule in self.rules:
            # Some rules like SajAlignmentRule can take all_detections
            if hasattr(rule.evaluate, "__code__") and "all_detections" in rule.evaluate.__code__.co_varnames:
                results.append(rule.evaluate(detection, all_detections))
            else:
                results.append(rule.evaluate(detection))
                
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
