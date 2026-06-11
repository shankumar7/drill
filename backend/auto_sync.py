import json
import os

def find_offsets(json_path):
    with open(json_path, 'r') as f:
        data = json.load(f)

    # We want to find the peak of the stomp. 
    # In mediapipe, landmark 28 is Right Ankle. 
    # Y axis is 0 at top, so minimum Y means highest foot position.
    
    peaks = {'front': (None, float('inf')), 'back': (None, float('inf')), 'side': (None, float('inf'))}

    for frame_data in data:
        frame_idx = frame_data['frame']
        poses = frame_data['poses']
        
        for view in ['front', 'back', 'side']:
            if poses[view] and len(poses[view]) > 28:
                # Get Y of right ankle
                y = poses[view][28]['y']
                # Get visibility
                v = poses[view][28]['v']
                
                # Only consider if visibility is decent
                if v > 0.3:
                    if y < peaks[view][1]:
                        peaks[view] = (frame_idx, y)

    print("Highest foot position (Right Ankle) found at frames:")
    print(f"Front: Frame {peaks['front'][0]}")
    print(f"Back:  Frame {peaks['back'][0]}")
    print(f"Side:  Frame {peaks['side'][0]}")
    
    if all(p[0] is not None for p in peaks.values()):
        # Let's align them to the earliest peak
        min_peak = min(peaks['front'][0], peaks['back'][0], peaks['side'][0])
        
        print("\nTo perfectly sync them, we need to shift them by this many ADDITIONAL frames:")
        print(f"Front needs to skip: {peaks['front'][0] - peaks['side'][0]} more frames compared to side")
        print(f"Back needs to skip:  {peaks['back'][0] - peaks['side'][0]} more frames compared to side")
        
        # We know fps is ~29.04 from previous log
        fps = 29.04
        print(f"\nIn seconds, increase the offset by:")
        print(f"Front: +{(peaks['front'][0] - peaks['side'][0])/fps:.3f} seconds")
        print(f"Back:  +{(peaks['back'][0] - peaks['side'][0])/fps:.3f} seconds")

if __name__ == "__main__":
    home = os.path.expanduser('~')
    desktop = os.path.join(home, 'Desktop')
    json_path = os.path.join(desktop, 'savadhan_keypoints.json')
    find_offsets(json_path)
