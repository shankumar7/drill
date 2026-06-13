import os
import cv2
import json
import time
from tqdm import tqdm
from backend.inference.pose_estimator import YoloPoseEstimator

dataset_dir = "/Users/shankumar/Desktop/Drill Footages/Dataset"
output_log = "/Users/shankumar/Desktop/Drill Footages/processing_log.txt"

def process_dataset():
    print("Loading YOLO Pose Estimator...")
    pose_estimator = YoloPoseEstimator(
        model_path="yolo11n-pose.pt",
        confidence=0.5,
        image_size=640,
        prefer_half_precision=False,
        tracking_enabled=False
    )
    
    # Collect all take directories
    tasks = []
    for drill in os.listdir(dataset_dir):
        drill_path = os.path.join(dataset_dir, drill)
        if not os.path.isdir(drill_path):
            continue
        for take in os.listdir(drill_path):
            take_path = os.path.join(drill_path, take)
            if not os.path.isdir(take_path):
                continue
            tasks.append((drill, take, take_path))
            
    print(f"Found {len(tasks)} tasks to process.")
    
    for drill, take, take_path in tqdm(tasks, desc="Processing Takes"):
        out_json = os.path.join(take_path, "keypoints.json")
        if os.path.exists(out_json):
            # Skip if already processed to allow resuming
            continue
            
        take_data = {
            "drill": drill,
            "take": take,
            "fps": None,
            "frames": {}
        }
        
        # Open available videos
        caps = {}
        for view in ["front", "side", "back"]:
            vid_path = os.path.join(take_path, f"{view}.mp4")
            if os.path.exists(vid_path):
                caps[view] = cv2.VideoCapture(vid_path)
                if take_data["fps"] is None:
                    take_data["fps"] = caps[view].get(cv2.CAP_PROP_FPS) or 30.0
                    
        if not caps:
            continue
            
        frame_idx = 0
        while True:
            active_videos = False
            frame_data = {}
            for view, cap in caps.items():
                ret, frame = cap.read()
                if ret:
                    active_videos = True
                    # Process every 3rd frame to save time (approx 10 FPS)
                    if frame_idx % 3 == 0:
                        detections = pose_estimator.infer(frame)
                        if detections:
                            # Keep only the primary detection
                            det = detections[0]
                            kpts = []
                            for kp in det.keypoints:
                                kpts.append({
                                    "x": float(kp[0]),
                                    "y": float(kp[1]),
                                    "conf": float(kp[2])
                                })
                            frame_data[view] = kpts
            
            if not active_videos:
                break
                
            if frame_data:
                take_data["frames"][frame_idx] = frame_data
                
            frame_idx += 1
            
        # Save JSON
        with open(out_json, "w") as f:
            json.dump(take_data, f)
            
        # Clean up caps
        for cap in caps.values():
            cap.release()

if __name__ == "__main__":
    process_dataset()
    print("Batch processing complete.")
