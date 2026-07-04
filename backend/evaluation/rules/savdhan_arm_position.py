from backend.core.types import PoseDetection, RuleResult
from backend.evaluation.geometry import segment_length, angle_degrees
from backend.evaluation.rules.base import EvaluationRule

class SavdhanArmPositionRule(EvaluationRule):
    name = "Arms at sides"

    def evaluate(self, detection: PoseDetection) -> RuleResult:
        k = detection.keypoints
        # Shoulders (5, 6), Elbows (7, 8), Wrists (9, 10), Hips (11, 12)
        l_visible = min(k[5, 2], k[7, 2], k[9, 2], k[11, 2]) >= 0.25
        r_visible = min(k[6, 2], k[8, 2], k[10, 2], k[12, 2]) >= 0.25
        
        if not (l_visible or r_visible):
            return RuleResult(self.name, "not_evaluable", None, "Arm or hip keypoints are not reliable.")

        geometry = detection.foot_geometry or {}
        spine_length = geometry.get("spine_length", 100)
        
        if spine_length < 20 or spine_length == 100:
            return RuleResult(self.name, "not_evaluable", None, "Spine length too small or unreliable for scaling.")

        def evaluate_arm(shoulder, elbow, wrist, hip):
            # 1. Arm must be straight (elbow angle near 180)
            elbow_angle = angle_degrees(shoulder[:2], elbow[:2], wrist[:2])
            
            # 2. Wrist must be strictly below the hip (Y axis increases downwards)
            # In Vishram (hands behind back), the wrist is lifted up to hip level.
            # In Savdhan, hands hang straight down by the seams.
            y_drop = (wrist[1] - hip[1]) / spine_length
            
            score = 100.0
            
            # Penalize bent elbows (in Vishram, arms are bent behind back)
            if elbow_angle < 150:
                score -= (150 - elbow_angle) * 2.0
                
            # Penalize if wrists are lifted too high (not hanging down)
            if y_drop < 0.15:
                score -= (0.15 - y_drop) * 500.0
                
            # Penalize if wrists are too far horizontally from hips (not pinned to side)
            x_dist = abs(wrist[0] - hip[0]) / spine_length
            if x_dist > 0.35:
                score -= (x_dist - 0.35) * 200.0
                
            return max(0.0, min(100.0, score)), elbow_angle, y_drop

        scores = []
        msg_parts = []
        if l_visible:
            s, ang, drop = evaluate_arm(k[5], k[7], k[9], k[11])
            scores.append(s)
            msg_parts.append(f"L(ang:{ang:.0f}°, drop:{drop:.2f})")
            
        if r_visible:
            s, ang, drop = evaluate_arm(k[6], k[8], k[10], k[12])
            scores.append(s)
            msg_parts.append(f"R(ang:{ang:.0f}°, drop:{drop:.2f})")
            
        score = min(scores) # Take the worst visible arm

        history = detection.posture_history.setdefault(self.name, []) if detection.posture_history is not None else []
        history.append(score)
        del history[:-10]
        if len(history) < 5:
            return RuleResult(self.name, "not_evaluable", None, "Collecting stable arm-position evidence.")
            
        stable_score = sum(history) / len(history)
        status = "pass" if stable_score >= 90 else "fail"
        return RuleResult(self.name, status, round(stable_score, 1), f"Arm straightness: {', '.join(msg_parts)}")
