import numpy as np
from collections import deque
from backend.engine.foot_analyzer import FootGeometryAnalyzer

class SavdhanRule:
    def evaluate(self, keypoints, frame=None, history=None):
        raise NotImplementedError

class HeelAlignmentRule(SavdhanRule):
    def __init__(self, foot_analyzer):
        self.foot_analyzer = foot_analyzer

    def evaluate(self, keypoints, frame=None, history=None):
        if frame is not None:
            geometry = self.foot_analyzer.analyze_geometry(frame, keypoints)
            if geometry and geometry.get("true_heel_dist") is not None:
                dist = geometry["true_heel_dist"]
                scale = geometry["pose_scale"]
                score = max(0, 100 - (dist / (scale + 1e-6)) * 120)
                return round(score, 1), "Heel gap detected (Visual)" if score < 65 else None

        l_ankle = keypoints[15][:2]
        r_ankle = keypoints[16][:2]
        l_hip = keypoints[11][:2]
        r_hip = keypoints[12][:2]
        hip_width = np.linalg.norm(l_hip - r_hip)
        ankle_dist = np.linalg.norm(l_ankle - r_ankle)
        score = max(0, 100 - (ankle_dist / (hip_width + 1e-6)) * 80)
        return round(score, 1), "Heel gap detected (Sensor)" if score < 60 else None

class FootAngleRule(SavdhanRule):
    def __init__(self, foot_analyzer):
        self.foot_analyzer = foot_analyzer

    def evaluate(self, keypoints, frame=None, history=None):
        if frame is not None:
            geometry = self.foot_analyzer.analyze_geometry(frame, keypoints)
            if geometry and geometry.get("foot_angle") is not None:
                angle = geometry["foot_angle"]
                heel_dist = geometry.get("true_heel_dist", 0.0)
                scale = geometry.get("pose_scale", 1.0)
                
                # Check for visual heel gap
                is_heel_gap = False
                if scale > 0:
                    is_heel_gap = (heel_dist / scale) > 0.1
                    
                if is_heel_gap:
                    return 20.0, "Foot angle invalid: heels not touching"
                    
                # OFFICIAL RANGE: 28-32 Excellent, 25-35 Acceptable
                target = 30.0
                diff = abs(angle - target)
                
                # Strict scoring: 1 point penalty per degree of deviation
                score = max(0, 100 - diff * 3) 
                
                msg = None
                if angle < 25: msg = "Foot angle too narrow (target 30 deg)"
                elif angle > 35: msg = "Foot angle too wide (target 30 deg)"
                
                return round(score, 1), msg
                
        return 90.0, None # Fallback

class KneeStabilityRule(SavdhanRule):
    def evaluate(self, keypoints, frame=None, history=None):
        def get_angle(a, b, c):
            ba = a - b
            bc = c - b
            cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc) + 1e-6)
            return np.degrees(np.arccos(np.clip(cosine_angle, -1.0, 1.0)))

        l_angle = get_angle(keypoints[11][:2], keypoints[13][:2], keypoints[15][:2])
        r_angle = get_angle(keypoints[12][:2], keypoints[14][:2], keypoints[16][:2])
        l_score = max(0, 100 - abs(180 - l_angle) * 3)
        r_score = max(0, 100 - abs(180 - r_angle) * 3)
        score = (l_score + r_score) / 2
        return round(score, 1), "Knees bent" if score < 75 else None

class ArmAlignmentRule(SavdhanRule):
    def evaluate(self, keypoints, frame=None, history=None):
        def get_angle(a, b, c):
            ba = a - b
            bc = c - b
            cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc) + 1e-6)
            return np.degrees(np.arccos(np.clip(cosine_angle, -1.0, 1.0)))

        l_straight = get_angle(keypoints[5][:2], keypoints[7][:2], keypoints[9][:2])
        r_straight = get_angle(keypoints[6][:2], keypoints[8][:2], keypoints[10][:2])
        l_hip_dist = np.linalg.norm(keypoints[9][:2] - keypoints[11][:2])
        r_hip_dist = np.linalg.norm(keypoints[10][:2] - keypoints[12][:2])
        hip_width = np.linalg.norm(keypoints[11][:2] - keypoints[12][:2])
        straight_score = (max(0, 100 - abs(180 - l_straight) * 2) + max(0, 100 - abs(180 - r_straight) * 2)) / 2
        pos_score = (max(0, 100 - (l_hip_dist / (hip_width + 1e-6)) * 60) + max(0, 100 - (r_hip_dist / (hip_width + 1e-6)) * 60)) / 2
        score = (straight_score + pos_score) / 2
        return round(score, 1), "Arms away from body" if pos_score < 65 else None

class TorsoPostureRule(SavdhanRule):
    def evaluate(self, keypoints, frame=None, history=None):
        mid_shoulder = (keypoints[5][:2] + keypoints[6][:2]) / 2
        mid_hip = (keypoints[11][:2] + keypoints[12][:2]) / 2
        dy = mid_hip[1] - mid_shoulder[1]
        dx = mid_hip[0] - mid_shoulder[0]
        angle = np.degrees(np.arctan2(abs(dx), dy))
        score = max(0, 100 - angle * 2)
        return round(score, 1), "Slouching/Leaning" if score < 75 else None

class HeadAlignmentRule(SavdhanRule):
    def evaluate(self, keypoints, frame=None, history=None):
        nose = keypoints[0][:2]
        neck = (keypoints[5][:2] + keypoints[6][:2]) / 2
        dy = neck[1] - nose[1]
        dx = neck[0] - nose[0]
        angle = np.degrees(np.arctan2(abs(dx), dy))
        score = max(0, 100 - angle * 4)
        return round(score, 1), "Head tilted/turned" if score < 70 else None
#this is the last rule to check for savdhan in phase 3 
class StabilityRule(SavdhanRule):
    def evaluate(self, keypoints, frame=None, history=None):
        if history is None or len(history) < 5:
            return 100.0, None
        history_np = np.array(history)
        variance = np.mean(np.std(history_np, axis=0))
        score = max(0, 100 - variance * 30)
        return round(score, 1), "Unstable/Swaying" if score < 60 else None

class SavdhanAnalyzer:
    def __init__(self):
        self.foot_analyzer = FootGeometryAnalyzer()
        self.rules = {
            "Heel Alignment": HeelAlignmentRule(self.foot_analyzer),
            "Foot Angle": FootAngleRule(self.foot_analyzer),
            "Knee Stability": KneeStabilityRule(),
            "Arm Alignment": ArmAlignmentRule(),
            "Torso Posture": TorsoPostureRule(),
            "Head Alignment": HeadAlignmentRule(),
            "Stability": StabilityRule()
        }
        self.cadet_histories = {}

    def analyze(self, cadet_id, keypoints, frame=None):
        if cadet_id not in self.cadet_histories:
            self.cadet_histories[cadet_id] = deque(maxlen=30)
        self.cadet_histories[cadet_id].append(keypoints[:, :2])
        
        scores = {}
        violations = []
        
        for name, rule in self.rules.items():
            history = self.cadet_histories[cadet_id] if name == "Stability" else None
            score, violation = rule.evaluate(keypoints, frame, history)
            scores[name] = score
            if violation:
                violations.append(violation)
        
        overall_score = sum(scores.values()) / len(scores)
        status = "Excellent"
        if overall_score < 70: status = "Incorrect"
        elif overall_score < 85: status = "Warning"
        elif overall_score < 95: status = "Good"
        
        return {
            'scores': scores,
            'overall': round(overall_score, 1),
            'status': status,
            'violations': violations
        }
