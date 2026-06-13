from backend.core.types import PoseDetection, RuleResult
from backend.evaluation.geometry import segment_length
from backend.evaluation.rules.base import EvaluationRule

class SavdhanArmPositionRule(EvaluationRule):
    name = "Arms at sides"

    def evaluate(self, detection: PoseDetection) -> RuleResult:
        k = detection.keypoints
        # Wrist (9, 10) and Hip (11, 12)
        if min(k[9, 2], k[10, 2], k[11, 2], k[12, 2]) < 0.25:
            return RuleResult(self.name, "not_evaluable", None, "Wrist or hip keypoints are not reliable enough.")

        l_wrist_hip_dist = segment_length(k[9, :2], k[11, :2])
        r_wrist_hip_dist = segment_length(k[10, :2], k[12, :2])
        shoulder_width = segment_length(k[5, :2], k[6, :2])

        if shoulder_width < 10:
            return RuleResult(self.name, "not_evaluable", None, "Shoulder width too small for scaling.")

        # In original code, ideal distance was 19 to 55 pixels for 1100x1100 image.
        # This roughly translates to 0.1 to 0.5 times the shoulder width.
        # We will normalize by shoulder width.
        norm_l = l_wrist_hip_dist / shoulder_width
        norm_r = r_wrist_hip_dist / shoulder_width
        
        def calculate_score(norm):
            if 0.25 <= norm <= 0.55:
                return 100.0
            elif 0.55 < norm <= 0.8:
                return max(0.0, 100.0 - ((norm - 0.55) * 400.0))
            elif 0.05 <= norm < 0.25:
                return max(0.0, 100.0 - ((0.25 - norm) * 500.0))
            return 0.0
            
        score_l = calculate_score(norm_l)
        score_r = calculate_score(norm_r)
        score = min(score_l, score_r)

        history = detection.posture_history.setdefault(self.name, []) if detection.posture_history is not None else []
        history.append(score)
        del history[:-10]
        if len(history) < 5:
            return RuleResult(self.name, "not_evaluable", None, "Collecting stable arm-position evidence.")
            
        stable_score = sum(history) / len(history)
        status = "pass" if stable_score >= 80 else "fail"
        return RuleResult(self.name, status, round(stable_score, 1), f"Arm-Hip Distance (normalized): L={norm_l:.2f}, R={norm_r:.2f}")
