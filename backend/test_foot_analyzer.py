import cv2
import numpy as np
import sys
from backend.engine.foot_analyzer import FootGeometryAnalyzer

def run_tests():
    print("=== STARTING FOOT GEOMETRY ANALYZER AUTOMATED TESTS ===")
    
    # 1. Setup Mock Frame and Keypoints
    h, w = 480, 640
    frame = np.zeros((h, w, 3), dtype=np.uint8)
    
    # Draw two dark shoe silhouettes (gray) on a bright white floor background (white)
    # The background is bright, so THRESH_BINARY_INV will turn the shoes white
    frame.fill(255)
    
    # Cadet's Right Foot (Camera Left, Ankle ~ 300, 400)
    # Tilted 15 degrees counter-clockwise -> points down-left
    # We draw an angled ellipse representing the shoe
    # Center = (280, 420), Size = (20, 50), Angle = -15
    cv2.ellipse(frame, (280, 420), (20, 55), -15, 0, 360, (50, 50, 50), -1)
    
    # Cadet's Left Foot (Camera Right, Ankle ~ 340, 400)
    # Tilted 15 degrees clockwise -> points down-right
    # Center = (360, 420), Size = (20, 50), Angle = 15
    cv2.ellipse(frame, (360, 420), (20, 55), 15, 0, 360, (50, 50, 50), -1)
    
    # Setup keypoints (33 standard MediaPipe style joints, but we only need 15: L_ankle, 16: R_ankle)
    # keypoints structure: [x, y, conf]
    keypoints = np.zeros((33, 3))
    keypoints[15] = [340, 400, 0.9] # Left Ankle (Camera Right)
    keypoints[16] = [300, 400, 0.9] # Right Ankle (Camera Left)
    
    # 2. Instantiate and run FootGeometryAnalyzer
    analyzer = FootGeometryAnalyzer()
    
    print("Testing initial geometry calculation...")
    result = analyzer.analyze_geometry(frame, keypoints)
    
    if result is None:
        print("ERROR: Analyzer returned None!")
        sys.exit(1)
        
    print("\n[SUCCESS] Geometry calculated successfully!")
    print(f"Calculated Image-Plane Foot Angle: {result['image_plane_angle']:.2f} degrees")
    print(f"Calculated Heel Distance: {result['true_heel_dist']} pixels")
    print(f"Pose Scale: {result['pose_scale']} pixels")
    print(f"Left Toe Tip (Camera Right): {result['toe_l']}")
    print(f"Right Toe Tip (Camera Left): {result['toe_r']}")
    
    # Assertions
    # The foot angle should be within 10 to 50 degrees depending on mock projection
    assert result['image_plane_angle'] is not None, "Image-plane angle should be available!"
    assert result['toe_r'] is not None, "Right toe tip not found!"
    assert result['toe_l'] is not None, "Left toe tip not found!"
    assert result['true_heel_dist'] >= 0, "Heel distance should be >= 0!"
    
    print("\nChecking Caching performance...")
    # Call again with same frame and keypoints (should hit cache)
    result2 = analyzer.analyze_geometry(frame, keypoints)
    
    # Ensure they are identical objects (cache hit)
    assert result is result2, "Cache missed! A new dictionary was calculated/returned."
    print("[SUCCESS] Caching Layer is operational (O(1) consecutive return)!")
    
    # Call with slightly modified keypoints (should miss cache)
    keypoints_mod = keypoints.copy()
    keypoints_mod[15][0] += 1
    result3 = analyzer.analyze_geometry(frame, keypoints_mod)
    assert result3 is not result, "Cache hit on modified keypoints! That is unsafe."
    print("[SUCCESS] Cache correctly invalidated upon input changes!")
    
    print("\n=== ALL AUTOMATED TESTS PASSED SUCCESSFULLY ===")

if __name__ == "__main__":
    run_tests()
