import numpy as np
from collections import deque
from backend.engine.foot_analyzer import FootGeometryAnalyzer
from backend.utils.smoothing import PoseSmoother

# Import rules at module level to ensure they are available in all methods
from backend.engine.analyzer import KneeStabilityRule, TorsoPostureRule, HeadAlignmentRule, StabilityRule
from backend.engine.intelligence import ShoulderSymmetryRule, BodySymmetryRule

class VishramFootSpacingRule:
    def __init__(self, foot_analyzer):
        self.foot_analyzer = foot_analyzer

    def evaluate(self, keypoints, frame=None, history=None):
        if frame is not None:
            geometry = self.foot_analyzer.analyze_geometry(frame, keypoints)
            if geometry:
                true_heel_dist = geometry.get("true_heel_dist", 0.0)
                scale = geometry.get("pose_scale", 1.0)
                toe_r = geometry.get("toe_r")
                toe_l = geometry.get("toe_l")
                
                # Calibrate pixels to inches using standard adult hip width (9.5 inches)
                scale_factor = 9.5 / (scale + 1e-6)
                heel_in = true_heel_dist * scale_factor
                
                toe_dist = 0.0
                if toe_r and toe_l:
                    toe_dist = abs(toe_l[0] - toe_r[0])
                toe_in = toe_dist * scale_factor
                
                # Strict scoring based on standard 12-inch and 18-inch limits
                heel_dev = abs(heel_in - 12.0)
                toe_dev = abs(toe_in - 18.0)
                
                score = max(0, 100 - (heel_dev * 6.0 + toe_dev * 4.0))
                
                msg = None
                if heel_in < 10.5: msg = "Foot spacing too narrow (target 12 in)"
                elif heel_in > 13.5: msg = "Foot spacing too wide (target 12 in)"
                elif toe_in < 16.0: msg = "Toes too narrow (target 18 in)"
                elif toe_in > 20.0: msg = "Toes too wide (target 18 in)"
                
                return round(score, 1), msg
                
        # Sensor fallback if no frame available
        l_ankle, r_ankle = keypoints[15], keypoints[16]
        l_hip, r_hip = keypoints[11], keypoints[12]
        hip_width = np.linalg.norm(l_hip[:2] - r_hip[:2])
        heel_dist = np.linalg.norm(l_ankle[:2] - r_ankle[:2])
        target_ratio = 1.3
        current_ratio = heel_dist / (hip_width + 1e-6)
        score = max(0, 100 - abs(current_ratio - target_ratio) * 100)
        
        msg = None
        if current_ratio < 1.0: msg = "Foot spacing too narrow (Vishram)"
        elif current_ratio > 1.8: msg = "Foot spacing too wide (Vishram)"
        
        return round(score, 1), msg

class VishramHandPlacementRule:
    def evaluate(self, keypoints, mask=None, frame=None, history=None):
        l_wrist, r_wrist = keypoints[9], keypoints[10]
        l_hip, r_hip = keypoints[11], keypoints[12]
        center_x = (l_hip[0] + r_hip[0]) / 2
        l_dist = abs(l_wrist[0] - center_x)
        r_dist = abs(r_wrist[0] - center_x)
        dist_score = max(0, 100 - (l_dist + r_dist) * 0.5)
        visual_score = 95.0 if mask is not None else 80.0
        score = (dist_score * 0.5) + (visual_score * 0.5)
        msg = "Rear hand placement deviation" if score < 75 else None
        return round(score, 1), msg

class VishramIntelligenceEngine:
    def __init__(self):
        self.foot_analyzer = FootGeometryAnalyzer()
        self.smoothers = {}
        self.rules = {
            "Foot Spacing": VishramFootSpacingRule(self.foot_analyzer),
            "Foot Symmetry": BodySymmetryRule(),
            "Knee Lock": KneeStabilityRule(),
            "Rear Hand Position": VishramHandPlacementRule(),
            "Balance Score": BodySymmetryRule(),
            "Torso Discipline": TorsoPostureRule(),
            "Shoulder Alignment": ShoulderSymmetryRule(),
            "Head Alignment": HeadAlignmentRule(),
            "Stability": StabilityRule()
        }
        self.cadet_histories = {}

    def analyze(self, cadet_id, keypoints, mask=None, frame=None, mode="VISHRAM"):
        if cadet_id not in self.smoothers:
            self.smoothers[cadet_id] = PoseSmoother()
        smoothed_kpts = self.smoothers[cadet_id].smooth(keypoints)
        
        if cadet_id not in self.cadet_histories:
            self.cadet_histories[cadet_id] = deque(maxlen=30)
        self.cadet_histories[cadet_id].append(smoothed_kpts[:, :2])
        
        scores = {}
        violations = []
        kp_conf = np.mean(keypoints[:, 2])
        
        for name, rule in self.rules.items():
            strictness = 1.0
            if mode == "AARAM_SE":
                if name in ["Torso Discipline", "Head Alignment", "Stability"]:
                    strictness = 0.5
            
            history = self.cadet_histories.get(cadet_id, deque(maxlen=30))
            
            try:
                if hasattr(rule, 'evaluate'):
                    # Fix: Ensure types are checked against module-level imports
                    if isinstance(rule, (VishramHandPlacementRule, ShoulderSymmetryRule)):
                        score, v = rule.evaluate(smoothed_kpts, mask, frame, history)
                    else:
                        score, v = rule.evaluate(smoothed_kpts, frame, history)
                else:
                    score, v = 90.0, None
            except:
                score, v = 50.0, f"Error: {name}"

            final_score = (score * strictness) + (100 * (1 - strictness))
            weighted_score = final_score * (0.9 + 0.1 * kp_conf)
            scores[name] = round(weighted_score, 1)
            if v:
                violations.append(v)
        
        overall = sum(scores.values()) / len(scores)
        
        # Extract visual foot geometry for spacing guidelines
        foot_geom = None
        if frame is not None:
            foot_geom = self.foot_analyzer.analyze_geometry(frame, smoothed_kpts)
            
        if overall >= 95: status = "EXCELLENT"
        elif overall >= 85: status = "GOOD"
        elif overall >= 70: status = "WARNING"
        else: status = "INCORRECT"
        
        return {
            'scores': scores,
            'overall': round(overall, 1),
            'status': status,
            'violations': list(dict.fromkeys(violations)),
            'smoothed_kpts': smoothed_kpts,
            'foot_geometry': foot_geom,
            'mode': mode
        }
