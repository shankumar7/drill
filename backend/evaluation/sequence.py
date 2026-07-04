import time
from backend.core.types import PoseDetection, RuleResult

class VisarjanSequence:
    def __init__(self):
        self.name = "Visarjan Sequence"
        self.states = {} # track_id -> {"state": str, "last_transition_time": float}

    def evaluate(self, detection: PoseDetection, *args, **kwargs) -> RuleResult:
        now = time.time()
        track_id = getattr(detection, 'track_id', -1)
        
        if track_id not in self.states:
            self.states[track_id] = {"state": "WAITING_TURN", "last_transition_time": now}
            
        tracker = self.states[track_id]
        
        # Determine current static posture to drive state machine
        # 1. Check for Dahine Murh (Right Turn)
        is_right_turn = False
        l_shoulder = detection.keypoints[5]
        r_shoulder = detection.keypoints[6]
        if l_shoulder[2] > 0.4 and r_shoulder[2] > 0.4:
            shoulder_width = abs(l_shoulder[0] - r_shoulder[0])
            l_hip = detection.keypoints[11]
            r_hip = detection.keypoints[12]
            spine_length = abs( ((l_hip[1]+r_hip[1])/2) - ((l_shoulder[1]+r_shoulder[1])/2) )
            if spine_length > 10 and (shoulder_width / spine_length) < 0.4:
                is_right_turn = True

        # 2. Check for Salute
        is_saluting = False
        r_wrist = detection.keypoints[10]
        r_elbow = detection.keypoints[8]
        r_eye = detection.keypoints[2]
        r_ear = detection.keypoints[4]
        
        if r_wrist[2] > 0.3 and (r_eye[2] > 0.3 or r_ear[2] > 0.3):
            target_y = r_eye[1] if r_eye[2] > 0.3 else r_ear[1]
            if abs(r_wrist[1] - target_y) < 30: # Wrist near eye/ear level
                is_saluting = True

        # State Machine Transitions
        if tracker["state"] == "WAITING_TURN":
            if is_right_turn:
                tracker["state"] = "TURNED_RIGHT"
                tracker["last_transition_time"] = now
                return RuleResult("Visarjan Sequence", 33, "partial_pass", "Right turn detected. Waiting for salute.")
            return RuleResult("Visarjan Sequence", 0, "fail", "Waiting for Dahine Murh (Right Turn)")
            
        elif tracker["state"] == "TURNED_RIGHT":
            if is_saluting:
                tracker["state"] = "SALUTED"
                tracker["last_transition_time"] = now
                return RuleResult("Visarjan Sequence", 66, "partial_pass", "Salute detected. Waiting for dispersal.")
            if now - tracker["last_transition_time"] > 5.0:
                tracker["state"] = "WAITING_TURN" # Timeout, reset
            return RuleResult("Visarjan Sequence", 33, "partial_pass", "Right turn detected. Waiting for salute.")
            
        elif tracker["state"] == "SALUTED":
            # For dispersal, we just wait for them to start walking (legs apart) or leave frame.
            l_ankle = detection.keypoints[15]
            r_ankle = detection.keypoints[16]
            if l_ankle[2] > 0.3 and r_ankle[2] > 0.3:
                ankle_dist = abs(l_ankle[0] - r_ankle[0])
                if ankle_dist > 40: # Taking a step
                    tracker["state"] = "DISPERSING"
                    tracker["last_transition_time"] = now
                    return RuleResult("Visarjan Sequence", 100, "pass", "Dispersal step detected. Visarjan complete.")
            
            if now - tracker["last_transition_time"] > 5.0:
                tracker["state"] = "WAITING_TURN"
            return RuleResult("Visarjan Sequence", 66, "partial_pass", "Salute detected. Waiting for dispersal.")
            
        elif tracker["state"] == "DISPERSING":
            return RuleResult("Visarjan Sequence", 100, "pass", "Visarjan complete.")

        return RuleResult("Visarjan Sequence", 0, "fail", "Unknown state")

class TejChalSequence:
    def __init__(self):
        self.name = "Tej Chal (Quick March)"
        self.buffers = {} # track_id -> list of {"time": float, "l_wrist": [x,y,c], "r_wrist": [x,y,c], "l_ankle": [x,y,c], "r_ankle": [x,y,c]}
        
    def evaluate(self, detection: PoseDetection, *args, **kwargs) -> RuleResult:
        now = time.time()
        track_id = getattr(detection, 'track_id', -1)
        
        if track_id not in self.buffers:
            self.buffers[track_id] = []
            
        buf = self.buffers[track_id]
        
        # Add current frame
        buf.append({
            "time": now,
            "l_wrist": detection.keypoints[9],
            "r_wrist": detection.keypoints[10],
            "l_ankle": detection.keypoints[15],
            "r_ankle": detection.keypoints[16],
            "l_shoulder": detection.keypoints[5],
            "r_shoulder": detection.keypoints[6],
            "l_hip": detection.keypoints[11],
            "r_hip": detection.keypoints[12]
        })
        
        # Prune old frames (keep last 2.0 seconds)
        self.buffers[track_id] = [f for f in buf if now - f["time"] <= 2.0]
        buf = self.buffers[track_id]
        
        if len(buf) < 10:
            return RuleResult(self.name, None, "not_evaluable", "Gathering marching data...")
            
        # Analyze the buffer
        max_wrist_dist = 0
        max_ankle_dist = 0
        spine_length = 100
        
        for f in buf:
            # Spine length (for scaling)
            sl = abs( ((f["l_hip"][1]+f["r_hip"][1])/2) - ((f["l_shoulder"][1]+f["r_shoulder"][1])/2) )
            if sl > 10: spine_length = sl
            
            # Wrist distance (X-axis primarily, but Euclidean is safer for all angles)
            if f["l_wrist"][2] > 0.3 and f["r_wrist"][2] > 0.3:
                # Euclidean distance between wrists
                w_dist = ((f["l_wrist"][0] - f["r_wrist"][0])**2 + (f["l_wrist"][1] - f["r_wrist"][1])**2)**0.5
                if w_dist > max_wrist_dist: max_wrist_dist = w_dist
                
            # Ankle distance
            if f["l_ankle"][2] > 0.3 and f["r_ankle"][2] > 0.3:
                a_dist = ((f["l_ankle"][0] - f["r_ankle"][0])**2 + (f["l_ankle"][1] - f["r_ankle"][1])**2)**0.5
                if a_dist > max_ankle_dist: max_ankle_dist = a_dist

        norm_wrist = max_wrist_dist / spine_length
        norm_ankle = max_ankle_dist / spine_length
        
        # Scoring
        # Marching requires good arm swing and long strides
        arm_score = 100 if norm_wrist > 0.8 else max(0, int(norm_wrist / 0.8 * 100))
        stride_score = 100 if norm_ankle > 0.6 else max(0, int(norm_ankle / 0.6 * 100))
        
        overall = int((arm_score + stride_score) / 2)
        
        if overall > 80:
            return RuleResult(self.name, overall, "pass", f"Excellent marching cadence (Arm: {arm_score}%, Stride: {stride_score}%)")
        elif overall > 50:
            return RuleResult(self.name, overall, "partial_pass", f"Weak marching cadence (Arm: {arm_score}%, Stride: {stride_score}%)")
        else:
            return RuleResult(self.name, overall, "fail", f"Not marching or poor cadence (Arm: {arm_score}%, Stride: {stride_score}%)")

class ThaamSequence:
    def __init__(self):
        self.name = "Thaam (Halt from March)"
        self.states = {} # track_id -> {"state": str, "last_transition": float}
        # To evaluate Savdhan post-halt
        from backend.evaluation.rules.savdhan_heel_contact import SavdhanHeelContactRule
        from backend.evaluation.rules.savdhan_arm_position import SavdhanArmPositionRule
        from backend.evaluation.rules.knee_distance import KneeDistanceRule
        self.savdhan_rules = [
            SavdhanHeelContactRule(),
            SavdhanArmPositionRule(),
            KneeDistanceRule("close")
        ]

    def evaluate(self, detection: PoseDetection, *args, **kwargs) -> RuleResult:
        now = time.time()
        track_id = getattr(detection, 'track_id', -1)
        if track_id not in self.states:
            self.states[track_id] = {"state": "MARCHING", "last_transition": now}
            
        tracker = self.states[track_id]
        
        # Check lower body dynamic state
        l_ankle = detection.keypoints[15]
        r_ankle = detection.keypoints[16]
        
        ankle_dist = 0
        if l_ankle[2] > 0.3 and r_ankle[2] > 0.3:
            ankle_dist = abs(l_ankle[0] - r_ankle[0])
            
        l_hip = detection.keypoints[11]
        r_hip = detection.keypoints[12]
        l_shoulder = detection.keypoints[5]
        r_shoulder = detection.keypoints[6]
        spine_length = 100
        if l_hip[2] > 0.3 and l_shoulder[2] > 0.3:
            spine_length = abs( ((l_hip[1]+r_hip[1])/2) - ((l_shoulder[1]+r_shoulder[1])/2) )
            if spine_length < 10: spine_length = 100
            
        norm_stride = ankle_dist / spine_length
        
        if tracker["state"] == "MARCHING":
            if norm_stride < 0.2: # Stride has closed (feet together)
                tracker["state"] = "HALTED"
                tracker["last_transition"] = now
                return RuleResult(self.name, 50, "partial_pass", "Halt detected, checking Savdhan posture...")
            return RuleResult(self.name, 0, "fail", "Waiting for Halt (feet together)")
            
        elif tracker["state"] == "HALTED":
            if norm_stride > 0.4:
                # Started moving again
                tracker["state"] = "MARCHING"
                tracker["last_transition"] = now
                return RuleResult(self.name, 0, "fail", "Broke halt, returned to marching")
                
            # Must hold halt for at least 1 second to formally evaluate Savdhan
            if now - tracker["last_transition"] > 1.0:
                # Evaluate Savdhan rules
                results = [r.evaluate(detection) for r in self.savdhan_rules]
                scored = [r.score for r in results if r.score is not None]
                if not scored:
                    return RuleResult(self.name, None, "not_evaluable", "Halted, but cannot see full body")
                
                avg_score = int(sum(scored) / len(scored))
                if avg_score > 80:
                    return RuleResult(self.name, avg_score, "pass", f"Excellent Halt into Savdhan ({avg_score}%)")
                else:
                    return RuleResult(self.name, avg_score, "fail", f"Poor Savdhan posture after Halt ({avg_score}%)")
            else:
                return RuleResult(self.name, 50, "partial_pass", "Holding Halt...")
                
        return RuleResult(self.name, 0, "fail", "Unknown state")

class MarchingSaluteSequence:
    def __init__(self, direction: str):
        self.direction = direction
        self.name = f"Marching Salute ({direction.capitalize()})"
        self.buffers = {} # track_id -> list of frames
        
        from backend.evaluation.rules.salute_arm_angle import SaluteRightArmAngleRule, StraightLeftArmAngleRule
        from backend.evaluation.rules.salute_hand_position import SaluteHandPositionRule
        from backend.evaluation.rules.salute_head_direction import HeadDirectionRule
        
        self.upper_body_rules = [
            SaluteRightArmAngleRule(),
            StraightLeftArmAngleRule(),
            SaluteHandPositionRule(),
            HeadDirectionRule(direction)
        ]

    def evaluate(self, detection: PoseDetection, *args, **kwargs) -> RuleResult:
        now = time.time()
        track_id = getattr(detection, 'track_id', -1)
        
        if track_id not in self.buffers:
            self.buffers[track_id] = []
            
        buf = self.buffers[track_id]
        
        # Add current frame
        buf.append({
            "time": now,
            "l_ankle": detection.keypoints[15],
            "r_ankle": detection.keypoints[16],
            "l_shoulder": detection.keypoints[5],
            "r_shoulder": detection.keypoints[6],
            "l_hip": detection.keypoints[11],
            "r_hip": detection.keypoints[12]
        })
        
        # Prune old frames (keep last 2.0 seconds)
        self.buffers[track_id] = [f for f in buf if now - f["time"] <= 2.0]
        buf = self.buffers[track_id]
        
        if len(buf) < 10:
            return RuleResult(self.name, None, "not_evaluable", "Gathering marching data...")
            
        # Analyze the buffer for stride (Legs must be marching)
        max_ankle_dist = 0
        spine_length = 100
        
        for f in buf:
            sl = abs( ((f["l_hip"][1]+f["r_hip"][1])/2) - ((f["l_shoulder"][1]+f["r_shoulder"][1])/2) )
            if sl > 10: spine_length = sl
            if f["l_ankle"][2] > 0.3 and f["r_ankle"][2] > 0.3:
                a_dist = ((f["l_ankle"][0] - f["r_ankle"][0])**2 + (f["l_ankle"][1] - f["r_ankle"][1])**2)**0.5
                if a_dist > max_ankle_dist: max_ankle_dist = a_dist

        norm_ankle = max_ankle_dist / spine_length
        stride_score = 100 if norm_ankle > 0.6 else max(0, int(norm_ankle / 0.6 * 100))
        
        if stride_score < 40:
            return RuleResult(self.name, stride_score, "fail", f"Cadet stopped marching (Stride: {stride_score}%)")
            
        # Evaluate upper body static salute
        results = [r.evaluate(detection) for r in self.upper_body_rules]
        scored = [r.score for r in results if r.score is not None]
        if not scored:
            return RuleResult(self.name, None, "not_evaluable", "Marching, but cannot evaluate salute posture")
            
        upper_score = int(sum(scored) / len(scored))
        overall = int((stride_score + upper_score) / 2)
        
        if overall > 80:
            return RuleResult(self.name, overall, "pass", f"Excellent Marching Salute (Stride: {stride_score}%, Salute: {upper_score}%)")
        elif overall > 50:
            return RuleResult(self.name, overall, "partial_pass", f"Weak Marching Salute (Stride: {stride_score}%, Salute: {upper_score}%)")
        else:
            return RuleResult(self.name, overall, "fail", f"Poor Marching Salute (Stride: {stride_score}%, Salute: {upper_score}%)")

class MarchingTurnSequence:
    def __init__(self, turn_type: str):
        self.turn_type = turn_type
        self.name = f"Marching Turn ({turn_type.capitalize()})"
        self.states = {} # track_id -> {"state": str, "last_transition": float, "initial_shoulder_width": float}
        self.buffers = {}
        
    def evaluate(self, detection: PoseDetection, *args, **kwargs) -> RuleResult:
        now = time.time()
        track_id = getattr(detection, 'track_id', -1)
        
        if track_id not in self.states:
            self.states[track_id] = {"state": "MARCHING_STRAIGHT", "last_transition": now, "initial_shoulder_width": 0}
            self.buffers[track_id] = []
            
        tracker = self.states[track_id]
        buf = self.buffers[track_id]
        
        # Add current frame
        buf.append({
            "time": now,
            "l_ankle": detection.keypoints[15],
            "r_ankle": detection.keypoints[16],
            "l_shoulder": detection.keypoints[5],
            "r_shoulder": detection.keypoints[6],
            "l_hip": detection.keypoints[11],
            "r_hip": detection.keypoints[12]
        })
        
        # Prune old frames (keep last 2.0 seconds)
        self.buffers[track_id] = [f for f in buf if now - f["time"] <= 2.0]
        buf = self.buffers[track_id]
        
        # Check stride
        max_ankle_dist = 0
        spine_length = 100
        current_shoulder_width = 0
        
        for f in buf:
            sl = abs( ((f["l_hip"][1]+f["r_hip"][1])/2) - ((f["l_shoulder"][1]+f["r_shoulder"][1])/2) )
            if sl > 10: spine_length = sl
            if f["l_ankle"][2] > 0.3 and f["r_ankle"][2] > 0.3:
                a_dist = ((f["l_ankle"][0] - f["r_ankle"][0])**2 + (f["l_ankle"][1] - f["r_ankle"][1])**2)**0.5
                if a_dist > max_ankle_dist: max_ankle_dist = a_dist

        norm_ankle = max_ankle_dist / spine_length
        is_marching = norm_ankle > 0.4
        
        l_shoulder = detection.keypoints[5]
        r_shoulder = detection.keypoints[6]
        if l_shoulder[2] > 0.3 and r_shoulder[2] > 0.3:
            current_shoulder_width = abs(l_shoulder[0] - r_shoulder[0]) / spine_length
            
        # State Machine
        if tracker["state"] == "MARCHING_STRAIGHT":
            if not is_marching:
                return RuleResult(self.name, 0, "fail", "Must be marching before turning")
                
            if tracker["initial_shoulder_width"] == 0 and current_shoulder_width > 0:
                tracker["initial_shoulder_width"] = current_shoulder_width
                
            # If shoulder width drops significantly, they are turning (showing profile)
            # OR if Pichhe (About Turn), shoulders swap sides (but width might briefly drop)
            if tracker["initial_shoulder_width"] > 0 and current_shoulder_width < (tracker["initial_shoulder_width"] * 0.6):
                tracker["state"] = "TURNING"
                tracker["last_transition"] = now
                return RuleResult(self.name, 50, "partial_pass", "Turn detected. Maintaining stride...")
                
            return RuleResult(self.name, 0, "fail", "Marching straight. Waiting for turn.")
            
        elif tracker["state"] == "TURNING":
            if not is_marching:
                tracker["state"] = "MARCHING_STRAIGHT" # Reset
                return RuleResult(self.name, 0, "fail", "Cadet stopped marching during the turn!")
                
            # Hold turn state for 1 second to ensure they continue marching through it
            if now - tracker["last_transition"] > 1.0:
                tracker["state"] = "TURN_COMPLETED"
                tracker["last_transition"] = now
                return RuleResult(self.name, 100, "pass", "Marching Turn executed flawlessly without breaking stride.")
                
            return RuleResult(self.name, 75, "partial_pass", "Turning... keep marching!")
            
        elif tracker["state"] == "TURN_COMPLETED":
            return RuleResult(self.name, 100, "pass", "Marching Turn completed.")
            
        return RuleResult(self.name, 0, "fail", "Unknown state")
