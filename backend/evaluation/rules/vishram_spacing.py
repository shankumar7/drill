from backend.core.types import PoseDetection, RuleResult
from backend.evaluation.geometry import segment_length
from backend.evaluation.rules.base import EvaluationRule


class VishramSpacingRule(EvaluationRule):
    """Official Rule: Vishram position requires 12-inch heel-to-heel and 18-inch toe-to-toe spacing.
    
    From the Drill Précis: "erhi to erhi 12 inch, panja to panja 18 inch ka fasla"
    """
    name = "Foot spacing"

    def evaluate(self, detection: PoseDetection) -> RuleResult:
        k = detection.keypoints
        geometry = detection.foot_geometry or {}
        heel_spacing = geometry.get("heel_to_heel_in")
        toe_spacing = geometry.get("toe_to_toe_in")
        
        if heel_spacing is None or toe_spacing is None:
            # Fallback: use ankle keypoints relative to shoulder width as a rough proxy
            if min(k[15, 2], k[16, 2]) < 0.3:
                return RuleResult(
                    self.name,
                    "not_evaluable",
                    None,
                    "Ankle keypoints not visible. Cannot measure foot spacing.",
                )
            
            ankle_dist = segment_length(k[15, :2], k[16, :2])
            shoulder_width = segment_length(k[5, :2], k[6, :2])
            
            if shoulder_width < 10:
                return RuleResult(self.name, "not_evaluable", None, "Shoulder width too small for scaling.")
            
            # In Vishram, feet should be roughly shoulder-width apart (12 inches heel, ~16 inch shoulders)
            # So ankle distance should be ~0.75 * shoulder width
            norm_dist = ankle_dist / shoulder_width
            
            # Ideal normalized ankle distance for vishram: 0.5 to 1.0 (roughly shoulder-width)
            score = 0.0
            if 0.5 <= norm_dist <= 1.0:
                score = 100.0
            elif 0.3 <= norm_dist < 0.5:
                score = max(0.0, 100.0 - (0.5 - norm_dist) * 500)
            elif 1.0 < norm_dist <= 1.3:
                score = max(0.0, 100.0 - (norm_dist - 1.0) * 333)
            
            smoothed = self.smooth_score(detection, score)
            if isinstance(smoothed, RuleResult):
                return smoothed
            
            status = "pass" if smoothed >= 80 else "fail"
            return RuleResult(
                self.name,
                status,
                round(smoothed, 1),
                f"Ankle spread ratio: {norm_dist:.2f} (Ideal: 0.5-1.0). Official: 12in heels, 18in toes.",
            )
        
        # If calibrated geometry is available, use exact measurements
        # Official: 12 inches heel-to-heel, 18 inches toe-to-toe
        heel_error = abs(heel_spacing - 12.0)
        toe_error = abs(toe_spacing - 18.0)
        score = max(0.0, 100.0 - heel_error * 6.0 - toe_error * 4.0)
        status = "pass" if heel_error <= 2.0 and toe_error <= 3.0 else "fail"
        return RuleResult(
            self.name,
            status,
            round(score, 1),
            f"Heels {heel_spacing:.1f}in (target: 12in), toes {toe_spacing:.1f}in (target: 18in).",
        )
