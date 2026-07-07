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
            # Nose = 0, L Ear = 3, R Ear = 4
            nose_x = k[0, 0]
            ear_x = k[3, 0] if k[3, 2] > k[4, 2] else k[4, 0]
            
            if k[0, 2] < 0.25 or (k[3, 2] < 0.25 and k[4, 2] < 0.25):
                return RuleResult(self.name, "not_evaluable", None, "Head orientation not clear.")
                
            facing_right = nose_x > ear_x  # If nose X > ear X, looking right
            
            hip_x = (k[11, 0] + k[12, 0]) / 2
            
            # Identify the most reliable wrist
            if lw_conf < 0.3 and rw_conf < 0.3:
                return RuleResult(self.name, "not_evaluable", None, "Wrists not visible.")
                
            wrist_x = k[9, 0] if lw_conf > rw_conf else k[10, 0]
            
            # Tolerance in pixels
            tolerance = 15
            
            if facing_right:
                # Body is looking right. Back is to the left (smaller X). Wrists should be left of hips.
                hands_behind = wrist_x < (hip_x - tolerance)
            else:
                # Body is looking left. Back is to the right (larger X). Wrists should be right of hips.
                hands_behind = wrist_x > (hip_x + tolerance)
                
            if hands_behind:
                score = 100.0
                msg = "Hands are properly placed behind the back."
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
            msg = "Hands correctly placed behind back."
        elif one_hidden:
            visible_wrist_y = k[9, 1] if rw_conf < 0.4 else k[10, 1]
            hanging = visible_wrist_y > hip_y + 0.25 * spine_length
            too_high = visible_wrist_y < hip_y - 0.2 * spine_length
            
            if hanging:
                score = -100.0
                msg = "Hand is hanging by the side! Clasp behind back."
            elif too_high:
                score = -100.0
                msg = "Hand is too high. Clasp behind back."
            else:
                score = 100.0
                msg = "Hands correctly placed behind back."
        else:
            l_wrist_y, r_wrist_y = k[9, 1], k[10, 1]
            
            hanging_l = l_wrist_y > hip_y + 0.25 * spine_length
            hanging_r = r_wrist_y > hip_y + 0.25 * spine_length
            too_high_l = l_wrist_y < hip_y - 0.2 * spine_length
            too_high_r = r_wrist_y < hip_y - 0.2 * spine_length
            
            if hanging_l or hanging_r:
                score = -100.0
                msg = "Hands are hanging by the sides! Clasp behind back."
            elif too_high_l or too_high_r:
                score = -100.0
                msg = "Hands are too high. Clasp behind back."
            else:
                import numpy as np
                wrist_dist = np.linalg.norm(k[9, :2] - k[10, :2])
                
                # If they are near the hips (vertically) and not wider than the shoulders,
                # they are clasped behind the back (even if YOLO draws them at the hip edges).
                if wrist_dist < 0.8 * spine_length:
                    score = 100.0
                    msg = "Hands correctly placed behind back."
                else:
                    score = -100.0
                    msg = "Hands are too far apart."

        # Smooth the score
        history = detection.posture_history.setdefault(self.name, []) if detection.posture_history is not None else []
        history.append(score)
        del history[:-10]
        
        if len(history) < 5:
            return RuleResult(self.name, "not_evaluable", None, "Collecting hand position data.")
            
        stable_score = sum(history) / len(history)
        status = "pass" if stable_score >= 90 else "fail"
        
        return RuleResult(self.name, status, round(stable_score, 1), msg)