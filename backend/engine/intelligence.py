import numpy as np
from collections import deque
from backend.engine.foot_analyzer import FootGeometryAnalyzer
from backend.utils.smoothing import PoseSmoother

class SavdhanRule:
    def evaluate(self, keypoints, mask=None, frame=None, history=None):
        raise NotImplementedError

class ArmBodyIntelligenceRule(SavdhanRule):
    def evaluate(self, keypoints, mask=None, frame=None, history=None):
        # RULE 4 & 6: Arm Alignment & Trouser Seams
        l_shoulder, l_elbow, l_wrist = keypoints[5], keypoints[7], keypoints[9]
        r_shoulder, r_elbow, r_wrist = keypoints[6], keypoints[8], keypoints[10]
        
        # 1. Straightness (Elbow lock)
        def get_angle(a, b, c):
            ba = a - b
            bc = c - b
            return np.degrees(np.arccos(np.clip(np.dot(ba, bc)/(np.linalg.norm(ba)*np.linalg.norm(bc)+1e-6), -1, 1)))

        l_angle = get_angle(l_shoulder[:2], l_elbow[:2], l_wrist[:2])
        r_angle = get_angle(r_shoulder[:2], r_elbow[:2], r_wrist[:2])
        straight_score = (max(0, 100 - abs(180 - l_angle)*3) + max(0, 100 - abs(180 - r_angle)*3)) / 2
        
        # 2. Silhouette Alignment (Flush with body)
        if mask is not None:
            # Placeholder for mask-based proximity check
            # In production, we'd check if wrist-torso pixels are contiguous
            mask_score = 98.0 
        else:
            mask_score = 75.0 
            
        overall = (straight_score * 0.4) + (mask_score * 0.6)
        msg = None
        if overall < 70: msg = "Visible arm alignment drift"
        elif overall < 85: msg = "Minor arm alignment deviation"
        
        return round(overall, 1), msg

class ShoulderSymmetryRule(SavdhanRule):
    def evaluate(self, keypoints, mask=None, frame=None, history=None):
        # RULE 7 & 11: Shoulder Alignment
        l_sh, r_sh = keypoints[5], keypoints[6]
        
        # 1. Height Symmetry (Shoulders must be level)
        height_diff = abs(l_sh[1] - r_sh[1])
        shoulder_width = np.linalg.norm(l_sh[:2] - r_sh[:2])
        height_score = max(0, 100 - (height_diff / (shoulder_width + 1e-6)) * 500)
        
        # 2. Center Symmetry (Shoulders centered over hips)
        l_hip, r_hip = keypoints[11], keypoints[12]
        center_sh = (l_sh[0] + r_sh[0]) / 2
        center_hip = (l_hip[0] + r_hip[0]) / 2
        alignment_score = max(0, 100 - abs(center_sh - center_hip) * 2)
        
        overall = (height_score + alignment_score) / 2
        msg = None
        if height_score < 80: msg = "Shoulder height asymmetry"
        elif alignment_score < 85: msg = "Torso alignment deviation"
        
        return round(overall, 1), msg

class BodySymmetryRule(SavdhanRule):
    def evaluate(self, keypoints, mask=None, frame=None, history=None):
        # RULE 10: Balanced Posture
        l_side = [5, 7, 9, 11, 13, 15]
        r_side = [6, 8, 10, 12, 14, 16]
        
        center_x = (keypoints[11][0] + keypoints[12][0]) / 2
        l_dist = np.mean([abs(keypoints[i][0] - center_x) for i in l_side])
        r_dist = np.mean([abs(keypoints[i][0] - center_x) for i in r_side])
        
        symmetry_diff = abs(l_dist - r_dist)
        score = max(0, 100 - symmetry_diff * 5)
        
        msg = "Minor posture asymmetry" if score < 85 else None
        return round(score, 1), msg

class SavdhanIntelligenceEngine:
    def __init__(self):
        self.foot_analyzer = FootGeometryAnalyzer()
        self.smoothers = {} # ID -> PoseSmoother
        
        # Official Military Rulebook
        from backend.engine.analyzer import HeelAlignmentRule, FootAngleRule, KneeStabilityRule, TorsoPostureRule, HeadAlignmentRule, StabilityRule
        self.rules = {
            "Heel Alignment": HeelAlignmentRule(self.foot_analyzer), # RULE 1
            "Foot Angle": FootAngleRule(self.foot_analyzer),        # RULE 2
            "Knee Lock": KneeStabilityRule(),                       # RULE 3
            "Arm Alignment": ArmBodyIntelligenceRule(),             # RULE 4, 5, 6, 7
            "Torso Posture": TorsoPostureRule(),                    # RULE 9, 10, 11
            "Shoulder Alignment": ShoulderSymmetryRule(),           # RULE 11
            "Head Alignment": HeadAlignmentRule(),                  # RULE 12, 13, 14
            "Stability": StabilityRule(),                           # RULE 15, 16
            "Symmetry": BodySymmetryRule()                          # RULE 10, 4
        }
        self.cadet_histories = {}

    def analyze(self, cadet_id, keypoints, mask=None, frame=None):
        # 1. Temporal Smoothing (MANDATORY)
        if cadet_id not in self.smoothers:
            self.smoothers[cadet_id] = PoseSmoother()
        smoothed_kpts = self.smoothers[cadet_id].smooth(keypoints)
        
        # 2. Update History for Stability Analysis
        if cadet_id not in self.cadet_histories:
            self.cadet_histories[cadet_id] = deque(maxlen=30)
        self.cadet_histories[cadet_id].append(smoothed_kpts[:, :2])
        
        # 3. Confidence-Aware Rule Evaluation
        scores = {}
        violations = []
        kp_conf = np.mean(keypoints[:, 2]) # Global pose confidence
        
        for name, rule in self.rules.items():
            history = self.cadet_histories[cadet_id] if name == "Stability" else None
            
            try:
                # Dispatch to appropriate evaluation method
                if isinstance(rule, (ArmBodyIntelligenceRule, ShoulderSymmetryRule, BodySymmetryRule)):
                    score, v = rule.evaluate(smoothed_kpts, mask, frame, history)
                else:
                    score, v = rule.evaluate(smoothed_kpts, frame, history)
            except Exception as e:
                score, v = 50.0, f"Analysis Error: {name}"

            # Apply Confidence Logic: Uncertainty reduces score slightly but doesn't cause failure
            weighted_score = score * (0.9 + 0.1 * kp_conf)
            scores[name] = round(weighted_score, 1)
            if v:
                violations.append(v)
        
        # 4. Final Scoring & Status Classification
        overall = sum(scores.values()) / len(scores)
        
        # Extract foot geometry for visual overlays
        foot_geom = None
        if frame is not None:
            foot_geom = self.foot_analyzer.analyze_geometry(frame, smoothed_kpts)
            
        # OFFICIAL CLASSIFICATION
        if overall >= 95: status = "EXCELLENT"
        elif overall >= 85: status = "GOOD"
        elif overall >= 70: status = "WARNING"
        else: status = "INCORRECT"
        
        return {
            'scores': scores,
            'overall': round(overall, 1),
            'status': status,
            'violations': list(dict.fromkeys(violations)), # De-duplicate
            'smoothed_kpts': smoothed_kpts,
            'foot_geometry': foot_geom,
            'mode': 'SAVDHAN'
        }
