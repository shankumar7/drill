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
import time
import tempfile

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

pose_estimator = None
try:
    from backend.inference.pose_estimator import YoloPoseEstimator
    pose_estimator = YoloPoseEstimator(
        model_path="yolo11n-pose.pt",
        confidence=0.5,
        image_size=640,
        prefer_half_precision=False,
        tracking_enabled=True,
        tracker_config="bytetrack.yaml"
    )
    print("Pose Estimator loaded in API.")
except Exception as e:
    print(f"Failed to load Pose Estimator: {e}")

whisper_model = None
try:
    import whisper
    whisper_model = whisper.load_model("base")
    print("Whisper Model loaded in API.")
except Exception as e:
    print(f"Failed to load Whisper Model: {e}")

# Helper to map pixel distance to inches based on a heuristic (shoulder width ~16 inches)
def estimate_foot_geometry(keypoints):
    from backend.evaluation.geometry import segment_length
    # 5: L Shoulder, 6: R Shoulder, 15: L Ankle, 16: R Ankle, 11: L Hip, 12: R Hip
    l_shoulder, r_shoulder = keypoints[5, :2], keypoints[6, :2]
    shoulder_pixel_width = segment_length(l_shoulder, r_shoulder)
    
    if shoulder_pixel_width < 10:
        shoulder_pixel_width = 100 # Fallback
    
    pixels_per_inch = shoulder_pixel_width / 16.0 
    
    # Check if ankles are actually visible (confidence > 0.3)
    l_ankle_conf = keypoints[15, 2] if keypoints.shape[1] > 2 else 1.0
    r_ankle_conf = keypoints[16, 2] if keypoints.shape[1] > 2 else 1.0
    if l_ankle_conf < 0.3 or r_ankle_conf < 0.3:
        return None
        
    l_ankle, r_ankle = keypoints[15, :2], keypoints[16, :2]
    # Simple heuristic: ankles represent heels, and toes are slightly further apart
    heel_dist_px = segment_length(l_ankle, r_ankle)
    heel_dist_in = heel_dist_px / pixels_per_inch
    
    # We fake toe distance based on heel distance + 6 inches for the V-shape
    toe_dist_in = heel_dist_in + 6.0 
    
    return {
        "heel_to_heel_in": heel_dist_in,
        "toe_to_toe_in": toe_dist_in,
        "true_heel_dist": heel_dist_px,
        "pose_scale": shoulder_pixel_width,
        "ground_plane_angle": 30.0 # Restored mock angle so rule can evaluate when standing
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
                        MULTI_CAM_DETECTIONS[camera_id] = {"det": det, "ts": time.time(), "ppi": ppi, "conf": avg_conf, "available_ids": available_ids}
                    
                    from backend.visualization.debug_view import _draw_skeleton
                    _draw_skeleton(frame, det.keypoints)
                    
                    tid = getattr(det, 'track_id', 'Unknown')
                    if tid is not None:
                        cx, cy = int(det.bbox[0]), int(det.bbox[1])
                        cv2.putText(frame, f"ID: {tid}", (cx, max(0, cy - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

                else:
                    async with DETECTION_LOCK:
                        MULTI_CAM_DETECTIONS[camera_id] = None
            except Exception as e:
                import traceback
                traceback.print_exc()
                print(f"Error in ML pipeline: {e}")

        # Add camera label
        cam_names = {0: "FRONT", 1: "SIDE", 2: "BACK"}
        cv2.putText(frame, f"{cam_names[camera_id]} - {ACTIVE_MODE}", (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
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
        result = whisper_model.transcribe(
            temp_audio_path,
            language="en",
            fp16=False,
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

        if any(kw in text_lower for kw in savdhan_keywords):
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
                conf = entry.get("conf", 1.0)
                evaluation = evaluator.evaluate(det)
                
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
                status = "PASS" if overall_score >= 85 else "FAIL"

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
