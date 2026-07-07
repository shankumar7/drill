from backend.core.types import PoseDetection, RuleResult
from backend.evaluation.rules.base import EvaluationRule


class SavdhanFootAngleRule(EvaluationRule):
    name = "Foot angle"

    def evaluate(self, detection: PoseDetection, camera_type: str = "front", **kwargs) -> RuleResult:
        if camera_type not in ["front", "back"]:
            return RuleResult(self.name, "not_evaluable", None, "Requires front or back camera view.")

        geometry = detection.foot_geometry
        if not geometry:
            return RuleResult(self.name, "not_evaluable", None, "Foot geometry is unavailable.")
            
        heel_gap = geometry.get("true_heel_dist")
        toe_gap = geometry.get("true_toe_dist")
        spine = geometry.get("spine_length")
        
        if heel_gap is None or toe_gap is None or spine in (None, 0, 100):
            # If spine is 100, it's the fallback which means it's not reliable
            if spine == 100:
                return RuleResult(self.name, "not_evaluable", None, "Spine length not reliable for scaling.")
            return RuleResult(self.name, "not_evaluable", None, "Heel/Toe geometry not reliable.")
            
        v_diff = (toe_gap - heel_gap) / spine
        
        score = 100.0
        if toe_gap > heel_gap + 1.0: 
            if v_diff < 0.05: 
                score = max(0.0, 100.0 - (0.05 - v_diff) * 1000.0)
            elif v_diff > 0.3: 
                score = max(0.0, 100.0 - (v_diff - 0.3) * 300.0)
        else:
            score = 100.0
            
        status = "pass" if score >= 90 else "fail"
        msg = f"V-shape toe-heel difference ratio: {v_diff:.2f}." if toe_gap > heel_gap + 1.0 else "Toe keypoints missing; assuming default 30° alignment."
        return RuleResult(self.name, status, round(score, 1), msg)
