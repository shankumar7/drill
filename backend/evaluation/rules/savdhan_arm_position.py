from backend.core.types import PoseDetection, RuleResult
from backend.evaluation.geometry import segment_length
from backend.evaluation.rules.base import EvaluationRule

class SavdhanArmPositionRule(EvaluationRule):
    name = "Arms at sides"

    def evaluate(self, detection: PoseDetection) -> RuleResult:
        k = detection.keypoints
        # Wrist (9, 10) and Hip (11, 12)
        l_visible = min(k[9, 2], k[11, 2]) >= 0.25
        r_visible = min(k[10, 2], k[12, 2]) >= 0.25
        
        if not (l_visible or r_visible):
            return RuleResult(self.name, "not_evaluable", None, "Wrist or hip keypoints are not reliable on either side.")

        # We must use spine length for scaling, because shoulder width collapses on a side profile
        geometry = detection.foot_geometry or {}
        spine_length = geometry.get("spine_length", 100)
        
        if spine_length < 20 or spine_length == 100:
            return RuleResult(self.name, "not_evaluable", None, "Spine length too small or unreliable for scaling.")

        def calculate_score(norm):
            # With spine scaling, the distance from wrist to hip is quite small since spine is long
            if 0.1 <= norm <= 0.35:
                return 100.0
            elif 0.35 < norm <= 0.6:
                return max(0.0, 100.0 - ((norm - 0.35) * 400.0))
            elif norm < 0.1:
                return max(0.0, 100.0 - ((0.1 - norm) * 800.0))
            return 0.0

        scores = []
        msg_parts = []
        if l_visible:
            l_dist = segment_length(k[9, :2], k[11, :2])
            norm_l = l_dist / spine_length
            scores.append(calculate_score(norm_l))
            msg_parts.append(f"L={norm_l:.2f}")
            
        if r_visible:
            r_dist = segment_length(k[10, :2], k[12, :2])
            norm_r = r_dist / spine_length
            scores.append(calculate_score(norm_r))
            msg_parts.append(f"R={norm_r:.2f}")
            
        score = min(scores) # Take the worst visible arm

        history = detection.posture_history.setdefault(self.name, []) if detection.posture_history is not None else []
        history.append(score)
        del history[:-10]
        if len(history) < 5:
            return RuleResult(self.name, "not_evaluable", None, "Collecting stable arm-position evidence.")
            
        stable_score = sum(history) / len(history)
        status = "pass" if stable_score >= 80 else "fail"
        return RuleResult(self.name, status, round(stable_score, 1), f"Arm-Hip Distance (normalized): {', '.join(msg_parts)}")
