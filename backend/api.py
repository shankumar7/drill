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
from backend.db.database import init_db, register_cadet, login_cadet, get_cadets, get_cadet_sessions, delete_cadet
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
    "active_mode": "CALIBRATION",
    "last_command": ""
}
ACTIVE_MODE = "CALIBRATION"
LOCKED_CADET_IDS: dict[int, int] = {}
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
    "side_camera_position": "right",
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
    side_camera_position: str | None = None
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
        return {
            "true_heel_dist": None,
            "true_toe_dist": None,
            "pose_scale": shoulder_pixel_width,
            "spine_length": spine_length
        }
        
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

from backend.io.camera import CameraReader
from queue import Queue, Empty

CAMERA_QUEUES = {0: Queue(maxsize=3), 1: Queue(maxsize=3), 2: Queue(maxsize=3)}
CAMERA_READERS = {}
ANNOTATED_FRAMES = {0: None, 1: None, 2: None}
RAW_FRAMES = {0: None, 1: None, 2: None}
ACTIVE_CLIENT_COUNTS = {0: 0, 1: 0, 2: 0}
CAMERA_LOCK = asyncio.Lock()

async def synchronized_inference_loop():
    import time
    while True:
        await asyncio.sleep(1/30)
        
        frames = {}
        for cam_id in [0, 1, 2]:
            q = CAMERA_QUEUES.get(cam_id)
            packet = None
            if q:
                try:
                    while not q.empty():
                        packet = q.get_nowait()
                except Empty:
                    pass
            if packet is not None:
                frames[cam_id] = packet.image

        if not frames:
            continue

        def _infer():
            for cam_id, frame in frames.items():
                if frame is None or pose_estimator is None:
                    continue
                try:
                    detections = pose_estimator.infer(frame)
                    if detections:
                        det = None
                        available_ids = [getattr(d, 'track_id', -1) for d in detections]
                        target_id = LOCKED_CADET_IDS.get(cam_id)
                        if target_id is not None:
                            for d in detections:
                                if getattr(d, 'track_id', None) == target_id:
                                    det = d
                                    break
                        if not det:
                            det = detections[0]
                            
                        det.foot_geometry = estimate_foot_geometry(det.keypoints)
                        shoulder_px = np.linalg.norm(det.keypoints[5, :2] - det.keypoints[6, :2])
                        if shoulder_px < 10: shoulder_px = 100
                        ppi = shoulder_px / 16.0
                        avg_conf = float(np.mean(det.keypoints[:, 2]))
                        
                        MULTI_CAM_DETECTIONS[cam_id] = {"det": det, "ts": time.time(), "ppi": ppi, "conf": avg_conf, "available_ids": available_ids, "all_dets": detections}
                        
                        RAW_FRAMES[cam_id] = frame.copy()
                        annotated = frame.copy()
                        if SETTINGS.get("show_skeleton", True):
                            _draw_skeleton(annotated, det.keypoints, color_name=SETTINGS.get("skeleton_color", "green"), opacity=SETTINGS.get("overlay_opacity", 0.8))
                        
                        tid = getattr(det, 'track_id', 'Unknown')
                        if tid is not None and SETTINGS.get("show_id_overlay", True):
                            cx, cy = int(det.bbox[0]), int(det.bbox[1])
                            cv2.putText(annotated, f"ID: {tid}", (cx, max(0, cy - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
                            
                        ANNOTATED_FRAMES[cam_id] = annotated
                    else:
                        MULTI_CAM_DETECTIONS[cam_id] = None
                        RAW_FRAMES[cam_id] = frame.copy()
                        ANNOTATED_FRAMES[cam_id] = frame.copy()
                except Exception as e:
                    import traceback
                    traceback.print_exc()
                    print(f"Error in ML pipeline: {e}")
                    
        await asyncio.to_thread(_infer)
 
async def generate_frames(camera_id: int, raw: bool = False):
    # Dynamic camera reader activation on client connection
    async with CAMERA_LOCK:
        ACTIVE_CLIENT_COUNTS[camera_id] += 1
        if CAMERA_READERS.get(camera_id) is None:
            try:
                CAMERA_READERS[camera_id] = CameraReader(camera_id, CAMERA_QUEUES[camera_id])
                CAMERA_READERS[camera_id].start()
                print(f"Dynamically started CameraReader for camera {camera_id} (Active clients: {ACTIVE_CLIENT_COUNTS[camera_id]})")
            except Exception as e:
                print(f"Failed to dynamically start camera {camera_id}: {e}")

    try:
        while True:
            frame = RAW_FRAMES.get(camera_id) if raw else ANNOTATED_FRAMES.get(camera_id)
            if frame is None:
                frame = np.ones((480, 640, 3), dtype=np.uint8) * 150
                cv2.putText(frame, f"CAM {camera_id} - WAITING", (150, 240), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                
            ret, buffer = cv2.imencode('.jpg', frame)
            yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
            await asyncio.sleep(1/30)
    finally:
        # Dynamic camera reader deactivation when stream disconnects
        async with CAMERA_LOCK:
            ACTIVE_CLIENT_COUNTS[camera_id] = max(0, ACTIVE_CLIENT_COUNTS[camera_id] - 1)
            if ACTIVE_CLIENT_COUNTS[camera_id] == 0:
                reader = CAMERA_READERS.pop(camera_id, None)
                if reader:
                    try:
                        reader.stop()
                        print(f"Dynamically stopped/released CameraReader for camera {camera_id}")
                    except Exception as e:
                        print(f"Error stopping camera {camera_id}: {e}")
                # Clear frames and queue
                RAW_FRAMES[camera_id] = None
                ANNOTATED_FRAMES[camera_id] = None
                # Drain the queue to prevent stale frames on next startup
                q = CAMERA_QUEUES.get(camera_id)
                if q:
                    while not q.empty():
                        try:
                            q.get_nowait()
                        except Empty:
                            break



class LockCadetRequest(BaseModel):
    track_id: int | None
    source_camera: int | None = None

class ModeRequest(BaseModel):
    mode: str

class RegisterRequest(BaseModel):
    name: str
    pin: str
    image: str
    unit: str | None = None
    instructor: str | None = None

class LoginRequest(BaseModel):
    pin: str

class SessionRequest(BaseModel):
    cadet_id: int
    drill_type: str
    score: float
    is_pass: bool
    cycle_count: int = 0

@app.post("/api/register")
async def api_register_cadet(req: RegisterRequest):
    try:
        cadet_id = register_cadet(req.name, req.pin, req.image, req.unit, req.instructor)
        return {"status": "ok", "cadet_id": cadet_id, "name": req.name}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/api/login")
async def api_login_cadet(req: LoginRequest):
    user = login_cadet(req.pin)
    if user:
        return {"status": "ok", "user": user}
    return {"status": "error", "message": "Invalid PIN"}

@app.get("/api/cadets")
async def api_get_cadets():
    cadets = get_cadets()
    return {"status": "ok", "cadets": cadets}

@app.get("/api/cadets/{cadet_id}/sessions")
async def api_get_cadet_sessions(cadet_id: int):
    try:
        sessions = get_cadet_sessions(cadet_id)
        return {"status": "ok", "sessions": sessions}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.delete("/api/cadets/{cadet_id}")
async def api_delete_cadet(cadet_id: int):
    try:
        delete_cadet(cadet_id)
        return {"status": "ok", "message": "Cadet deleted successfully"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/api/sessions")
async def api_save_session(req: SessionRequest):
    try:
        from backend.db.database import save_session
        session_id = save_session(req.cadet_id, req.drill_type, req.score, req.is_pass, req.cycle_count)
        return {"status": "ok", "session_id": session_id}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/api/lock_cadet")
async def lock_cadet(req: LockCadetRequest):
    global LOCKED_CADET_IDS
    if req.track_id is None:
        LOCKED_CADET_IDS = {}
        return {"status": "ok", "locked_ids": {}}
        
    src_cam = req.source_camera if req.source_camera is not None else 0
    LOCKED_CADET_IDS = {src_cam: req.track_id}
    
    async with DETECTION_LOCK:
        for cam_id, data in MULTI_CAM_DETECTIONS.items():
            if cam_id == src_cam:
                continue
            best_det = None
            best_score = -1
            for d in data.get("all_dets", []):
                shoulder_px = np.linalg.norm(d.keypoints[5, :2] - d.keypoints[6, :2])
                if shoulder_px > best_score:
                    best_score = shoulder_px
                    best_det = d
            if best_det and getattr(best_det, 'track_id', None) is not None:
                LOCKED_CADET_IDS[cam_id] = best_det.track_id

    return {"status": "ok", "locked_ids": LOCKED_CADET_IDS}

@app.post("/api/mode")
async def update_mode(req: ModeRequest):
    global ACTIVE_MODE, LATEST_TELEMETRY
    ACTIVE_MODE = req.mode
    if ACTIVE_MODE == "CALIBRATION":
        from backend.evaluation.rules.calibration import CALIBRATION_STATE
        CALIBRATION_STATE["step"] = 1
        CALIBRATION_STATE["front_cam_id"] = None
        CALIBRATION_STATE["side_cam_id"] = None
        CALIBRATION_STATE["back_cam_id"] = None
        CALIBRATION_STATE["locked_track_id"] = None
        CALIBRATION_STATE["completed"] = False
        CALIBRATION_STATE["last_success_time"] = 0
        global LOCKED_CADET_IDS
        LOCKED_CADET_IDS.clear()
        print("API mode change: Reset calibration state to step 1")
    if LATEST_TELEMETRY:
        LATEST_TELEMETRY["active_mode"] = ACTIVE_MODE
    print(f"Manual mode change: {ACTIVE_MODE}")
    return {"status": "ok", "mode": ACTIVE_MODE}

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
    SETTINGS["side_camera_position"] = "right"
    return {"status": "ok", "settings": SETTINGS}


from fastapi import UploadFile, File

@app.post("/api/voice_command")
async def process_voice_command(audio: UploadFile = File(...)):
    return {"error": "Voice commands disabled (Whisper removed)"}

@app.get("/api/video_feed/{camera_id}")
async def video_feed(camera_id: int, raw: bool = False):
    return StreamingResponse(generate_frames(camera_id, raw), media_type="multipart/x-mixed-replace; boundary=frame")

@app.get("/api/snapshot/{camera_id}")
async def get_snapshot(camera_id: int, raw: bool = True):
    import base64
    
    frame = None
    if CAMERA_READERS.get(camera_id) is not None:
        frame = RAW_FRAMES.get(camera_id) if raw else ANNOTATED_FRAMES.get(camera_id)
    else:
        try:
            temp_reader = CameraReader(camera_id, CAMERA_QUEUES[camera_id])
            temp_reader.start()
            await asyncio.sleep(0.5)
            ok, frame_img = temp_reader.capture.read()
            temp_reader.stop()
            if ok:
                frame = frame_img
        except Exception as e:
            print(f"Temp camera snapshot failed: {e}")

    if frame is None:
        frame = np.ones((480, 640, 3), dtype=np.uint8) * 150
        cv2.putText(frame, "NO SIGNAL", (200, 240), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
    ret, buffer = cv2.imencode('.jpg', frame)
    if not ret:
        return {"status": "error", "message": "Failed to encode frame"}
    b64_str = base64.b64encode(buffer).decode('utf-8')
    return {"status": "ok", "image": f"data:image/jpeg;base64,{b64_str}"}

@app.on_event("startup")
async def startup_event():
    init_db()
    asyncio.create_task(fusion_evaluator_loop())
    asyncio.create_task(prune_stale_detections())
    asyncio.create_task(synchronized_inference_loop())

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
            
            camera_mapping = SETTINGS.get("camera_mapping", {"front": 0, "side": 1, "back": 2})
            id_to_type = {v: k for k, v in camera_mapping.items()}
            
            for cam_id, entry in detections_snapshot.items():
                if not entry:
                    continue
                
                camera_type = id_to_type.get(cam_id, "front")
                det = entry["det"]
                all_dets = entry.get("all_dets", [det])
                conf = entry.get("conf", 1.0)
                evaluation = evaluator.evaluate(det, all_dets, camera_type=camera_type)
                
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
            
            if not fused_scores:
                status = "Initializing..."
            else:
                any_fail = any(r.status == "fail" for r in fused_results.values())
                status = "PASS" if (overall_score >= SETTINGS["pass_threshold"] and not any_fail) else "FAIL"

            def get_payload(rule_name):
                res = fused_results.get(rule_name)
                if not res:
                    return {"status": "not_evaluable", "reason": "No data"}
                return {"status": res.status, "reason": res.message}
                
            all_ids = set()
            for entry in detections_snapshot.values():
                if entry and "available_ids" in entry:
                    all_ids.update(entry["available_ids"])
            
            new_telemetry = {
                "active_mode": ACTIVE_MODE,
                "detected_ids": list(all_ids)
            }
            
            if ACTIVE_MODE == "CALIBRATION":
                from backend.evaluation.rules.calibration import CALIBRATION_STATE
                import time
                if not CALIBRATION_STATE["completed"]:
                    passed_cams = []
                    for cam_id, entry in detections_snapshot.items():
                        if not entry: continue
                        det = entry["det"]
                        evaluation = evaluator.evaluate(det, camera_type="front")
                        if evaluation.rules and evaluation.rules[0].status == "pass":
                            passed_cams.append((cam_id, getattr(det, 'track_id', None)))
                    
                    if passed_cams:
                        step = CALIBRATION_STATE["step"]
                        if step == 1:
                            front_cam, track_id = passed_cams[0]
                            CALIBRATION_STATE["front_cam_id"] = front_cam
                            CALIBRATION_STATE["locked_track_id"] = track_id
                            CALIBRATION_STATE["step"] = 2
                            CALIBRATION_STATE["last_success_time"] = time.time()
                            global LOCKED_CADET_IDS
                            LOCKED_CADET_IDS = {front_cam: track_id}
                        elif step == 2:
                            for c, t in passed_cams:
                                if c == CALIBRATION_STATE["front_cam_id"]:
                                    CALIBRATION_STATE["locked_track_id"] = t
                                    CALIBRATION_STATE["step"] = 3
                                    CALIBRATION_STATE["last_success_time"] = time.time()
                                    break
                        elif step == 3:
                            for c, t in passed_cams:
                                if c == CALIBRATION_STATE["front_cam_id"]:
                                    CALIBRATION_STATE["locked_track_id"] = t
                                    CALIBRATION_STATE["completed"] = True
                                    CALIBRATION_STATE["last_success_time"] = time.time()
                                    remaining = [cam for cam in [0,1,2] if cam != c]
                                    if len(remaining) >= 2:
                                        SETTINGS["camera_mapping"] = {"front": c, "side": remaining[0], "back": remaining[1]}
                                    for all_c in [0, 1, 2]:
                                        LOCKED_CADET_IDS[all_c] = CALIBRATION_STATE["locked_track_id"]
                                    break

                new_telemetry.update({
                    "calibration_step": CALIBRATION_STATE["step"],
                    "calibration_completed": CALIBRATION_STATE["completed"],
                    "locked_track_id": CALIBRATION_STATE.get("locked_track_id"),
                    "overall_score": 100 if CALIBRATION_STATE["completed"] else 0,
                    "status": "PASS" if CALIBRATION_STATE["completed"] else "Initializing..."
                })

            elif ACTIVE_MODE == "SAVDHAN":
                new_telemetry.update({
                    "torso_posture": get_payload("Body Posture"),
                    "heel_alignment": get_payload("Heel contact"),
                    "foot_angle": get_payload("Foot angle"),
                    "arm_alignment": get_payload("Arms at sides"),
                    "knee_tightness": get_payload("Knee distance"),
                    "overall_score": overall_score,
                    "status": status
                })
            elif ACTIVE_MODE == "VISHRAM":
                new_telemetry.update({
                    "heel_distance": get_payload("Foot spacing"),
                    "toe_distance": get_payload("Foot spacing"),
                    "knee_tightness": get_payload("Knee lock"),
                    "hands_behind_back": get_payload("Hands behind back"),
                    "torso_posture": get_payload("Body Posture"),
                    "overall_score": overall_score,
                    "status": status
                })
            elif ACTIVE_MODE == "AARAM_SE":
                new_telemetry.update({
                    "heel_distance": get_payload("Foot spacing"),
                    "toe_distance": get_payload("Foot spacing"),
                    "overall_score": overall_score,
                    "status": status
                })
            elif ACTIVE_MODE in ["FRONT_SALUTE", "BAYE_SALUTE", "DAINE_SALUTE"]:
                new_telemetry.update({
                    "torso_posture": get_payload("Body Posture"),
                    "salute_arm_angle": get_payload("Saluting Arm Angle"),
                    "straight_arm_angle": get_payload("Straight Arm Angle"),
                    "head_direction": get_payload("Head Direction"),
                    "salute_hand_position": get_payload("Saluting Hand Position"),
                    "overall_score": overall_score,
                    "status": status
                })
            elif ACTIVE_MODE == "DAHINE_MURH":
                new_telemetry.update({
                    "torso_posture": get_payload("Body Posture"),
                    "arm_alignment": get_payload("Right Turn (Dahine Murh)"),
                    "heel_alignment": get_payload("Right Turn (Dahine Murh)"),
                    "foot_angle": get_payload("Right Turn (Dahine Murh)"),
                    "overall_score": overall_score,
                    "status": status
                })
            elif ACTIVE_MODE == "BAYEN_MURH":
                new_telemetry.update({
                    "torso_posture": get_payload("Body Posture"),
                    "arm_alignment": get_payload("Left Turn (Bayen Murh)"),
                    "heel_alignment": get_payload("Left Turn (Bayen Murh)"),
                    "foot_angle": get_payload("Left Turn (Bayen Murh)"),
                    "overall_score": overall_score,
                    "status": status
                })
            elif ACTIVE_MODE == "PICHHE_MURH":
                new_telemetry.update({
                    "torso_posture": get_payload("Body Posture"),
                    "arm_alignment": get_payload("About Turn (Pichhe Murh)"),
                    "heel_alignment": get_payload("About Turn (Pichhe Murh)"),
                    "foot_angle": get_payload("About Turn (Pichhe Murh)"),
                    "overall_score": overall_score,
                    "status": status
                })
            elif ACTIVE_MODE == "KHULI_LINE_CHAL":
                new_telemetry.update({
                    "torso_posture": get_payload("Body Posture"),
                    "arm_alignment": get_payload("Open Line Chal (Khuli Line)"),
                    "heel_distance": get_payload("Open Line Chal (Khuli Line)"),
                    "toe_distance": get_payload("Open Line Chal (Khuli Line)"),
                    "overall_score": overall_score,
                    "status": status
                })
            elif ACTIVE_MODE == "NIKAT_LINE_CHAL":
                new_telemetry.update({
                    "torso_posture": get_payload("Body Posture"),
                    "arm_alignment": get_payload("Close Line Chal (Nikat Line)"),
                    "heel_distance": get_payload("Close Line Chal (Nikat Line)"),
                    "toe_distance": get_payload("Close Line Chal (Nikat Line)"),
                    "overall_score": overall_score,
                    "status": status
                })
            elif ACTIVE_MODE == "SAJ":
                new_telemetry.update({
                    "torso_posture": get_payload("Body Posture"),
                    "arm_alignment": get_payload("Squad Alignment (Saj)"),
                    "overall_score": overall_score,
                    "status": status
                })
            elif ACTIVE_MODE == "VISARJAN":
                new_telemetry.update({
                    "torso_posture": get_payload("Body Posture"),
                    "arm_alignment": get_payload("Visarjan Sequence"),
                    "overall_score": overall_score,
                    "status": status
                })
            elif ACTIVE_MODE == "TEJ_CHAL":
                new_telemetry.update({
                    "torso_posture": get_payload("Body Posture"),
                    "arm_alignment": get_payload("Tej Chal (Quick March)"),
                    "overall_score": overall_score,
                    "status": status
                })
            elif ACTIVE_MODE == "THAAM":
                new_telemetry.update({
                    "torso_posture": get_payload("Body Posture"),
                    "arm_alignment": get_payload("Thaam (Halt from March)"),
                    "overall_score": overall_score,
                    "status": status
                })
            elif ACTIVE_MODE in ["MARCHING_FRONT_SALUTE", "MARCHING_BAYE_SALUTE", "MARCHING_DAINE_SALUTE"]:
                dir_label = "Front" if "FRONT" in ACTIVE_MODE else "Left" if "BAYE" in ACTIVE_MODE else "Right"
                new_telemetry.update({
                    "torso_posture": get_payload("Body Posture"),
                    "arm_alignment": get_payload(f"Marching Salute ({dir_label})"),
                    "overall_score": overall_score,
                    "status": status
                })
            elif ACTIVE_MODE in ["MARCHING_TURN_DAHINE", "MARCHING_TURN_BAYEN", "MARCHING_TURN_PICHHE"]:
                turn_label = "Dahine" if "DAHINE" in ACTIVE_MODE else "Bayen" if "BAYEN" in ACTIVE_MODE else "Pichhe"
                new_telemetry.update({
                    "torso_posture": get_payload("Body Posture"),
                    "arm_alignment": get_payload(f"Marching Turn ({turn_label})"),
                    "overall_score": overall_score,
                    "status": status
                })
                
            # Assign atomically to the global dictionary so the websocket picks it up instantly
            LATEST_TELEMETRY = new_telemetry
        except Exception as e:
            import traceback
            with open("fusion_error.txt", "a") as f:
                f.write(traceback.format_exc() + "\n")
            print(f"Fusion error: {e}")

@app.websocket("/ws/telemetry")
async def websocket_telemetry(websocket: WebSocket):
    global ACTIVE_MODE
    await websocket.accept()
    
    # Reset calibration state on new websocket connection if we are in CALIBRATION mode
    if ACTIVE_MODE == "CALIBRATION":
        from backend.evaluation.rules.calibration import CALIBRATION_STATE
        CALIBRATION_STATE["step"] = 1
        CALIBRATION_STATE["front_cam_id"] = None
        CALIBRATION_STATE["side_cam_id"] = None
        CALIBRATION_STATE["back_cam_id"] = None
        CALIBRATION_STATE["locked_track_id"] = None
        CALIBRATION_STATE["completed"] = False
        CALIBRATION_STATE["last_success_time"] = 0
        global LOCKED_CADET_IDS
        LOCKED_CADET_IDS.clear()
        print("Websocket connected: Reset calibration state to step 1")
    
    async def send_telemetry():
        while True:
            try:
                await websocket.send_text(json.dumps(LATEST_TELEMETRY))
                await asyncio.sleep(0.5)
            except Exception:
                break

    async def receive_mode():
        global ACTIVE_MODE, LATEST_TELEMETRY
        while True:
            try:
                data = await websocket.receive_text()
                msg = json.loads(data)
                if "mode" in msg:
                    ACTIVE_MODE = msg["mode"].upper()
                    # Fix spelling mismatch from UI "Savadhan" vs backend "SAVDHAN"
                    if ACTIVE_MODE == "SAVADHAN":
                        ACTIVE_MODE = "SAVDHAN"
                    if ACTIVE_MODE == "CALIBRATION":
                        from backend.evaluation.rules.calibration import CALIBRATION_STATE
                        CALIBRATION_STATE["step"] = 1
                        CALIBRATION_STATE["front_cam_id"] = None
                        CALIBRATION_STATE["side_cam_id"] = None
                        CALIBRATION_STATE["back_cam_id"] = None
                        CALIBRATION_STATE["locked_track_id"] = None
                        CALIBRATION_STATE["completed"] = False
                        CALIBRATION_STATE["last_success_time"] = 0
                        LOCKED_CADET_IDS.clear()
                        print("Websocket mode change: Reset calibration state to step 1")
                    LATEST_TELEMETRY["active_mode"] = ACTIVE_MODE
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
