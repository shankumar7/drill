from backend.core.types import PoseDetection, RuleResult
from backend.evaluation.geometry import segment_length
from backend.evaluation.rules.base import EvaluationRule

class SaluteHandPositionRule(EvaluationRule):
    name = "Saluting Hand Position"

    def evaluate(self, detection: PoseDetection) -> RuleResult:
        k = detection.keypoints
        # Try right wrist to right eye, then left wrist to left eye (handles mirrored feed)
        # Right: Wrist (10), Eye (2), Shoulders (5, 6)
        # Left:  Wrist (9),  Eye (1), Shoulders (5, 6)
        
        right_ok = min(k[10, 2], k[2, 2]) >= 0.3
        left_ok = min(k[9, 2], k[1, 2]) >= 0.3
        
        if not right_ok and not left_ok:
            return RuleResult(self.name, "not_evaluable", None, "Hand or eye keypoints not reliable.")
        
        shoulder_width = segment_length(k[5, :2], k[6, :2])
        if shoulder_width < 10:
            return RuleResult(self.name, "not_evaluable", None, "Shoulder width too small")
        
        # Pick the arm whose wrist is closer to the corresponding eye (more likely saluting)
        best_norm_dist = float('inf')
        
        if right_ok:
            r_wrist = k[10, :2]
            r_eye = k[2, :2]
            dist_r = segment_length(r_wrist, r_eye) / shoulder_width
            best_norm_dist = min(best_norm_dist, dist_r)
            
        if left_ok:
            l_wrist = k[9, :2]
            l_eye = k[1, :2]
            dist_l = segment_length(l_wrist, l_eye) / shoulder_width
            best_norm_dist = min(best_norm_dist, dist_l)
        
        norm_dist = best_norm_dist
        
        # When saluting, wrist is near the eyebrow.
        # Widened threshold: < 0.5 * shoulder_width is ideal (was 0.35)
        score = 0.0
        if norm_dist <= 0.5:
            score = 100.0
        elif norm_dist < 0.8:
            score = 100.0 - ((norm_dist - 0.5) * 333)
            
        score = max(0.0, score)
        
        smoothed = self.smooth_score(detection, score)
        if isinstance(smoothed, RuleResult):
            return smoothed
            
        status = "pass" if smoothed >= 80 else "fail"
        return RuleResult(self.name, status, round(smoothed, 1), f"Wrist-Eye Distance: {norm_dist:.2f} (Ideal: < 0.5)")
