import cv2
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import json
import numpy as np
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import time
import tempfile
from backend.visualization.debug_view import _draw_skeleton
app = FastAPI(title="Military Drill Analysis API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state for ML
LATEST_TELEMETRY = {
    "torso_posture": 0,
    "heel_alignment": 0,
    "foot_angle": 0,
    "arm_alignment": 0,
    "heel_distance": 0,
    "toe_distance": 0,
    "knee_tightness": 0,
    "hands_behind_back": 0,
    "salute_arm_angle": 0,
    "straight_arm_angle": 0,
    "head_direction": 0,
    "salute_hand_position": 0,
    "overall_score": 0,
    "status": "Initializing...",
    "detected_ids": [],
    "active_mode": "SAVDHAN",
    "last_command": ""
}
ACTIVE_MODE = "SAVDHAN"
LOCKED_CADET_ID = None
MULTI_CAM_DETECTIONS = {}
DETECTION_LOCK = asyncio.Lock()

# ─── Configurable Settings ────────────────────────────────────────────────────
SETTINGS = {
    # ── Network
    "backend_host": "localhost",
    "backend_port": 8000,
    "ws_reconnect_interval": 3,
    # ── AI / Pose Detection
    "confidence": 0.5,
    "image_size": 640,
    "keypoint_visibility_threshold": 0.3,
    "max_detections": 10,
    "stale_detection_timeout": 2.0,
    "prefer_half_precision": True,
    "tracking_config": "bytetrack.yaml",
    "evaluation_fps": 20,
    # ── Evaluation / Scoring
    "pass_threshold": 85,
    "score_smoothing_window": 1,
    "savdhan_threshold": 85,
    "vishram_threshold": 80,
    "salute_threshold": 80,
    "aaram_se_threshold": 75,
    # ── Voice
    "voice_enabled": True,
    "voice_language": "en",
    "voice_initial_prompt": "Military drill commands: savadhan, attention, vishram, ease, salute, samne, baye, dahine, aaram.",
    # ── Display
    "show_skeleton": True,
    "show_id_overlay": True,
    "show_confidence_score": False,
    "camera_label_position": "top-left",
    "skeleton_color": "green",
    "overlay_opacity": 0.8,
    # ── Session
    "auto_save_session": False,
    "unit_name": "",
    "instructor_name": "Lt Col K Srinath",
    "export_format": "json",
    "session_duration_limit": 0,
    # ── Camera
    "camera_mapping": {"front": 0, "side": 1, "back": 2},
    "camera_flip_horizontal": False,
    "camera_flip_vertical": False,
    "camera_fps_cap": 30,
    # ── Alerts
    "alert_on_pass": False,
    "alert_on_fail": True,
    "alert_visual_flash": True,
}

class SettingsUpdate(BaseModel):
    # Network
    backend_host: str | None = None
    backend_port: int | None = None
    ws_reconnect_interval: int | None = None
    # AI
    confidence: float | None = None
    image_size: int | None = None
    keypoint_visibility_threshold: float | None = None
    max_detections: int | None = None
    stale_detection_timeout: float | None = None
    prefer_half_precision: bool | None = None
    tracking_config: str | None = None
    evaluation_fps: int | None = None
    # Evaluation
    pass_threshold: int | None = None
    score_smoothing_window: int | None = None
    savdhan_threshold: int | None = None
    vishram_threshold: int | None = None
    salute_threshold: int | None = None
    aaram_se_threshold: int | None = None
    # Voice
    voice_enabled: bool | None = None
    voice_language: str | None = None
    voice_initial_prompt: str | None = None
    # Display
    show_skeleton: bool | None = None
    show_id_overlay: bool | None = None
    show_confidence_score: bool | None = None
    camera_label_position: str | None = None
    skeleton_color: str | None = None
    overlay_opacity: float | None = None
    # Session
    auto_save_session: bool | None = None
    unit_name: str | None = None
    instructor_name: str | None = None
    export_format: str | None = None
    session_duration_limit: int | None = None
    # Camera
    camera_mapping: dict | None = None
    camera_flip_horizontal: bool | None = None
    camera_flip_vertical: bool | None = None
    camera_fps_cap: int | None = None
    # Alerts
    alert_on_pass: bool | None = None
    alert_on_fail: bool | None = None
    alert_visual_flash: bool | None = None

pose_estimator = None
try:
    from backend.inference.pose_estimator import YoloPoseEstimator
    pose_estimator = YoloPoseEstimator(
        model_path="yolo11n-pose.pt",
        confidence=0.5,
        image_size=640,
        prefer_half_precision=True,
        tracking_enabled=True,
        tracker_config="bytetrack.yaml"
    )
    print("Pose Estimator loaded in API.")
except Exception as e:
    print(f"Failed to load Pose Estimator: {e}")

whisper_model = None
try:
    import whisper
    import torch
    device = "cuda" if torch.cuda.is_available() else "cpu"
    whisper_model = whisper.load_model("base", device=device)
    print(f"Whisper Model loaded in API on {device}.")
except Exception as e:
    print(f"Failed to load Whisper Model: {e}")

# Helper to map pixel distance to inches based on a heuristic (shoulder width ~16 inches)
def estimate_foot_geometry(keypoints):
    from backend.evaluation.geometry import segment_length, mid_point
    
    # 5: L Shoulder, 6: R Shoulder, 11: L Hip, 12: R Hip, 15: L Ankle, 16: R Ankle, 19: L Toe, 22: R Toe
    # (Note: YOLO11n-POSE uses COCO 17 or similar, toes are typically not explicitly 19/22 in COCO, 
    # but ankles are 15, 16 and we can use ankles as proxies for heel distance, and toes are not reliably available 
    # in standard 17-keypoint models without mediapipe. Let's just use 15 and 16).
    
    l_shoulder, r_shoulder = keypoints[5, :2], keypoints[6, :2]
    l_hip, r_hip = keypoints[11, :2], keypoints[12, :2]
    
    shoulder_pixel_width = segment_length(l_shoulder, r_shoulder)
    spine_length = segment_length(mid_point(l_shoulder, r_shoulder), mid_point(l_hip, r_hip))
    
    if spine_length < 10:
        spine_length = 100 # Fallback for extreme cases
    if shoulder_pixel_width < 10:
        shoulder_pixel_width = 100
    
    # Check if ankles are actually visible (confidence > 0.3)
    l_ankle_conf = keypoints[15, 2] if keypoints.shape[1] > 2 else 1.0
    r_ankle_conf = keypoints[16, 2] if keypoints.shape[1] > 2 else 1.0
    
    if l_ankle_conf < 0.3 or r_ankle_conf < 0.3:
        return None
        
    l_ankle, r_ankle = keypoints[15, :2], keypoints[16, :2]
    heel_dist_px = segment_length(l_ankle, r_ankle)
    
    # If the model has more than 17 keypoints (e.g. 23+ for hands/feet), try to extract toes.
    # Otherwise, fallback to ankles for heel dist.
    toe_dist_px = heel_dist_px
    l_toe_conf = keypoints[19, 2] if keypoints.shape[0] > 19 and keypoints.shape[1] > 2 else 0.0
    r_toe_conf = keypoints[22, 2] if keypoints.shape[0] > 22 and keypoints.shape[1] > 2 else 0.0
    
    if l_toe_conf > 0.3 and r_toe_conf > 0.3:
        toe_dist_px = segment_length(keypoints[19, :2], keypoints[22, :2])
    
    return {
        "true_heel_dist": heel_dist_px,
        "true_toe_dist": toe_dist_px,
        "pose_scale": shoulder_pixel_width,
        "spine_length": spine_length
    }

async def generate_frames(camera_id: int):
    global LATEST_TELEMETRY, ACTIVE_MODE
    import os
    
    cap = cv2.VideoCapture(camera_id)
    is_webcam = True
    
    if not cap.isOpened() or camera_id not in [0, 1, 2]:
        while True:
            frame = np.ones((480, 640, 3), dtype=np.uint8) * 150
            cv2.putText(frame, f"CAM {camera_id} - MISSING VIDEO", (150, 240), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            ret, buffer = cv2.imencode('.jpg', frame)
            yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
            await asyncio.sleep(0.1)

    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
            
    while True:
        success, frame = cap.read()
        if not success:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            success, frame = cap.read()
            if not success:
                break
                
        # Slice the 804x480 frame into 3 sections (268px wide each)
        if not is_webcam:
            if camera_id == 0:
                frame = frame[:, :268]
            elif camera_id == 1:
                frame = frame[:, 268:536]
            elif camera_id == 2:
                frame = frame[:, 536:]
        
        if pose_estimator:
            try:
                detections = pose_estimator.infer(frame)
                if detections:
                    det = None
                    available_ids = [getattr(d, 'track_id', -1) for d in detections]
                    if LOCKED_CADET_ID is not None:
                        for d in detections:
                            if getattr(d, 'track_id', None) == LOCKED_CADET_ID:
                                det = d
                                break
                    if not det:
                        det = detections[0]
                        
                    det.foot_geometry = estimate_foot_geometry(det.keypoints)
                    shoulder_px = np.linalg.norm(det.keypoints[5, :2] - det.keypoints[6, :2])
                    if shoulder_px < 10:
                        shoulder_px = 100
                    ppi = shoulder_px / 16.0
                    avg_conf = float(np.mean(det.keypoints[:, 2]))
                    
                    async with DETECTION_LOCK:
                        MULTI_CAM_DETECTIONS[camera_id] = {"det": det, "ts": time.time(), "ppi": ppi, "conf": avg_conf, "available_ids": available_ids, "all_dets": detections}
                    
                    if SETTINGS.get("show_skeleton", True):
                        _draw_skeleton(frame, det.keypoints)
                        
                    if SETTINGS.get("show_confidence_score", False):
                        # Draw some debug confidence next to skeleton
                        for point in det.keypoints:
                            if point[2] > 0.3:
                                cv2.putText(frame, f"{point[2]:.2f}", (int(point[0])+5, int(point[1])-5), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0, 255, 0), 1)
                    
                    tid = getattr(det, 'track_id', 'Unknown')
                    if tid is not None and SETTINGS.get("show_id_overlay", True):
                        cx, cy = int(det.bbox[0]), int(det.bbox[1])
                        cv2.putText(frame, f"ID: {tid}", (cx, max(0, cy - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

                else:
                    async with DETECTION_LOCK:
                        MULTI_CAM_DETECTIONS[camera_id] = None
            except Exception as e:
                import traceback
                traceback.print_exc()
                print(f"Error in ML pipeline: {e}")

        # The Next.js frontend already overlays the camera name and mode cleanly in a UI pill,
        # so we don't need to draw ugly green OpenCV text on the raw frames anymore.
        
        ret, buffer = cv2.imencode('.jpg', frame)
        yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
        # Maintain roughly 30 FPS playback simulation
        await asyncio.sleep(1/fps)



from pydantic import BaseModel
class LockCadetRequest(BaseModel):
    track_id: int | None

@app.post("/api/lock_cadet")
async def lock_cadet(req: LockCadetRequest):
    global LOCKED_CADET_ID
    LOCKED_CADET_ID = req.track_id
    return {"status": "ok", "locked_id": LOCKED_CADET_ID}

@app.get("/api/settings")
async def get_settings():
    return SETTINGS

@app.post("/api/settings")
async def update_settings(update: SettingsUpdate):
    global SETTINGS, pose_estimator
    data = update.model_dump(exclude_none=True)
    SETTINGS.update(data)
    # Live-apply to pose estimator
    if pose_estimator:
        if "confidence" in data:
            try: pose_estimator.model.conf = data["confidence"]
            except Exception: pass
        if "image_size" in data:
            try: pose_estimator.model.imgsz = data["image_size"]
            except Exception: pass
    return {"status": "ok", "settings": SETTINGS}

@app.get("/api/settings/reset")
async def reset_settings():
    """Reset all settings to defaults."""
    global SETTINGS
    SETTINGS["confidence"] = 0.5
    SETTINGS["pass_threshold"] = 85
    SETTINGS["image_size"] = 640
    SETTINGS["voice_language"] = "en"
    return {"status": "ok", "settings": SETTINGS}


from fastapi import UploadFile, File

@app.post("/api/voice_command")
async def process_voice_command(audio: UploadFile = File(...)):
    global ACTIVE_MODE, LATEST_TELEMETRY
    if not whisper_model:
        return {"error": "Whisper model not loaded"}
    
    content = await audio.read()
    # WebM headers are small. If file is < 1KB, it contains no actual audio frames
    if len(content) < 1000:
        return {"error": "Recording too short. Please hold the button longer while speaking."}
    
    filename = audio.filename if audio.filename else "command.webm"
    ext = os.path.splitext(filename)[1]
    if not ext:
        ext = ".webm"
        
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as temp_audio:
        temp_audio.write(content)
        temp_audio_path = temp_audio.name
        
    try:
        # Whisper automatically handles various audio formats including webm
        # Note: This requires ffmpeg to be installed on the system
        import torch
        result = whisper_model.transcribe(
            temp_audio_path,
            language="en",
            fp16=torch.cuda.is_available(),
            initial_prompt="Military drill commands: savadhan, attention, vishram, ease, salute, samne, baye, dahine, aaram."
        )
        text = result.get("text", "").strip()
        text_lower = text.lower()
        
        # Enhanced keyword matching for Indian accents and common whisper mis-transcriptions
        savdhan_keywords = ["savadhan", "attention", "savdhan", "south on", "sawan", "some down", "savage on", "sound on", "sab dhan", "sabdan"]
        vishram_keywords = ["vishram", "ease", "vish", "mushroom", "wish ram", "visram", "rest", "base ram", "besram", "bharam"]
        salute_keywords = ["salute", "samne", "someday", "sam ne"]
        baye_keywords = ["baye", "left", "bye", "by a", "baen", "baaye"]
        dahine_keywords = ["dahine", "right", "dining", "diane", "daehne", "dahin", "dhahine"]
        aaram_keywords = ["aaram", "aram", "alarm", "aram se"]
        
        # New drill keywords
        dahine_murh_keywords = ["dahine murh", "right turn", "turn right", "dahine mood", "dahine mud", "diane mud"]
        bayen_murh_keywords = ["bayen murh", "left turn", "turn left", "bayen mood", "bayen mud", "baye mud", "baye mood"]
        pichhe_murh_keywords = ["pichhe murh", "about turn", "piche murh", "piche mud", "pichhe mud"]
        khuli_line_keywords = ["khuli line", "open line"]
        nikat_line_keywords = ["nikat line", "close line", "near line"]

        if any(kw in text_lower for kw in dahine_murh_keywords):
            ACTIVE_MODE = "DAHINE_MURH"
        elif any(kw in text_lower for kw in bayen_murh_keywords):
            ACTIVE_MODE = "BAYEN_MURH"
        elif any(kw in text_lower for kw in pichhe_murh_keywords):
            ACTIVE_MODE = "PICHHE_MURH"
        elif any(kw in text_lower for kw in khuli_line_keywords):
            ACTIVE_MODE = "KHULI_LINE_CHAL"
        elif any(kw in text_lower for kw in nikat_line_keywords):
            ACTIVE_MODE = "NIKAT_LINE_CHAL"
        elif any(kw in text_lower for kw in savdhan_keywords):
            ACTIVE_MODE = "SAVDHAN"
        elif any(kw in text_lower for kw in vishram_keywords):
            ACTIVE_MODE = "VISHRAM"
        elif any(kw in text_lower for kw in salute_keywords) or any(kw in text_lower for kw in baye_keywords) or any(kw in text_lower for kw in dahine_keywords):
            if any(kw in text_lower for kw in baye_keywords):
                ACTIVE_MODE = "BAYE_SALUTE"
            elif any(kw in text_lower for kw in dahine_keywords):
                ACTIVE_MODE = "DAINE_SALUTE"
            else:
                ACTIVE_MODE = "FRONT_SALUTE"
        elif any(kw in text_lower for kw in aaram_keywords):
            ACTIVE_MODE = "AARAM_SE"
            
        print(f"Voice Command Received: '{text}', Mode updated to: {ACTIVE_MODE}")
        LATEST_TELEMETRY["active_mode"] = ACTIVE_MODE
        LATEST_TELEMETRY["last_command"] = text
        
        return {"text": text, "active_mode": ACTIVE_MODE}
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Whisper Transcription Error: {e}")
        return {"error": str(e)}
    finally:
        os.remove(temp_audio_path)

@app.get("/api/video_feed/{camera_id}")
async def video_feed(camera_id: int):
    return StreamingResponse(generate_frames(camera_id), media_type="multipart/x-mixed-replace; boundary=frame")

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(fusion_evaluator_loop())
    asyncio.create_task(prune_stale_detections())

async def fusion_evaluator_loop():
    global LATEST_TELEMETRY
    current_evaluator_mode = None
    evaluator = None
    
    while True:
        await asyncio.sleep(0.05)  # 20 FPS Evaluation
        
        try:
            from backend.evaluation.evaluator import StaticPostureEvaluator
            if current_evaluator_mode != ACTIVE_MODE:
                evaluator = StaticPostureEvaluator(ACTIVE_MODE)
                current_evaluator_mode = ACTIVE_MODE
                
            # Copy detections under lock
            async with DETECTION_LOCK:
                detections_snapshot = dict(MULTI_CAM_DETECTIONS)
            
            # Find the most recent timestamp
            timestamps = [v["ts"] for v in detections_snapshot.values() if v]
            if not timestamps:
                # print("No timestamps found in detections")
                continue
            
            fused_scores = {}
            fused_weights = {}
            fused_results = {}
            for cam_id, entry in detections_snapshot.items():
                if not entry:
                    continue
                
                det = entry["det"]
                all_dets = entry.get("all_dets", [det])
                conf = entry.get("conf", 1.0)
                evaluation = evaluator.evaluate(det, all_dets)
                
                for r in evaluation.rules:
                    if r.score is not None:
                        weighted_score = r.score * conf
                        if r.name not in fused_weights or weighted_score > fused_weights[r.name]:
                            fused_weights[r.name] = weighted_score
                            fused_scores[r.name] = r.score
                            fused_results[r.name] = r
                    else:
                        if r.name not in fused_results:
                            fused_results[r.name] = r

            if not fused_results:
                continue

            overall_score = round(sum(fused_scores.values()) / len(fused_scores)) if fused_scores else 0
            
            any_missing = any(res.status == "not_evaluable" for res in fused_results.values())
            
            if any_missing or not fused_scores:
                status = "Initializing..."
            else:
                status = "PASS" if overall_score >= SETTINGS["pass_threshold"] else "FAIL"

            def get_payload(rule_name):
                res = fused_results.get(rule_name)
                if not res:
                    return {"status": "not_evaluable", "reason": "No data"}
                return {"status": res.status, "reason": res.message}
                
            all_ids = set()
            for entry in detections_snapshot.values():
                if entry and "available_ids" in entry:
                    all_ids.update(entry["available_ids"])
            LATEST_TELEMETRY["detected_ids"] = list(all_ids)

            if ACTIVE_MODE == "SAVDHAN":
                LATEST_TELEMETRY.update({
                    "torso_posture": get_payload("Body Posture"),
                    "heel_alignment": get_payload("Heel contact"),
                    "foot_angle": get_payload("Foot angle"),
                    "arm_alignment": get_payload("Arms at sides"),
                    "knee_tightness": get_payload("Knee distance"),
                    "overall_score": overall_score,
                    "status": status
                })
            elif ACTIVE_MODE == "VISHRAM":
                LATEST_TELEMETRY.update({
                    "heel_distance": get_payload("Foot spacing"),
                    "toe_distance": get_payload("Foot spacing"),
                    "knee_tightness": get_payload("Knee lock"),
                    "hands_behind_back": get_payload("Hands behind back"),
                    "torso_posture": get_payload("Body Posture"),
                    "overall_score": overall_score,
                    "status": status
                })
            elif ACTIVE_MODE == "AARAM_SE":
                LATEST_TELEMETRY.update({
                    "heel_distance": get_payload("Foot spacing"),
                    "toe_distance": get_payload("Foot spacing"),
                    "overall_score": overall_score,
                    "status": status
                })
            elif ACTIVE_MODE in ["FRONT_SALUTE", "BAYE_SALUTE", "DAINE_SALUTE"]:
                LATEST_TELEMETRY.update({
                    "torso_posture": get_payload("Body Posture"),
                    "salute_arm_angle": get_payload("Saluting Arm Angle"),
                    "straight_arm_angle": get_payload("Straight Arm Angle"),
                    "head_direction": get_payload("Head Direction"),
                    "salute_hand_position": get_payload("Saluting Hand Position"),
                    "overall_score": overall_score,
                    "status": status
                })
            elif ACTIVE_MODE == "DAHINE_MURH":
                LATEST_TELEMETRY.update({
                    "torso_posture": get_payload("Body Posture"),
                    "arm_alignment": get_payload("Right Turn (Dahine Murh)"),
                    "heel_alignment": get_payload("Right Turn (Dahine Murh)"),
                    "foot_angle": get_payload("Right Turn (Dahine Murh)"),
                    "overall_score": overall_score,
                    "status": status
                })
            elif ACTIVE_MODE == "BAYEN_MURH":
                LATEST_TELEMETRY.update({
                    "torso_posture": get_payload("Body Posture"),
                    "arm_alignment": get_payload("Left Turn (Bayen Murh)"),
                    "heel_alignment": get_payload("Left Turn (Bayen Murh)"),
                    "foot_angle": get_payload("Left Turn (Bayen Murh)"),
                    "overall_score": overall_score,
                    "status": status
                })
            elif ACTIVE_MODE == "PICHHE_MURH":
                LATEST_TELEMETRY.update({
                    "torso_posture": get_payload("Body Posture"),
                    "arm_alignment": get_payload("About Turn (Pichhe Murh)"),
                    "heel_alignment": get_payload("About Turn (Pichhe Murh)"),
                    "foot_angle": get_payload("About Turn (Pichhe Murh)"),
                    "overall_score": overall_score,
                    "status": status
                })
            elif ACTIVE_MODE == "KHULI_LINE_CHAL":
                LATEST_TELEMETRY.update({
                    "torso_posture": get_payload("Body Posture"),
                    "arm_alignment": get_payload("Open Line Chal (Khuli Line)"),
                    "heel_distance": get_payload("Open Line Chal (Khuli Line)"),
                    "toe_distance": get_payload("Open Line Chal (Khuli Line)"),
                    "overall_score": overall_score,
                    "status": status
                })
            elif ACTIVE_MODE == "NIKAT_LINE_CHAL":
                LATEST_TELEMETRY.update({
                    "torso_posture": get_payload("Body Posture"),
                    "arm_alignment": get_payload("Close Line Chal (Nikat Line)"),
                    "heel_distance": get_payload("Close Line Chal (Nikat Line)"),
                    "toe_distance": get_payload("Close Line Chal (Nikat Line)"),
                    "overall_score": overall_score,
                    "status": status
                })
            elif ACTIVE_MODE == "SAJ":
                LATEST_TELEMETRY.update({
                    "torso_posture": get_payload("Body Posture"),
                    "arm_alignment": get_payload("Squad Alignment (Saj)"),
                    "overall_score": overall_score,
                    "status": status
                })
            elif ACTIVE_MODE == "VISARJAN":
                LATEST_TELEMETRY.update({
                    "torso_posture": get_payload("Body Posture"),
                    "arm_alignment": get_payload("Visarjan Sequence"),
                    "overall_score": overall_score,
                    "status": status
                })
            elif ACTIVE_MODE == "TEJ_CHAL":
                LATEST_TELEMETRY.update({
                    "torso_posture": get_payload("Body Posture"),
                    "arm_alignment": get_payload("Tej Chal (Quick March)"),
                    "overall_score": overall_score,
                    "status": status
                })
            elif ACTIVE_MODE == "THAAM":
                LATEST_TELEMETRY.update({
                    "torso_posture": get_payload("Body Posture"),
                    "arm_alignment": get_payload("Thaam (Halt from March)"),
                    "overall_score": overall_score,
                    "status": status
                })
            elif ACTIVE_MODE in ["MARCHING_FRONT_SALUTE", "MARCHING_BAYE_SALUTE", "MARCHING_DAINE_SALUTE"]:
                dir_label = "Front" if "FRONT" in ACTIVE_MODE else "Left" if "BAYE" in ACTIVE_MODE else "Right"
                LATEST_TELEMETRY.update({
                    "torso_posture": get_payload("Body Posture"),
                    "arm_alignment": get_payload(f"Marching Salute ({dir_label})"),
                    "overall_score": overall_score,
                    "status": status
                })
            elif ACTIVE_MODE in ["MARCHING_TURN_DAHINE", "MARCHING_TURN_BAYEN", "MARCHING_TURN_PICHHE"]:
                turn_label = "Dahine" if "DAHINE" in ACTIVE_MODE else "Bayen" if "BAYEN" in ACTIVE_MODE else "Pichhe"
                LATEST_TELEMETRY.update({
                    "torso_posture": get_payload("Body Posture"),
                    "arm_alignment": get_payload(f"Marching Turn ({turn_label})"),
                    "overall_score": overall_score,
                    "status": status
                })
        except Exception as e:
            import traceback
            with open("/tmp/fusion_error.txt", "a") as f:
                f.write(traceback.format_exc() + "\n")
            print(f"Fusion error: {e}")

@app.websocket("/ws/telemetry")
async def websocket_telemetry(websocket: WebSocket):
    global ACTIVE_MODE
    await websocket.accept()
    
    async def send_telemetry():
        while True:
            try:
                await websocket.send_text(json.dumps(LATEST_TELEMETRY))
                await asyncio.sleep(0.5)
            except Exception:
                break

    async def receive_mode():
        global ACTIVE_MODE
        while True:
            try:
                data = await websocket.receive_text()
                msg = json.loads(data)
                if "mode" in msg:
                    ACTIVE_MODE = msg["mode"].upper()
                    # Fix spelling mismatch from UI "Savadhan" vs backend "SAVDHAN"
                    if ACTIVE_MODE == "SAVADHAN":
                        ACTIVE_MODE = "SAVDHAN"
                    print(f"Mode switched to {ACTIVE_MODE}")
            except Exception:
                break
                
    task1 = asyncio.create_task(send_telemetry())
    task2 = asyncio.create_task(receive_mode())
    
    try:
        await asyncio.gather(task1, task2)
    except WebSocketDisconnect:
        task1.cancel()
        task2.cancel()
        print("Client disconnected")

async def prune_stale_detections():
    """Remove detections older than 2 seconds to avoid stale data poisoning the fusion."""
    while True:
        await asyncio.sleep(1)
        now = time.time()
        async with DETECTION_LOCK:
            stale_keys = [k for k, v in MULTI_CAM_DETECTIONS.items() if v and (now - v["ts"] > 2)]
            for k in stale_keys:
                del MULTI_CAM_DETECTIONS[k]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
