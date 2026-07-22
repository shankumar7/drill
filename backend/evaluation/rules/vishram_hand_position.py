from backend.core.types import PoseDetection, RuleResult
from backend.evaluation.rules.base import EvaluationRule


class VishramHandPositionRule(EvaluationRule):
    name = "Hands behind back"

    def evaluate(self, detection: PoseDetection, camera_type: str = "front", **kwargs) -> RuleResult:
        if camera_type not in ["front", "back", "side"]:
            return RuleResult(self.name, "not_evaluable", None, "Requires front, back, or side camera view.")
            
        k = detection.keypoints
        lw_conf = k[9, 2]
        rw_conf = k[10, 2]
        
        if camera_type == "side":
            # For side camera, check if wrists are spatially behind the hips based on facing direction
            nose_x = k[0, 0]
            ear_x = k[3, 0] if k[3, 2] > k[4, 2] else k[4, 0]
            
            if k[0, 2] < 0.25 or (k[3, 2] < 0.25 and k[4, 2] < 0.25):
                return RuleResult(self.name, "not_evaluable", None, "Head orientation not clear.")
                
            facing_right = nose_x > ear_x  # If nose X > ear X, looking right
            hip_x = (k[11, 0] + k[12, 0]) / 2
            
            if lw_conf < 0.3 and rw_conf < 0.3:
                return RuleResult(self.name, "pass", 100.0, "Wrists occluded behind torso in side view (correct).")
                
            wrist_x = k[9, 0] if lw_conf > rw_conf else k[10, 0]
            tolerance = 15
            
            if facing_right:
                hands_behind = wrist_x < (hip_x - tolerance)
            else:
                hands_behind = wrist_x > (hip_x + tolerance)
                
            if hands_behind:
                return RuleResult(self.name, "pass", 100.0, "Hands are properly placed behind the back.")
            else:
                return RuleResult(self.name, "fail", 0.0, "Hands should be placed behind the back.")

        both_hidden = lw_conf < 0.4 and rw_conf < 0.4
        one_hidden = lw_conf < 0.4 or rw_conf < 0.4
        
        geometry = detection.foot_geometry or {}
        spine_length = geometry.get("spine_length", 100)
        if spine_length < 20 or spine_length == 100:
            spine_length = 100
            
        hip_y = (k[11, 1] + k[12, 1]) / 2
        
        msg = "Wrists should be clasped behind the back (left below, right above)."
        
        if both_hidden:
            score = 100.0
            msg = "Hands correctly clasped behind back (left hand below, right hand on top)."
        elif one_hidden:
            visible_wrist_y = k[9, 1] if rw_conf < 0.4 else k[10, 1]
            hanging = visible_wrist_y > hip_y + 0.25 * spine_length
            too_high = visible_wrist_y < hip_y - 0.2 * spine_length
            
            if hanging:
                score = 0.0
                msg = "Hand is hanging by the side! Clasp behind back (left hand below, right hand on top)."
            elif too_high:
                score = 0.0
                msg = "Hand is too high. Clasp behind back."
            else:
                score = 100.0
                msg = "Hands correctly clasped behind back (left hand below, right hand on top)."
        else:
            l_wrist_y, r_wrist_y = k[9, 1], k[10, 1]
            
            hanging_l = l_wrist_y > hip_y + 0.25 * spine_length
            hanging_r = r_wrist_y > hip_y + 0.25 * spine_length
            too_high_l = l_wrist_y < hip_y - 0.2 * spine_length
            too_high_r = r_wrist_y < hip_y - 0.2 * spine_length
            
            if hanging_l or hanging_r:
                score = 0.0
                msg = "Hands are hanging by the sides! Clasp behind back."
            elif too_high_l or too_high_r:
                score = 0.0
                msg = "Hands are too high. Clasp behind back."
            else:
                import numpy as np
                wrist_dist = np.linalg.norm(k[9, :2] - k[10, :2])
                
                if wrist_dist < 0.8 * spine_length:
                    score = 100.0
                    msg = "Hands correctly clasped behind back (left hand below, right hand on top)."
                else:
                    score = 0.0
                    msg = "Hands are too far apart."

        # Smooth the score
        history = detection.posture_history.setdefault(self.name, []) if detection.posture_history is not None else []
        history.append(score)
        del history[:-10]
        
        stable_score = sum(history) / len(history) if history else score
        status = "pass" if stable_score >= 80 else "fail"
        
        return RuleResult(self.name, status, round(stable_score, 1), msg)