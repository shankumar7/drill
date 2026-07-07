from backend.core.types import PoseDetection, RuleResult

class SajAlignmentRule:
    def __init__(self):
        self.name = "Squad Alignment (Saj)"

    def evaluate(self, detection: PoseDetection, camera_type: str = "front", all_detections: list[PoseDetection] = None, **kwargs) -> RuleResult:
        if camera_type != "side":
            return RuleResult(self.name, "not_evaluable", None, "Requires side camera view.")

        if not all_detections or len(all_detections) < 2:
            return RuleResult(self.name, "not_evaluable", None, "Need at least 2 cadets")

        # Get the y-coordinates of the shoulders or feet of all cadets
        # We'll use the mid-point of the shoulders for alignment checking
        shoulder_y_coords = []
        for det in all_detections:
            l_shoulder = det.keypoints[5]
            r_shoulder = det.keypoints[6]
            if l_shoulder[2] > 0.4 and r_shoulder[2] > 0.4:
                mid_y = (l_shoulder[1] + r_shoulder[1]) / 2.0
                shoulder_y_coords.append(mid_y)

        if len(shoulder_y_coords) < 2:
            return RuleResult(self.name, None, "not_evaluable", "Shoulders not visible on enough cadets")

        # Calculate the variance or max difference in Y coordinates
        y_min = min(shoulder_y_coords)
        y_max = max(shoulder_y_coords)
        diff_px = y_max - y_min

        # Normalize by the current cadet's spine length to get scale-invariant threshold
        l_shoulder = detection.keypoints[5]
        r_shoulder = detection.keypoints[6]
        l_hip = detection.keypoints[11]
        r_hip = detection.keypoints[12]
        
        spine_length = 100
        if l_shoulder[2] > 0.4 and r_shoulder[2] > 0.4 and l_hip[2] > 0.4 and r_hip[2] > 0.4:
            mid_shoulder_y = (l_shoulder[1] + r_shoulder[1]) / 2.0
            mid_hip_y = (l_hip[1] + r_hip[1]) / 2.0
            spine_length = abs(mid_hip_y - mid_shoulder_y)
            if spine_length < 10:
                spine_length = 100

        normalized_diff = diff_px / spine_length

        # If they are within 15% of a spine length vertically from each other, they are perfectly aligned
        if normalized_diff < 0.15:
            return RuleResult(self.name, 100, "pass", "Squad is perfectly aligned")
        elif normalized_diff < 0.30:
            score = 100 - ((normalized_diff - 0.15) * 200)
            return RuleResult(self.name, score, "partial_pass", "Slight misalignment in squad")
        else:
            score = max(0, 70 - ((normalized_diff - 0.30) * 100))
            return RuleResult(self.name, score, "fail", "Squad is out of alignment")
