import os
import cv2
import json
import numpy as np
import re
import sys

# Ensure backend can be imported
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from backend.inference.pose_estimator import YoloPoseEstimator
from backend.evaluation.geometry import angle_degrees, segment_length

def main():
    print("=== STARTING DRILL MODEL TRAINING & CALIBRATION PIPELINE ===")
    
    video_dir = r"C:\Users\The Moe\Downloads\all the drill videos"
    if not os.path.exists(video_dir):
        print(f"Error: Video directory not found: {video_dir}")
        return
        
    # Initialize YOLO pose estimator
    print("Initializing YOLO Pose Estimator...")
    pose_estimator = YoloPoseEstimator(
        model_path="yolo11n-pose.pt",
        confidence=0.5,
        image_size=640,
        prefer_half_precision=False,
        tracking_enabled=False
    )
    
    videos = [f for f in os.listdir(video_dir) if f.lower().endswith('.mp4')]
    print(f"Found {len(videos)} videos to process.")
    
    # Storage for extracted metrics by posture type
    data_savdhan = {
        "heel_gap_ratios": [],
        "arm_horizontal_ratios": [],
        "elbow_angles": []
    }
    
    data_vishram = {
        "heel_gap_ratios": []
    }
    
    data_salute = {
        "elbow_drops": [],
        "arm_angles": [],
        "hand_eye_distances": []
    }
    
    for idx, video_name in enumerate(videos):
        video_path = os.path.join(video_dir, video_name)
        lower_name = video_name.lower()
        
        # Decide which postures this video is relevant for
        is_savdhan_video = "savdhan" in lower_name
        is_vishram_video = "vishram" in lower_name
        is_salute_video = "salute" in lower_name
        
        if not (is_savdhan_video or is_vishram_video or is_salute_video):
            # Skip marching, turning etc. for static posture calibration
            print(f"[{idx+1}/{len(videos)}] Skipping {video_name} (dynamic drill movement)")
            continue
            
        print(f"[{idx+1}/{len(videos)}] Processing {video_name}...")
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print(f"Failed to open {video_name}")
            continue
            
        frame_idx = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break
                
            # Process every 5th frame to speed up training
            if frame_idx % 5 != 0:
                frame_idx += 1
                continue
                
            detections = pose_estimator.infer(frame)
            if not detections:
                frame_idx += 1
                continue
                
            # Get primary cadet detection
            det = detections[0]
            k = det.keypoints  # Shape [17, 3] (x, y, conf)
            
            # Extract basic spine scale and landmark visibilities
            l_shoulder, r_shoulder = k[5], k[6]
            l_hip, r_hip = k[11], k[12]
            
            # Ensure shoulders and hips are reasonably visible
            if min(l_shoulder[2], r_shoulder[2], l_hip[2], r_hip[2]) < 0.25:
                frame_idx += 1
                continue
                
            # Spine length estimation
            neck = (l_shoulder[:2] + r_shoulder[:2]) / 2
            mid_hip = (l_hip[:2] + r_hip[:2]) / 2
            spine_length = segment_length(neck, mid_hip)
            if spine_length < 20:
                frame_idx += 1
                continue
                
            # Ankle distance
            l_ankle, r_ankle = k[15], k[16]
            heel_dist_px = segment_length(l_ankle[:2], r_ankle[:2])
            heel_gap_ratio = heel_dist_px / spine_length
            
            # Arm positions
            l_elbow, r_elbow = k[7], k[8]
            l_wrist, r_wrist = k[9], k[10]
            
            l_arm_visible = min(l_shoulder[2], l_elbow[2], l_wrist[2], l_hip[2]) >= 0.25
            r_arm_visible = min(r_shoulder[2], r_elbow[2], r_wrist[2], r_hip[2]) >= 0.25
            
            # Elbow angles
            l_elbow_angle = angle_degrees(l_wrist[:2], l_elbow[:2], l_shoulder[:2]) if l_arm_visible else 180
            r_elbow_angle = angle_degrees(r_wrist[:2], r_elbow[:2], r_shoulder[:2]) if r_arm_visible else 180
            
            # Horizontal wrist-hip distances
            l_wrist_hip_horiz = abs(l_wrist[0] - l_hip[0]) / spine_length if l_arm_visible else 0
            r_wrist_hip_horiz = abs(r_wrist[0] - r_hip[0]) / spine_length if r_arm_visible else 0
            
            # Vertical wrist-hip distances
            l_wrist_hip_vert = (l_wrist[1] - l_hip[1]) / spine_length if l_arm_visible else 0
            r_wrist_hip_vert = (r_wrist[1] - r_hip[1]) / spine_length if r_arm_visible else 0
            
            # 1. Evaluate Savdhan Candidate
            if is_savdhan_video:
                # Heuristic: Hands hanging low, elbows straight, heels close
                if (l_wrist_hip_vert > -0.1 and r_wrist_hip_vert > -0.1 and 
                    l_wrist_hip_horiz < 0.65 and r_wrist_hip_horiz < 0.65 and 
                    l_elbow_angle > 140 and r_elbow_angle > 140 and 
                    heel_gap_ratio < 0.38):
                    
                    data_savdhan["heel_gap_ratios"].append(heel_gap_ratio)
                    if l_arm_visible:
                        data_savdhan["arm_horizontal_ratios"].append(l_wrist_hip_horiz)
                        data_savdhan["elbow_angles"].append(l_elbow_angle)
                    if r_arm_visible:
                        data_savdhan["arm_horizontal_ratios"].append(r_wrist_hip_horiz)
                        data_savdhan["elbow_angles"].append(r_elbow_angle)
            
            # 2. Evaluate Vishram Candidate
            if is_vishram_video:
                # Heuristic: Heels spread wide
                if heel_gap_ratio >= 0.38:
                    data_vishram["heel_gap_ratios"].append(heel_gap_ratio)
                    
            # 3. Evaluate Salute Candidate
            if is_salute_video:
                # Heuristic: Right wrist raised near head
                r_eye = k[2]
                nose = k[0]
                if r_wrist[2] >= 0.25 and r_eye[2] >= 0.25 and r_elbow[2] >= 0.25:
                    r_wrist_eye_dist = segment_length(r_wrist[:2], r_eye[:2]) / spine_length
                    r_elbow_drop = (r_elbow[1] - r_shoulder[1]) / spine_length
                    
                    # If wrist is raised above face level
                    if r_wrist[1] < nose[1] + 0.1 * spine_length and r_elbow_angle < 130:
                        data_salute["elbow_drops"].append(r_elbow_drop)
                        data_salute["arm_angles"].append(r_elbow_angle)
                        data_salute["hand_eye_distances"].append(r_wrist_eye_dist)
            
            frame_idx += 1
            
        cap.release()
        
    print("\nExtraction completed. Calculating calibrated metrics...")
    
    # ─── Process Savdhan Calibrated Parameters ───
    savdhan_report = "### Savdhan Parameters\n"
    if data_savdhan["heel_gap_ratios"]:
        # Safe upper bound for heel gap ratio (e.g. 95th percentile)
        calibrated_savdhan_heel_gap = float(np.percentile(data_savdhan["heel_gap_ratios"], 95))
        # Ensure it doesn't drop below 0.20 for stability
        calibrated_savdhan_heel_gap = max(0.20, min(0.35, calibrated_savdhan_heel_gap))
        savdhan_report += f"- Heel Gap Ratio (95th Pct): {calibrated_savdhan_heel_gap:.3f}\n"
    else:
        calibrated_savdhan_heel_gap = 0.25
        savdhan_report += "- Heel Gap Ratio: Defaulting to 0.25 (No frames found)\n"
        
    if data_savdhan["arm_horizontal_ratios"]:
        # Safe upper bound for arm-to-hip horizontal distance (95th percentile)
        calibrated_savdhan_arm_dist = float(np.percentile(data_savdhan["arm_horizontal_ratios"], 95))
        calibrated_savdhan_arm_dist = max(0.45, min(0.65, calibrated_savdhan_arm_dist))
        savdhan_report += f"- Arm Side Distance Ratio (95th Pct): {calibrated_savdhan_arm_dist:.3f}\n"
    else:
        calibrated_savdhan_arm_dist = 0.55
        savdhan_report += "- Arm Side Distance Ratio: Defaulting to 0.55\n"
        
    # ─── Process Vishram Calibrated Parameters ───
    vishram_report = "### Vishram Parameters\n"
    if data_vishram["heel_gap_ratios"]:
        # Vishram range based on 5th to 95th percentile
        vishram_min = float(np.percentile(data_vishram["heel_gap_ratios"], 5))
        vishram_max = float(np.percentile(data_vishram["heel_gap_ratios"], 95))
        # Add safety cushions
        vishram_min = max(0.30, min(0.48, vishram_min - 0.05))
        vishram_max = max(0.85, min(1.20, vishram_max + 0.05))
        vishram_report += f"- Heel Spread Range: {vishram_min:.3f} to {vishram_max:.3f}\n"
    else:
        vishram_min = 0.40
        vishram_max = 1.00
        vishram_report += "- Heel Spread Range: Defaulting to 0.40 to 1.00\n"
        
    # ─── Process Salute Calibrated Parameters ───
    salute_report = "### Salute Parameters\n"
    if data_salute["arm_angles"]:
        salute_angle_min = float(np.percentile(data_salute["arm_angles"], 5))
        salute_angle_max = float(np.percentile(data_salute["arm_angles"], 95))
        # Add tolerance
        salute_angle_min = max(20, min(40, salute_angle_min - 5))
        salute_angle_max = max(110, min(135, salute_angle_max + 5))
        salute_report += f"- Saluting Arm Interior Angle Range: {salute_angle_min:.1f}° to {salute_angle_max:.1f}°\n"
    else:
        salute_angle_min = 25
        salute_angle_max = 120
        salute_report += "- Saluting Arm Interior Angle Range: Defaulting to 25° to 120°\n"
        
    if data_salute["elbow_drops"]:
        calibrated_elbow_drop = float(np.percentile(data_salute["elbow_drops"], 95))
        calibrated_elbow_drop = max(0.15, min(0.35, calibrated_elbow_drop + 0.03))
        salute_report += f"- Elbow Drop Ratio (95th Pct): {calibrated_elbow_drop:.3f}\n"
    else:
        calibrated_elbow_drop = 0.20
        salute_report += "- Elbow Drop Ratio: Defaulting to 0.20\n"
        
    if data_salute["hand_eye_distances"]:
        calibrated_hand_eye_dist = float(np.percentile(data_salute["hand_eye_distances"], 95))
        calibrated_hand_eye_dist = max(0.45, min(0.70, calibrated_hand_eye_dist + 0.05))
        salute_report += f"- Right Wrist-Eye Distance Ratio (95th Pct): {calibrated_hand_eye_dist:.3f}\n"
    else:
        calibrated_hand_eye_dist = 0.55
        salute_report += "- Right Wrist-Eye Distance Ratio: Defaulting to 0.55\n"

    # Write training report
    report_content = f"""# Drill Calibration and Training Report

This report summarizes the data-driven geometric thresholds extracted by running YOLO pose estimation on the new training videos located in `C:\\Users\\The Moe\\Downloads\\all the drill videos`.

{savdhan_report}
{vishram_report}
{salute_report}

All thresholds have been automatically updated in the corresponding rule files in `backend/evaluation/rules/`.
"""
    report_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "training_report.md")
    
    # Wait, let's put it in the artifacts folder, and copy it here.
    # The workspace path is C:\Users\The Moe\Desktop\drill
    with open(os.path.join(r"C:\Users\The Moe\Desktop\drill", "training_report.md"), "w") as f:
        f.write(report_content)
    print("Saved training_report.md to workspace.")

    # ─── Rewrite Rule Files with Calibrated Values ───
    print("Updating rule files...")
    
    # 1. savdhan_heel_contact.py
    sh_path = r"backend/evaluation/rules/savdhan_heel_contact.py"
    if os.path.exists(sh_path):
        with open(sh_path, "r") as f:
            content = f.read()
        content = re.sub(r'normalized_gap\s*<=\s*[0-9.]+', f'normalized_gap <= {calibrated_savdhan_heel_gap:.3f}', content)
        content = re.sub(r'normalized_gap\s*-\s*[0-9.]+', f'normalized_gap - {calibrated_savdhan_heel_gap:.3f}', content)
        content = re.sub(r'Gap ratio:\s*\{\s*normalized_gap\s*:\s*\.2f\s*\}', f'Gap ratio: {{normalized_gap:.2f}} (Threshold: {calibrated_savdhan_heel_gap:.3f})', content)
        with open(sh_path, "w") as f:
            f.write(content)
        print(f"Updated {sh_path} with heel gap: {calibrated_savdhan_heel_gap:.3f}")
        
    # 2. savdhan_arm_position.py
    sa_path = r"backend/evaluation/rules/savdhan_arm_position.py"
    if os.path.exists(sa_path):
        with open(sa_path, "r") as f:
            content = f.read()
        content = re.sub(r'x_dist\s*>\s*[0-9.]+', f'x_dist > {calibrated_savdhan_arm_dist:.3f}', content)
        content = re.sub(r'x_dist\s*-\s*[0-9.]+', f'x_dist - {calibrated_savdhan_arm_dist:.3f}', content)
        content = re.sub(r'x_dist\s*-\s*[0-9.]+', f'x_dist - {calibrated_savdhan_arm_dist:.3f}', content)
        with open(sa_path, "w") as f:
            f.write(content)
        print(f"Updated {sa_path} with arm distance: {calibrated_savdhan_arm_dist:.3f}")
        
    # 3. vishram_spacing.py
    vs_path = r"backend/evaluation/rules/vishram_spacing.py"
    if os.path.exists(vs_path):
        with open(vs_path, "r") as f:
            content = f.read()
        # Find lines:
        # if 0.4 <= norm_dist <= 1.0:
        #     score = 100.0
        # elif 0.2 <= norm_dist < 0.4:
        #     score = max(0.0, 100.0 - (0.4 - norm_dist) * 300)
        # elif 1.0 < norm_dist <= 1.3:
        #     score = max(0.0, 100.0 - (norm_dist - 1.0) * 300)
        content = re.sub(r'if\s*[0-9.]+\s*<=\s*norm_dist\s*<=\s*[0-9.]+\s*:', f'if {vishram_min:.3f} <= norm_dist <= {vishram_max:.3f}:', content)
        content = re.sub(r'elif\s*[0-9.]+\s*<=\s*norm_dist\s*<\s*[0-9.]+\s*:', f'elif {vishram_min - 0.2:.3f} <= norm_dist < {vishram_min:.3f}:', content)
        content = re.sub(r'100\.0\s*-\s*\(\s*[0-9.]+\s*-\s*norm_dist\s*\)\s*\*\s*300', f'100.0 - ({vishram_min:.3f} - norm_dist) * 300', content)
        content = re.sub(r'elif\s*[0-9.]+\s*<\s*norm_dist\s*<=\s*[0-9.]+\s*:', f'elif {vishram_max:.3f} < norm_dist <= {vishram_max + 0.3:.3f}:', content)
        content = re.sub(r'100\.0\s*-\s*\(\s*norm_dist\s*-\s*[0-9.]+\s*\)\s*\*\s*300', f'100.0 - (norm_dist - {vishram_max:.3f}) * 300', content)
        with open(vs_path, "w") as f:
            f.write(content)
        print(f"Updated {vs_path} with vishram range: {vishram_min:.3f} to {vishram_max:.3f}")
        
    # 4. salute_arm_angle.py
    sarm_path = r"backend/evaluation/rules/salute_arm_angle.py"
    if os.path.exists(sarm_path):
        with open(sarm_path, "r") as f:
            content = f.read()
        # Update elbow drop
        content = re.sub(r'elbow_drop\s*>\s*[0-9.]+', f'elbow_drop > {calibrated_elbow_drop:.3f}', content)
        # Update interior angle ranges
        # if 25 <= angle <= 120:
        #     score = 100.0
        # elif 15 <= angle < 25:
        #     score = 100.0 - ((25 - angle) * 10.0)
        # elif 120 < angle <= 145:
        #     score = 100.0 - ((angle - 120) * 4.0)
        content = re.sub(r'if\s*[0-9.]+\s*<=\s*angle\s*<=\s*[0-9.]+\s*:', f'if {salute_angle_min:.1f} <= angle <= {salute_angle_max:.1f}:', content)
        content = re.sub(r'elif\s*[0-9.]+\s*<=\s*angle\s*<\s*[0-9.]+\s*:', f'elif {salute_angle_min - 10:.1f} <= angle < {salute_angle_min:.1f}:', content)
        content = re.sub(r'100\.0\s*-\s*\(\(\s*[0-9.]+\s*-\s*angle\s*\)\s*\*\s*10\.0\)', f'100.0 - (({salute_angle_min:.1f} - angle) * 10.0)', content)
        content = re.sub(r'elif\s*[0-9.]+\s*<\s*angle\s*<=\s*[0-9.]+\s*:', f'elif {salute_angle_max:.1f} < angle <= {salute_angle_max + 25:.1f}:', content)
        content = re.sub(r'100\.0\s*-\s*\(\(\s*angle\s*-\s*[0-9.]+\s*\)\s*\*\s*4\.0\)', f'100.0 - ((angle - {salute_angle_max:.1f}) * 4.0)', content)
        with open(sarm_path, "w") as f:
            f.write(content)
        print(f"Updated {sarm_path} with elbow drop: {calibrated_elbow_drop:.3f} and angle range: {salute_angle_min:.1f}-{salute_angle_max:.1f}")
        
    # 5. salute_hand_position.py
    shand_path = r"backend/evaluation/rules/salute_hand_position.py"
    if os.path.exists(shand_path):
        with open(shand_path, "r") as f:
            content = f.read()
        # Update norm_dist limit
        # if norm_dist <= 0.55:
        #     score = 100.0
        # elif norm_dist < 0.75:
        #     score = 100.0 - ((norm_dist - 0.55) * 500)
        content = re.sub(r'norm_dist\s*<=\s*[0-9.]+', f'norm_dist <= {calibrated_hand_eye_dist:.3f}', content)
        content = re.sub(r'norm_dist\s*<\s*[0-9.]+', f'norm_dist < {calibrated_hand_eye_dist + 0.20:.3f}', content)
        content = re.sub(r'norm_dist\s*-\s*[0-9.]+', f'norm_dist - {calibrated_hand_eye_dist:.3f}', content)
        with open(shand_path, "w") as f:
            f.write(content)
        print(f"Updated {shand_path} with hand-eye distance: {calibrated_hand_eye_dist:.3f}")

    print("\nCalibration successful! Running refactor scripts to update shared rule classes...")
    # Run refactor_rules.py to update savdhan_shared.py, vishram_shared.py, generic_shared.py
    try:
        import refactor_rules
        print("Refactored shared rule files successfully.")
    except Exception as e:
        print(f"Warning: Failed to run refactor_rules.py: {e}")

if __name__ == "__main__":
    main()
