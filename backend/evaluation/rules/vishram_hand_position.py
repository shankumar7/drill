from backend.core.types import PoseDetection, RuleResult
from backend.evaluation.rules.base import EvaluationRule


class VishramHandPositionRule(EvaluationRule):
    name = "Hands behind back"

    def evaluate(self, detection: PoseDetection) -> RuleResult:
        k = detection.keypoints
        # Heuristic: If wrists (indices 9 and 10) are hidden/low confidence, assume they are behind the back.
        # From a front camera, wrists may still be partially visible when hands are behind the back,
        # so we use a more lenient approach:
        # 1. Both wrists low confidence (< 0.4) = clearly behind back
        # 2. One wrist low confidence = likely behind back  
        # 3. Both wrists visible but below/behind the hips = possibly behind back
        
        lw_conf = k[9, 2]
        rw_conf = k[10, 2]
        
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
            shoulder_width = np.linalg.norm(k[5, :2] - k[6, :2])
            wrists_close = wrist_dist < shoulder_width * 0.5 if shoulder_width > 10 else False
            
            if wrists_low and wrists_close:
                score = 75.0
            elif wrists_low:
                score = 55.0
            else:
                score = 30.0
        
        status = "pass" if score >= 70 else "fail"
        
        return RuleResult(
            self.name,
            status,
            round(score, 1),
            "Wrists should be clasped behind the back (left below, right above).",
        )
