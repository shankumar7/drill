
from backend.evaluation.rules.savdhan_shared import SavdhanBackPostureRule, SavdhanBodyPostureRule, SavdhanShoulderLevelRule, SavdhanHeadAlignmentRule
from backend.evaluation.rules.vishram_shared import VishramBackPostureRule, VishramBodyPostureRule, VishramShoulderLevelRule, VishramHeadAlignmentRule
from backend.evaluation.rules.generic_shared import GenericBackPostureRule, GenericBodyPostureRule, GenericShoulderLevelRule, GenericHeadAlignmentRule
from backend.core.types import CadetEvaluation, PoseDetection
from backend.evaluation.rules.knee_lock import KneeLockRule
from backend.evaluation.rules.savdhan_arm_position import SavdhanArmPositionRule
from backend.evaluation.rules.savdhan_foot_angle import SavdhanFootAngleRule
from backend.evaluation.rules.savdhan_heel_contact import SavdhanHeelContactRule
from backend.evaluation.rules.vishram_hand_position import VishramHandPositionRule
from backend.evaluation.rules.vishram_spacing import VishramSpacingRule
from backend.evaluation.rules.calibration import AutoCalibrationRule

from backend.evaluation.rules.knee_distance import KneeDistanceRule
from backend.evaluation.rules.salute_arm_angle import SaluteRightArmAngleRule, StraightLeftArmAngleRule
from backend.evaluation.rules.salute_head_direction import HeadDirectionRule
from backend.evaluation.rules.salute_hand_position import SaluteHandPositionRule
from backend.evaluation.rules.turning_details import DahineMurhRule, BayenMurhRule, PichheMurhRule
from backend.evaluation.rules.line_movements import KhuliLineChalRule, NikatLineChalRule
from backend.evaluation.rules.saj_alignment import SajAlignmentRule
from backend.evaluation.sequence import VisarjanSequence, TejChalSequence, ThaamSequence, MarchingSaluteSequence, MarchingTurnSequence


class StaticPostureEvaluator:
    def __init__(self, mode: str) -> None:
        self.mode = mode.upper()
        
        if self.mode == "CALIBRATION":
            self.rules = [AutoCalibrationRule()]
        elif self.mode == "SAVDHAN":
            self.rules = [
                SavdhanHeelContactRule(),
                SavdhanFootAngleRule(),
                SavdhanArmPositionRule(),
                KneeDistanceRule("close"),
                SavdhanHeadAlignmentRule(),
                SavdhanBackPostureRule(160, 210),
                SavdhanBodyPostureRule(160, 200),
                SavdhanShoulderLevelRule()
            ]
        elif self.mode == "VISHRAM":
            self.rules = [
                VishramSpacingRule(),
                VishramHandPositionRule(),
                KneeLockRule(),
                VishramHeadAlignmentRule(),
                VishramBackPostureRule(160, 210),
                VishramBodyPostureRule(160, 200),
                VishramShoulderLevelRule()
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
                GenericBackPostureRule(160, 210),
                GenericBodyPostureRule(160, 200),
                GenericShoulderLevelRule()
            ]
        elif self.mode == "BAYE_SALUTE":
            self.rules = [
                KneeDistanceRule("relaxed"),
                SaluteRightArmAngleRule(),
                StraightLeftArmAngleRule(),
                SaluteHandPositionRule(),
                HeadDirectionRule("left"),
                GenericBackPostureRule(160, 210),
                GenericBodyPostureRule(160, 200),
                GenericShoulderLevelRule()
            ]
        elif self.mode == "DAINE_SALUTE":
            self.rules = [
                KneeDistanceRule("relaxed"),
                SaluteRightArmAngleRule(),
                StraightLeftArmAngleRule(),
                SaluteHandPositionRule(),
                HeadDirectionRule("right"),
                GenericBackPostureRule(160, 210),
                GenericBodyPostureRule(160, 200),
                GenericShoulderLevelRule()
            ]
        elif self.mode == "DAHINE_MURH":
            self.rules = [
                DahineMurhRule(),
                GenericBackPostureRule(160, 210),
                GenericBodyPostureRule(160, 200),
                GenericShoulderLevelRule()
            ]
        elif self.mode == "BAYEN_MURH":
            self.rules = [
                BayenMurhRule(),
                GenericBackPostureRule(160, 210),
                GenericBodyPostureRule(160, 200),
                GenericShoulderLevelRule()
            ]
        elif self.mode == "PICHHE_MURH":
            self.rules = [
                PichheMurhRule(),
                GenericBackPostureRule(160, 210),
                GenericBodyPostureRule(160, 200),
                GenericShoulderLevelRule()
            ]
        elif self.mode == "KHULI_LINE_CHAL":
            self.rules = [
                KhuliLineChalRule(),
                GenericBackPostureRule(160, 210),
                GenericBodyPostureRule(160, 200),
                GenericShoulderLevelRule()
            ]
        elif self.mode == "NIKAT_LINE_CHAL":
            self.rules = [
                NikatLineChalRule(),
                GenericBackPostureRule(160, 210),
                GenericBodyPostureRule(160, 200),
                GenericShoulderLevelRule()
            ]
        elif self.mode == "SAJ":
            self.rules = [
                SajAlignmentRule(),
                GenericBackPostureRule(160, 210),
                GenericBodyPostureRule(160, 200),
                GenericShoulderLevelRule()
            ]
        elif self.mode == "VISARJAN":
            self.rules = [
                VisarjanSequence(),
                GenericBackPostureRule(160, 210),
                GenericBodyPostureRule(160, 200),
                GenericShoulderLevelRule()
            ]
        elif self.mode == "TEJ_CHAL":
            self.rules = [
                TejChalSequence(),
                GenericBackPostureRule(160, 210),
                GenericBodyPostureRule(160, 200),
                GenericShoulderLevelRule()
            ]
        elif self.mode == "THAAM":
            self.rules = [
                ThaamSequence(),
                GenericBackPostureRule(160, 210),
                GenericBodyPostureRule(160, 200),
                GenericShoulderLevelRule()
            ]
        elif self.mode == "MARCHING_FRONT_SALUTE":
            self.rules = [
                MarchingSaluteSequence("front"),
                GenericBackPostureRule(160, 210),
                GenericBodyPostureRule(160, 200),
                GenericShoulderLevelRule()
            ]
        elif self.mode == "MARCHING_BAYE_SALUTE":
            self.rules = [
                MarchingSaluteSequence("left"),
                GenericBackPostureRule(160, 210),
                GenericBodyPostureRule(160, 200),
                GenericShoulderLevelRule()
            ]
        elif self.mode == "MARCHING_DAINE_SALUTE":
            self.rules = [
                MarchingSaluteSequence("right"),
                GenericBackPostureRule(160, 210),
                GenericBodyPostureRule(160, 200),
                GenericShoulderLevelRule()
            ]
        elif self.mode == "MARCHING_TURN_DAHINE":
            self.rules = [
                MarchingTurnSequence("dahine"),
                GenericBackPostureRule(160, 210),
                GenericBodyPostureRule(160, 200),
                GenericShoulderLevelRule()
            ]
        elif self.mode == "MARCHING_TURN_BAYEN":
            self.rules = [
                MarchingTurnSequence("bayen"),
                GenericBackPostureRule(160, 210),
                GenericBodyPostureRule(160, 200),
                GenericShoulderLevelRule()
            ]
        elif self.mode == "MARCHING_TURN_PICHHE":
            self.rules = [
                MarchingTurnSequence("pichhe"),
                GenericBackPostureRule(160, 210),
                GenericBodyPostureRule(160, 200),
                GenericShoulderLevelRule()
            ]
        else:
            self.rules = []
            
        self.histories: dict[int, dict[str, list[float]]] = {}

    def evaluate(self, detection: PoseDetection, all_detections: list[PoseDetection] = None, camera_type: str = "front") -> CadetEvaluation:
        detection.posture_history = self.histories.setdefault(detection.track_id, {})
        
        results = []
        for rule in self.rules:
            kwargs = {"camera_type": camera_type}
            if hasattr(rule.evaluate, "__code__") and "all_detections" in rule.evaluate.__code__.co_varnames:
                kwargs["all_detections"] = all_detections
            results.append(rule.evaluate(detection, **kwargs))
                
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
