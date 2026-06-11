import cv2
import mediapipe as mp
import os
import json

def get_fps(video_path):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error opening video {video_path}")
        return None
    fps = cap.get(cv2.CAP_PROP_FPS)
    cap.release()
    return fps

def process_videos(front_path, back_path, side_path, offsets, output_path, json_path):
    print("Initializing MediaPipe Pose...")
    mp_pose = mp.solutions.pose
    mp_drawing = mp.solutions.drawing_utils
    
    # Initialize 3 separate pose estimators (one for each view)
    pose_front = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
    pose_back = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
    pose_side = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)

    caps = {
        'front': cv2.VideoCapture(front_path),
        'back': cv2.VideoCapture(back_path),
        'side': cv2.VideoCapture(side_path)
    }

    fps = get_fps(front_path) or 30.0
    print(f"Assuming video FPS: {fps}")

    # Calculate frames to skip
    frames_to_skip = {
        'front': int(offsets['front'] * fps),
        'back': int(offsets['back'] * fps),
        'side': int(offsets['side'] * fps)
    }

    print(f"Skipping frames - Front: {frames_to_skip['front']}, Back: {frames_to_skip['back']}, Side: {frames_to_skip['side']}")

    # Fast-forward videos
    for view, cap in caps.items():
        for _ in range(frames_to_skip[view]):
            ret, _ = cap.read()
            if not ret:
                print(f"Warning: Reached end of {view} video while skipping.")
                break

    # Setup video writer
    # Assuming all videos have same resolution. Let's read first frame to get size.
    rets = {view: cap.read()[0] for view, cap in caps.items()}
    frames = {view: cap.read()[1] for view, cap in caps.items()}
    
    # reset back to start of sequence
    for view, cap in caps.items():
        cap.set(cv2.CAP_PROP_POS_FRAMES, frames_to_skip[view])

    # We will stack them horizontally: front, side, back
    # Let's resize each to a standard height to ensure they fit well side-by-side
    target_height = 480
    
    def resize_frame(frame, target_h):
        h, w = frame.shape[:2]
        ratio = target_h / float(h)
        target_w = int(w * ratio)
        return cv2.resize(frame, (target_w, target_h))

    # Read first frame to get output dimensions
    ret_f, f_frame = caps['front'].read()
    ret_b, b_frame = caps['back'].read()
    ret_s, s_frame = caps['side'].read()
    
    if not (ret_f and ret_b and ret_s):
        print("Error: Could not read starting frames from videos.")
        return

    f_frame = resize_frame(f_frame, target_height)
    b_frame = resize_frame(b_frame, target_height)
    s_frame = resize_frame(s_frame, target_height)

    out_w = f_frame.shape[1] + s_frame.shape[1] + b_frame.shape[1]
    out_h = target_height

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (out_w, out_h))

    print(f"Creating synced video at {output_path} with resolution {out_w}x{out_h}")

    # reset caps again
    for view, cap in caps.items():
        cap.set(cv2.CAP_PROP_POS_FRAMES, frames_to_skip[view])

    frame_count = 0
    extracted_data = []

    print("Processing frames...")
    while True:
        ret_f, frame_f = caps['front'].read()
        ret_b, frame_b = caps['back'].read()
        ret_s, frame_s = caps['side'].read()

        if not (ret_f and ret_b and ret_s):
            print("Reached end of one or more videos.")
            break

        # Process Front
        rgb_f = cv2.cvtColor(frame_f, cv2.COLOR_BGR2RGB)
        res_f = pose_front.process(rgb_f)
        if res_f.pose_landmarks:
            mp_drawing.draw_landmarks(frame_f, res_f.pose_landmarks, mp_pose.POSE_CONNECTIONS)
            
        # Process Back
        rgb_b = cv2.cvtColor(frame_b, cv2.COLOR_BGR2RGB)
        res_b = pose_back.process(rgb_b)
        if res_b.pose_landmarks:
            mp_drawing.draw_landmarks(frame_b, res_b.pose_landmarks, mp_pose.POSE_CONNECTIONS)

        # Process Side
        rgb_s = cv2.cvtColor(frame_s, cv2.COLOR_BGR2RGB)
        res_s = pose_side.process(rgb_s)
        if res_s.pose_landmarks:
            mp_drawing.draw_landmarks(frame_s, res_s.pose_landmarks, mp_pose.POSE_CONNECTIONS)

        # Extract data to save
        frame_data = {
            "frame": frame_count,
            "timestamp_sec": frame_count / fps,
            "poses": {
                "front": [{"x": lm.x, "y": lm.y, "z": lm.z, "v": lm.visibility} for lm in res_f.pose_landmarks.landmark] if res_f.pose_landmarks else None,
                "back": [{"x": lm.x, "y": lm.y, "z": lm.z, "v": lm.visibility} for lm in res_b.pose_landmarks.landmark] if res_b.pose_landmarks else None,
                "side": [{"x": lm.x, "y": lm.y, "z": lm.z, "v": lm.visibility} for lm in res_s.pose_landmarks.landmark] if res_s.pose_landmarks else None,
            }
        }
        extracted_data.append(frame_data)

        # Resize for stacking
        f_disp = resize_frame(frame_f, target_height)
        s_disp = resize_frame(frame_s, target_height)
        b_disp = resize_frame(frame_b, target_height)

        # Stack horizontally: Front, Side, Back
        combined = cv2.hconcat([f_disp, s_disp, b_disp])
        
        # Add labels
        cv2.putText(combined, "Front", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(combined, "Side", (f_disp.shape[1] + 10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(combined, "Back", (f_disp.shape[1] + s_disp.shape[1] + 10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        out.write(combined)
        frame_count += 1

        if frame_count % 30 == 0:
            print(f"Processed {frame_count} frames...")

    out.release()
    for cap in caps.values():
        cap.release()

    with open(json_path, 'w') as f:
        json.dump(extracted_data, f)
        
    print(f"\nDone! Output saved to: \n- {output_path}\n- {json_path}")

if __name__ == "__main__":
    home = os.path.expanduser('~')
    desktop = os.path.join(home, 'Desktop')
    
    process_videos(
        front_path=os.path.join(desktop, 'front.mp4'),
        back_path=os.path.join(desktop, 'back.mp4'),
        side_path=os.path.join(desktop, 'side.mp4'),
        offsets={
            'front': 1.034, # 1 second + 1 frame
            'back': 3.138,  # 3 seconds + 4 frames
            'side': 0.0   # 0 seconds
        },
        output_path=os.path.join(desktop, 'savadhan_synced_output.mp4'),
        json_path=os.path.join(desktop, 'savadhan_keypoints.json')
    )
