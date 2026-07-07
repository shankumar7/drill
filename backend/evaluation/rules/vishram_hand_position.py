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
            else:
                score = 30.0
                msg = "Hands are not placed behind the back."
                
            smoothed = self.smooth_score(detection, score)
            if isinstance(smoothed, RuleResult): return smoothed
            return RuleResult(self.name, "pass" if smoothed >= 75 else "fail", round(smoothed, 1), msg)

        # FRONT / BACK CAMERA LOGIC
        # Heuristic: If wrists (indices 9 and 10) are hidden/low confidence, assume they are behind the back.
        # From a front camera, wrists may still be partially visible when hands are behind the back,
        # so we use a more lenient approach:
        # 1. Both wrists low confidence (< 0.4) = clearly behind back
        # 2. One wrist low confidence = likely behind back  
        # 3. Both wrists visible but below/behind the hips = possibly behind back
        
        both_hidden = lw_conf < 0.4 and rw_conf < 0.4
        one_hidden = lw_conf < 0.4 or rw_conf < 0.4
        
        if both_hidden:
            score = 100.0
        elif one_hidden:
            # One wrist hidden, check if the visible one is near/behind the hip
            visible_wrist_y = k[9, 1] if rw_conf < 0.4 else k[10, 1]
            hip_y = (k[11, 1] + k[12, 1]) / 2  # Average hip y position
            
            # If wrist is near hip level or below (within tolerance), likely behind back
            if visible_wrist_y >= hip_y - 20:  # Allow some tolerance above hips
                score = 85.0
            else:
                score = 50.0
        else:
            # Both wrists visible — check if they're positioned behind the torso
            # If both wrists are near/below hip level and close together, possibly behind back
            l_wrist_y, r_wrist_y = k[9, 1], k[10, 1]
            hip_y = (k[11, 1] + k[12, 1]) / 2
            
            wrists_low = l_wrist_y >= hip_y - 20 and r_wrist_y >= hip_y - 20
            
            # Check if wrists are close together (behind back position)
            import numpy as np
            wrist_dist = np.linalg.norm(k[9, :2] - k[10, :2])
            
            geometry = detection.foot_geometry or {}
            spine_length = geometry.get("spine_length", 100)
            
            # Use spine_length. Spine is ~25% longer than shoulders, so adjust ratio from 0.5 to 0.4
            wrists_close = wrist_dist < spine_length * 0.4 if spine_length >= 20 and spine_length != 100 else False
            
            if wrists_low and wrists_close:
                score = 75.0
            elif wrists_low:
                score = 55.0
            else:
                score = 20.0

        
        status = "pass" if score >= 90 else "fail"
        
        return RuleResult(
            self.name,
            status,
            round(score, 1),
            "Wrists should be clasped behind the back (left below, right above).",
        )
