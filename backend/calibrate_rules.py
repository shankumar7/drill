import os
import json
import numpy as np

dataset_dir = "/Users/shankumar/Desktop/Drill Footages/Dataset"

def segment_length(p1, p2):
    return np.linalg.norm(np.array(p1) - np.array(p2))

def analyze_savdhan():
    print("=== Analyzing SAVDHAN ===")
    savdhan_dir = os.path.join(dataset_dir, "Savdhan")
    if not os.path.exists(savdhan_dir):
        print("No Savdhan data found.")
        return
        
    arm_norms = []
    heel_norms = []
    knee_norms = []
    
    for take in os.listdir(savdhan_dir):
        json_path = os.path.join(savdhan_dir, take, "keypoints.json")
        if not os.path.exists(json_path):
            continue
            
        with open(json_path, 'r') as f:
            data = json.load(f)
            
        for frame_idx, views in data.get("frames", {}).items():
            # Usually front view is best for horizontal distances like heel/knee
            # Let's use the front view for Savdhan calibration
            if "front" not in views:
                continue
            kpts = views["front"]
            if len(kpts) < 17:
                continue
                
            # Convert to numpy arrays for easier math
            k = np.array([[kp["x"], kp["y"], kp["conf"]] for kp in kpts])
            
            # Shoulder Width
            if k[5, 2] < 0.3 or k[6, 2] < 0.3:
                continue
            shoulder_width = segment_length(k[5, :2], k[6, :2])
            if shoulder_width < 10:
                continue
                
            # Arm Position
            if k[9, 2] > 0.3 and k[11, 2] > 0.3:
                l_arm = segment_length(k[9, :2], k[11, :2]) / shoulder_width
                arm_norms.append(l_arm)
            if k[10, 2] > 0.3 and k[12, 2] > 0.3:
                r_arm = segment_length(k[10, :2], k[12, :2]) / shoulder_width
                arm_norms.append(r_arm)
                
            # Heel Distance
            if k[15, 2] > 0.3 and k[16, 2] > 0.3:
                heel_dist = segment_length(k[15, :2], k[16, :2]) / shoulder_width
                heel_norms.append(heel_dist)
                
            # Knee Distance
            if k[13, 2] > 0.3 and k[14, 2] > 0.3:
                knee_dist = segment_length(k[13, :2], k[14, :2]) / shoulder_width
                knee_norms.append(knee_dist)

    if arm_norms:
        print(f"Arms at Sides (Norm to Shoulder): Mean = {np.mean(arm_norms):.3f}, Std = {np.std(arm_norms):.3f}")
    if heel_norms:
        print(f"Heel Contact (Norm to Shoulder): Mean = {np.mean(heel_norms):.3f}, Std = {np.std(heel_norms):.3f}")
    if knee_norms:
        print(f"Knee Distance (Norm to Shoulder): Mean = {np.mean(knee_norms):.3f}, Std = {np.std(knee_norms):.3f}")

def analyze_vishram():
    print("\n=== Analyzing VISHRAM ===")
    vishram_dir = os.path.join(dataset_dir, "Vishram")
    if not os.path.exists(vishram_dir):
        print("No Vishram data found.")
        return
        
    heel_norms = []
    
    for take in os.listdir(vishram_dir):
        json_path = os.path.join(vishram_dir, take, "keypoints.json")
        if not os.path.exists(json_path):
            continue
            
        with open(json_path, 'r') as f:
            data = json.load(f)
            
        for frame_idx, views in data.get("frames", {}).items():
            if "front" not in views:
                continue
            kpts = views["front"]
            k = np.array([[kp["x"], kp["y"], kp["conf"]] for kp in kpts])
            
            if k[5, 2] < 0.3 or k[6, 2] < 0.3:
                continue
            shoulder_width = segment_length(k[5, :2], k[6, :2])
            if shoulder_width < 10:
                continue
                
            if k[15, 2] > 0.3 and k[16, 2] > 0.3:
                heel_dist = segment_length(k[15, :2], k[16, :2]) / shoulder_width
                heel_norms.append(heel_dist)

    if heel_norms:
        print(f"Vishram Heel Gap (Norm to Shoulder): Mean = {np.mean(heel_norms):.3f}, Std = {np.std(heel_norms):.3f}")

if __name__ == "__main__":
    analyze_savdhan()
    analyze_vishram()
