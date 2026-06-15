import cv2
import mediapipe as mp
import os
import json
import glob

def get_fps(video_path):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return None
    fps = cap.get(cv2.CAP_PROP_FPS)
    cap.release()
    return fps

def process_videos(drill_name, input_dir, output_path):
    print(f"Processing {drill_name} from {input_dir}")
    mp_pose = mp.solutions.pose
    mp_drawing = mp.solutions.drawing_utils
    
    views = ['front', 'side', 'back']
    available_views = {}
    for v in views:
        p = os.path.join(input_dir, f"{v}.mp4")
        if os.path.exists(p):
            available_views[v] = p
            
    if not available_views:
        print(f"No valid videos found for {drill_name}")
        return

    poses = {v: mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) for v in available_views}
    caps = {v: cv2.VideoCapture(p) for v, p in available_views.items()}

    fps = get_fps(list(available_views.values())[0]) or 30.0

    target_height = 480
    def resize_frame(frame, target_h):
        h, w = frame.shape[:2]
        ratio = target_h / float(h)
        target_w = int(w * ratio)
        return cv2.resize(frame, (target_w, target_h))

    # Read first frames
    frames = {}
    for v, cap in caps.items():
        ret, f = cap.read()
        if not ret:
            print(f"Error reading {v} for {drill_name}")
            return
        frames[v] = resize_frame(f, target_height)

    # Reset
    for cap in caps.values():
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

    out_w = sum(f.shape[1] for f in frames.values())
    out_h = target_height

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (out_w, out_h))

    frame_count = 0
    while True:
        current_frames = {}
        all_ret = True
        for v, cap in caps.items():
            ret, f = cap.read()
            if not ret:
                all_ret = False
                break
            current_frames[v] = f
            
        if not all_ret:
            break

        disp_frames = []
        for v in views:
            if v in current_frames:
                f = current_frames[v]
                rgb = cv2.cvtColor(f, cv2.COLOR_BGR2RGB)
                res = poses[v].process(rgb)
                if res.pose_landmarks:
                    mp_drawing.draw_landmarks(f, res.pose_landmarks, mp_pose.POSE_CONNECTIONS)
                
                disp = resize_frame(f, target_height)
                cv2.putText(disp, v.capitalize(), (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                disp_frames.append(disp)

        combined = cv2.hconcat(disp_frames)
        out.write(combined)
        frame_count += 1

    out.release()
    for cap in caps.values():
        cap.release()
        
    print(f"Saved {drill_name} to {output_path}")

if __name__ == "__main__":
    home = os.path.expanduser('~')
    desktop = os.path.join(home, 'Desktop')
    dataset_dir = os.path.join(desktop, 'Drill Footages', 'Dataset')
    
    if not os.path.exists(dataset_dir):
        print(f"Dataset directory not found: {dataset_dir}")
        exit()
        
    drills = [d for d in os.listdir(dataset_dir) if os.path.isdir(os.path.join(dataset_dir, d))]
    for drill in drills:
        take1_dir = os.path.join(dataset_dir, drill, 'take_1')
        if os.path.isdir(take1_dir):
            out_path = os.path.join(desktop, f"{drill.lower()}_synced_output.mp4")
            if not os.path.exists(out_path): # Skip if already exists
                process_videos(drill, take1_dir, out_path)
