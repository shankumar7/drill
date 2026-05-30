import cv2
import numpy as np

def draw_skeleton(frame, keypoints, analysis):
    """
    Draws a color-coded skeleton with specific error highlighting.
    """
    status = analysis['status']
    scores = analysis['scores']
    
    # Base status color
    color_map = {
        "Excellent": (0, 255, 0),   # Green
        "Good": (0, 255, 255),      # Yellow
        "Warning": (0, 165, 255),   # Orange
        "Incorrect": (0, 0, 255)    # Red
    }
    base_color = color_map.get(status, (255, 255, 255))
    
    # Define connection groups for error highlighting
    # (start, end, metric_name, threshold)
    groups = [
        ((5, 6), None),           # Shoulders (symmetry)
        ((5, 7), "Arm Alignment"), 
        ((7, 9), "Arm Alignment"),
        ((6, 8), "Arm Alignment"),
        ((8, 10), "Arm Alignment"),
        ((11, 13), "Knee Stability"),
        ((13, 15), "Knee Stability"),
        ((12, 14), "Knee Stability"),
        ((14, 16), "Knee Stability"),
        ((5, 11), "Torso Posture"),
        ((6, 12), "Torso Posture"),
        ((11, 12), "Heel Alignment")
    ]
    
    for (start_idx, end_idx), metric in groups:
        kp1 = keypoints[start_idx]
        kp2 = keypoints[end_idx]
        
        if kp1[2] > 0.5 and kp2[2] > 0.5:
            # Determine line color
            line_color = base_color
            if metric and metric in scores:
                score = scores[metric]
                if score < 70: line_color = (0, 0, 255) # Red
                elif score < 85: line_color = (0, 165, 255) # Orange
            
            cv2.line(frame, (int(kp1[0]), int(kp1[1])), (int(kp2[0]), int(kp2[1])), line_color, 2)
            
    # Draw keypoints
    for i, kp in enumerate(keypoints):
        if kp[2] > 0.5:
            cv2.circle(frame, (int(kp[0]), int(kp[1])), 3, (255, 255, 255), -1)

def draw_hud(frame, cadets, fps):
    """
    Draws HUD elements like FPS and Cadet IDs.
    """
    # Background HUD decoration
    cv2.rectangle(frame, (10, 10), (180, 60), (0, 0, 0), -1)
    cv2.rectangle(frame, (10, 10), (180, 60), (0, 255, 0), 1)
    cv2.putText(frame, f"LIVE FEED: {fps:.1f} FPS", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
    
    for cadet in cadets:
        bbox = cadet['bbox']
        analysis = cadet['analysis']
        status = analysis['status']
        score = analysis['overall']
        cid = cadet['id']
        
        color_map = {"Excellent": (0, 255, 0), "Good": (0, 255, 255), "Warning": (0, 165, 255), "Incorrect": (0, 0, 255)}
        color = color_map.get(status, (255, 255, 255))
        
        x1, y1, x2, y2 = map(int, bbox)
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 1)
        
        # Label HUD
        cv2.rectangle(frame, (x1, y1 - 25), (x1 + 180, y1), color, -1)
        label = f"CADET-{cid}: {score:.1f}%"
        cv2.putText(frame, label, (x1 + 5, y1 - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
        
        # Draw Skeleton
        draw_skeleton(frame, cadet['keypoints'], analysis)
        
        # Draw Foot Guidelines and Dynamic Stance Overlay
        foot_geom = analysis.get('foot_geometry')
        mode = analysis.get('mode', 'SAVDHAN')
        
        if foot_geom:
            toe_r = foot_geom.get('toe_r')
            toe_l = foot_geom.get('toe_l')
            foot_angle = foot_geom.get('foot_angle')
            true_heel_dist = foot_geom.get('true_heel_dist', 0.0)
            pose_scale = foot_geom.get('pose_scale', 1.0)
            heel_touch = foot_geom.get('heel_touch')
            
            # Inches calibration
            scale_factor = 9.5 / (pose_scale + 1e-6)
            heel_in = true_heel_dist * scale_factor
            
            toe_dist = 0.0
            if toe_r and toe_l:
                toe_dist = abs(toe_l[0] - toe_r[0])
            toe_in = toe_dist * scale_factor
            
            if mode in ["VISHRAM", "AARAM_SE"]:
                # --- VISHRAM / AARAM_SE HUD SPACING DRAWING ---
                # Heel Target: 12 in (OK: 10.5 to 13.5). Toe Target: 18 in (OK: 16.0 to 20.0).
                heel_ok = (10.5 <= heel_in <= 13.5)
                toe_ok = (16.0 <= toe_in <= 20.0)
                
                heel_color = (0, 255, 0) if heel_ok else (0, 0, 255)
                toe_color = (0, 255, 0) if toe_ok else (0, 0, 255)
                
                r_ankle = cadet['keypoints'][16][:2]
                l_ankle = cadet['keypoints'][15][:2]
                h_y = int((r_ankle[1] + l_ankle[1]) / 2.0)
                
                # Draw Heel Spacing horizontal bracket bar
                cv2.circle(frame, (int(r_ankle[0]), h_y), 5, heel_color, -1)
                cv2.circle(frame, (int(l_ankle[0]), h_y), 5, heel_color, -1)
                cv2.line(frame, (int(r_ankle[0]), h_y), (int(l_ankle[0]), h_y), heel_color, 2)
                
                # Draw Heel label plaque
                h_text = f"HEELS: {heel_in:.1f} in"
                h_size = cv2.getTextSize(h_text, cv2.FONT_HERSHEY_SIMPLEX, 0.4, 1)[0]
                h_mid_x = int((r_ankle[0] + l_ankle[0]) / 2.0)
                cv2.rectangle(frame, (h_mid_x - h_size[0]//2 - 4, h_y - 18), (h_mid_x + h_size[0]//2 + 4, h_y - 2), (0, 0, 0), -1)
                cv2.rectangle(frame, (h_mid_x - h_size[0]//2 - 4, h_y - 18), (h_mid_x + h_size[0]//2 + 4, h_y - 2), heel_color, 1)
                cv2.putText(frame, h_text, (h_mid_x - h_size[0]//2, h_y - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.4, heel_color, 1, cv2.LINE_AA)
                
                # Draw Toe Spacing horizontal bracket bar
                if toe_r and toe_l:
                    t_y = int((toe_r[1] + toe_l[1]) / 2.0)
                    cv2.circle(frame, (int(toe_r[0]), t_y), 5, toe_color, -1)
                    cv2.circle(frame, (int(toe_l[0]), t_y), 5, toe_color, -1)
                    cv2.line(frame, (int(toe_r[0]), t_y), (int(toe_l[0]), t_y), toe_color, 2)
                    
                    # Draw Toe label plaque
                    t_text = f"TOES: {toe_in:.1f} in"
                    t_size = cv2.getTextSize(t_text, cv2.FONT_HERSHEY_SIMPLEX, 0.4, 1)[0]
                    t_mid_x = int((toe_r[0] + toe_l[0]) / 2.0)
                    cv2.rectangle(frame, (t_mid_x - t_size[0]//2 - 4, t_y + 4), (t_mid_x + t_size[0]//2 + 4, t_y + 20), (0, 0, 0), -1)
                    cv2.rectangle(frame, (t_mid_x - t_size[0]//2 - 4, t_y + 4), (t_mid_x + t_size[0]//2 + 4, t_y + 20), toe_color, 1)
                    cv2.putText(frame, t_text, (t_mid_x - t_size[0]//2, t_y + 16), cv2.FONT_HERSHEY_SIMPLEX, 0.4, toe_color, 1, cv2.LINE_AA)
                    
            else:
                # --- SAVDHAN HUD ANGLE DRAWING ---
                # Check for visual heel gap (greater than 10% of ankle span scale)
                is_heel_gap = False
                if pose_scale > 0:
                    is_heel_gap = (true_heel_dist / pose_scale) > 0.1
                    
                if foot_angle is not None:
                    if is_heel_gap:
                        feet_color = (0, 0, 255)      # Red (Stance invalid due to heel gap)
                    elif 28.0 <= foot_angle <= 32.0:
                        feet_color = (0, 255, 0)      # Green (Perfect compliance)
                    elif 25.0 <= foot_angle <= 35.0:
                        feet_color = (0, 165, 255)    # Orange (Acceptable/Warning)
                    else:
                        feet_color = (0, 0, 255)      # Red (Out of regulation)
                        
                    # Draw Right Foot vector (Camera Left) starting from Heel Touch Point
                    if toe_r is not None and heel_touch is not None:
                        cv2.line(frame, (int(heel_touch[0]), int(heel_touch[1])), (int(toe_r[0]), int(toe_r[1])), feet_color, 3)
                        cv2.circle(frame, (int(toe_r[0]), int(toe_r[1])), 5, feet_color, -1)
                        cv2.circle(frame, (int(toe_r[0]), int(toe_r[1])), 6, (255, 255, 255), 1)
                        
                    # Draw Left Foot vector (Camera Right) starting from Heel Touch Point
                    if toe_l is not None and heel_touch is not None:
                        cv2.line(frame, (int(heel_touch[0]), int(heel_touch[1])), (int(toe_l[0]), int(toe_l[1])), feet_color, 3)
                        cv2.circle(frame, (int(toe_l[0]), int(toe_l[1])), 5, feet_color, -1)
                        cv2.circle(frame, (int(toe_l[0]), int(toe_l[1])), 6, (255, 255, 255), 1)
                        
                    # Draw a glowing circular vertex where the heels are touching together
                    if heel_touch is not None:
                        cv2.circle(frame, (int(heel_touch[0]), int(heel_touch[1])), 6, feet_color, -1)
                        cv2.circle(frame, (int(heel_touch[0]), int(heel_touch[1])), 8, (255, 255, 255), 1)
                        
                    # Draw feet angle text overlay
                    r_ankle = cadet['keypoints'][16][:2]
                    l_ankle = cadet['keypoints'][15][:2]
                    avg_foot_y = max(int(r_ankle[1]), int(l_ankle[1]))
                    avg_foot_x = int((r_ankle[0] + l_ankle[0]) / 2)
                    
                    text_label = f"ANGLE: {foot_angle:.1f} DEG"
                    text_size = cv2.getTextSize(text_label, cv2.FONT_HERSHEY_SIMPLEX, 0.45, 1)[0]
                    
                    box_x1 = avg_foot_x - text_size[0] // 2 - 8
                    box_y1 = avg_foot_y + 15
                    box_x2 = avg_foot_x + text_size[0] // 2 + 8
                    box_y2 = avg_foot_y + 15 + text_size[1] + 10
                    
                    cv2.rectangle(frame, (box_x1, box_y1), (box_x2, box_y2), (0, 0, 0), -1)
                    cv2.rectangle(frame, (box_x1, box_y1), (box_x2, box_y2), feet_color, 1)
                    cv2.putText(frame, text_label, (box_x1 + 8, box_y2 - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.45, feet_color, 1, cv2.LINE_AA)
        
        # Display major violations if any
        if analysis['violations']:
            v_text = "!" + analysis['violations'][0]
            cv2.putText(frame, v_text, (x1, y2 + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
    
    return frame
