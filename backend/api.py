import cv2
import asyncio
import json
import numpy as np
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import time

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
    "overall_score": 0,
    "status": "Initializing..."
}
ACTIVE_MODE = "SAVDHAN"

pose_estimator = None
try:
    from backend.inference.pose_estimator import YoloPoseEstimator
    pose_estimator = YoloPoseEstimator(
        model_path="yolo11n-pose.pt",
        confidence=0.5,
        image_size=640,
        prefer_half_precision=False,
        tracking_enabled=False,
        tracker_config=None
    )
    print("Pose Estimator loaded in API.")
except Exception as e:
    print(f"Failed to load Pose Estimator: {e}")

# Helper to map pixel distance to inches based on a heuristic (shoulder width ~16 inches)
def estimate_foot_geometry(keypoints):
    from backend.evaluation.geometry import segment_length
    # 5: L Shoulder, 6: R Shoulder, 15: L Ankle, 16: R Ankle, 11: L Hip, 12: R Hip
    l_shoulder, r_shoulder = keypoints[5, :2], keypoints[6, :2]
    shoulder_pixel_width = segment_length(l_shoulder, r_shoulder)
    
    if shoulder_pixel_width < 10:
        shoulder_pixel_width = 100 # Fallback
    
    pixels_per_inch = shoulder_pixel_width / 16.0 
    
    l_ankle, r_ankle = keypoints[15, :2], keypoints[16, :2]
    # Simple heuristic: ankles represent heels, and toes are slightly further apart
    heel_dist_px = segment_length(l_ankle, r_ankle)
    heel_dist_in = heel_dist_px / pixels_per_inch
    
    # We fake toe distance based on heel distance + 6 inches for the V-shape
    toe_dist_in = heel_dist_in + 6.0 
    
    return {
        "heel_to_heel_in": heel_dist_in,
        "toe_to_toe_in": toe_dist_in
    }

async def generate_frames(camera_id: int):
    global LATEST_TELEMETRY, ACTIVE_MODE
    if camera_id not in [0, 1]:
        while True:
            frame = np.ones((480, 640, 3), dtype=np.uint8) * 50
            cv2.putText(frame, "INVALID CAMERA ID", (150, 240), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            ret, buffer = cv2.imencode('.jpg', frame)
            yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
            await asyncio.sleep(1)

    cap = cv2.VideoCapture(camera_id)
    if not cap.isOpened():
        while True:
            frame = np.ones((480, 640, 3), dtype=np.uint8) * 150
            cv2.putText(frame, f"CAM {camera_id} - NO SIGNAL", (150, 240), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            ret, buffer = cv2.imencode('.jpg', frame)
            yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
            await asyncio.sleep(0.1)
            
    while True:
        success, frame = cap.read()
        if not success:
            break
        
        # Only run ML on camera 1 to save processing
        if camera_id == 1 and pose_estimator:
            try:
                from backend.evaluation.evaluator import StaticPostureEvaluator
                evaluator = StaticPostureEvaluator(ACTIVE_MODE)
                
                detections = pose_estimator.infer(frame)
                if detections:
                    det = detections[0]
                    det.foot_geometry = estimate_foot_geometry(det.keypoints)
                    evaluation = evaluator.evaluate(det)
                    
                    scores = {}
                    for r in evaluation.rules:
                        scores[r.name] = r.score if r.score is not None else 0
                    
                    # Map rule names to telemetry keys
                    if ACTIVE_MODE == "SAVDHAN":
                        LATEST_TELEMETRY.update({
                            "torso_posture": scores.get("Shoulder level", 0),
                            "heel_alignment": scores.get("Heel contact", 0),
                            "foot_angle": scores.get("Foot angle", 0),
                            "arm_alignment": scores.get("Arm position", 0),
                            "overall_score": evaluation.overall_score or 0,
                            "status": evaluation.status.replace("_", " ").title()
                        })
                    elif ACTIVE_MODE == "VISHRAM":
                        LATEST_TELEMETRY.update({
                            "heel_distance": scores.get("Foot spacing", 0),
                            "toe_distance": scores.get("Foot spacing", 0),
                            "knee_tightness": scores.get("Knee lock", 0),
                            "hands_behind_back": scores.get("Hands behind back", 0),
                            "overall_score": evaluation.overall_score or 0,
                            "status": evaluation.status.replace("_", " ").title()
                        })
                    
                    # Draw skeleton for vis
                    from backend.visualization.debug_view import _draw_skeleton
                    _draw_skeleton(frame, det.keypoints)
            except Exception as e:
                print(f"Error in ML pipeline: {e}")

        cv2.putText(frame, f"CAM {camera_id} - {ACTIVE_MODE}", (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        ret, buffer = cv2.imencode('.jpg', frame)
        yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
        await asyncio.sleep(0.03)

@app.get("/api/video_feed/{camera_id}")
async def video_feed(camera_id: int):
    return StreamingResponse(generate_frames(camera_id), media_type="multipart/x-mixed-replace; boundary=frame")

@app.websocket("/ws/telemetry")
async def websocket_telemetry(websocket: WebSocket):
    global ACTIVE_MODE
    await websocket.accept()
    
    async def send_telemetry():
        while True:
            await websocket.send_text(json.dumps(LATEST_TELEMETRY))
            await asyncio.sleep(0.5)

    async def receive_mode():
        global ACTIVE_MODE
        while True:
            try:
                data = await websocket.receive_text()
                msg = json.loads(data)
                if "mode" in msg:
                    ACTIVE_MODE = msg["mode"].upper()
                    print(f"Switched mode to: {ACTIVE_MODE}")
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
