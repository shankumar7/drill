import cv2
import asyncio
import json
import numpy as np
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Military Drill Analysis API")

# Enable CORS for the Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simulated camera generator
async def generate_frames(camera_id: int):
    cap = cv2.VideoCapture(camera_id)
    if not cap.isOpened():
        # Yield dummy gray frame if camera not found
        while True:
            frame = np.ones((480, 640, 3), dtype=np.uint8) * 150
            cv2.putText(frame, f"CAM {camera_id} - NO SIGNAL", (150, 240), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            ret, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            await asyncio.sleep(0.1)
            
    while True:
        success, frame = cap.read()
        if not success:
            break
        else:
            # Add simple text for testing
            cv2.putText(frame, f"CAM {camera_id}", (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            ret, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        
        await asyncio.sleep(0.03)

@app.get("/api/video_feed/{camera_id}")
async def video_feed(camera_id: int):
    return StreamingResponse(generate_frames(camera_id), media_type="multipart/x-mixed-replace; boundary=frame")

@app.websocket("/ws/telemetry")
async def websocket_telemetry(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # Send mock telemetry data for the gauges
            import random
            data = {
                "torso_posture": random.randint(70, 100),
                "heel_alignment": random.randint(70, 100),
                "foot_angle": random.randint(70, 100),
                "arm_alignment": random.randint(70, 100),
                "overall_score": random.randint(75, 100),
                "status": random.choice(["Excellent", "Good", "Needs Improvement"])
            }
            await websocket.send_text(json.dumps(data))
            await asyncio.sleep(0.5)
    except WebSocketDisconnect:
        print("Client disconnected")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
