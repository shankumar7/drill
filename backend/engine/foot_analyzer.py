import cv2
import numpy as np

class FootGeometryAnalyzer:
    def __init__(self):
        # High-performance caching properties
        self._last_frame_id = None
        self._last_keypoints = None
        self._last_result = None

    def get_feet_roi(self, frame, keypoints, padding=30):
        h, w = frame.shape[:2]
        l_ankle = keypoints[15]
        r_ankle = keypoints[16]
        
        x1 = max(0, int(min(l_ankle[0], r_ankle[0]) - padding * 2.0))
        x2 = min(w, int(max(l_ankle[0], r_ankle[0]) + padding * 2.0))
        y1 = max(0, int(min(l_ankle[1], r_ankle[1]) - padding // 2))
        y2 = min(h, int(max(l_ankle[1], r_ankle[1]) + padding * 2.5))
        
        if x2 <= x1 or y2 <= y1:
            return None, (0, 0)
            
        roi = frame[y1:y2, x1:x2]
        return roi, (x1, y1)

    def analyze_geometry(self, frame, keypoints, ground_mapper=None):
        # 1. High-Performance Frame Caching
        frame_id = id(frame)
        if (self._last_frame_id == frame_id and 
            self._last_keypoints is not None and 
            np.array_equal(self._last_keypoints, keypoints)):
            return self._last_result
            
        roi, offset = self.get_feet_roi(frame, keypoints)
        if roi is None or roi.size == 0:
            return None
            
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        _, thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        # 2. Get Ankles in ROI Space
        l_ankle_roi = [keypoints[15][0] - offset[0], keypoints[15][1] - offset[1]]
        r_ankle_roi = [keypoints[16][0] - offset[0], keypoints[16][1] - offset[1]]
        
        # 3. Split ROI Vertically down the Centerline between Ankles
        mid_x = int((l_ankle_roi[0] + r_ankle_roi[0]) / 2)
        roi_h, roi_w = thresh.shape
        mid_x = max(10, min(roi_w - 10, mid_x))
        
        thresh_left = np.zeros_like(thresh)
        thresh_left[:, :mid_x] = thresh[:, :mid_x]
        
        thresh_right = np.zeros_like(thresh)
        thresh_right[:, mid_x:] = thresh[:, mid_x:]
        
        # 4. Find Isolated Shoe Contours on Left Half (Cadet's Right Shoe)
        contours_left, _ = cv2.findContours(thresh_left, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        best_cnt_left = None
        max_area_left = 0
        for cnt in contours_left:
            area = cv2.contourArea(cnt)
            if area > 100:
                x, y, w, h = cv2.boundingRect(cnt)
                cx = x + w // 2
                if abs(cx - r_ankle_roi[0]) < 80:
                    if area > max_area_left:
                        max_area_left = area
                        best_cnt_left = cnt
                        
        if best_cnt_left is None:
            for cnt in contours_left:
                area = cv2.contourArea(cnt)
                if area > 100 and area > max_area_left:
                    max_area_left = area
                    best_cnt_left = cnt

        # 5. Find Isolated Shoe Contours on Right Half (Cadet's Left Shoe)
        contours_right, _ = cv2.findContours(thresh_right, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        best_cnt_right = None
        max_area_right = 0
        for cnt in contours_right:
            area = cv2.contourArea(cnt)
            if area > 100:
                x, y, w, h = cv2.boundingRect(cnt)
                cx = x + w // 2
                if abs(cx - l_ankle_roi[0]) < 80:
                    if area > max_area_right:
                        max_area_right = area
                        best_cnt_right = cnt
                        
        if best_cnt_right is None:
            for cnt in contours_right:
                area = cv2.contourArea(cnt)
                if area > 100 and area > max_area_right:
                    max_area_right = area
                    best_cnt_right = cnt

        # 6. Fit Ellipses to Contours for Purely Visual Stance & Angle Calculation
        # H represents the heel touch point (midpoint between ankles)
        heel_x = (l_ankle_roi[0] + r_ankle_roi[0]) / 2.0
        heel_y = (l_ankle_roi[1] + r_ankle_roi[1]) / 2.0
        
        toe_r = None
        tilt_r = None
        
        # Cadet's Right Foot (Camera Left)
        if best_cnt_left is not None and len(best_cnt_left) >= 5:
            try:
                ellipse_r = cv2.fitEllipse(best_cnt_left)
                cx, cy = ellipse_r[0]
                d_minor, d_major = ellipse_r[1]
                angle_deg = ellipse_r[2]
                
                # Calculate angle from vertical (0 to 90)
                angle_v = angle_deg
                if angle_v > 90: angle_v = 180 - angle_v
                
                # Apply 3D perspective projection correction
                tilt_r = np.degrees(np.arctan(np.tan(np.radians(angle_v)) / 2.2))
                
                # Compute major axis direction pointing down and left
                rad = np.radians(angle_deg)
                vx = -abs(np.sin(rad))
                vy = abs(np.cos(rad))
                
                # Toe tip is at the bottom end of the major axis
                toe_r = [cx + vx * d_major / 2.0, cy + vy * d_major / 2.0]
            except Exception:
                pass
                
        # Extreme-point Fallback if fitEllipse fails
        if toe_r is None and best_cnt_left is not None:
            pts = best_cnt_left.reshape(-1, 2)
            scores = -pts[:, 0] + pts[:, 1]
            idx = np.argmax(scores)
            toe_r = pts[idx].tolist()
            dx = toe_r[0] - heel_x
            dy = toe_r[1] - heel_y
            if dy <= 0: dy = 1e-6
            tilt_r = np.degrees(np.arctan2(abs(dx), dy * 2.2))
            
        toe_l = None
        tilt_l = None
        
        # Cadet's Left Foot (Camera Right)
        if best_cnt_right is not None and len(best_cnt_right) >= 5:
            try:
                ellipse_l = cv2.fitEllipse(best_cnt_right)
                cx, cy = ellipse_l[0]
                d_minor, d_major = ellipse_l[1]
                angle_deg = ellipse_l[2]
                
                # Calculate angle from vertical (0 to 90)
                angle_v = angle_deg
                if angle_v > 90: angle_v = 180 - angle_v
                
                # Apply 3D perspective projection correction
                tilt_l = np.degrees(np.arctan(np.tan(np.radians(angle_v)) / 2.2))
                
                # Compute major axis direction pointing down and right
                rad = np.radians(angle_deg)
                vx = abs(np.sin(rad))
                vy = abs(np.cos(rad))
                
                # Toe tip is at the bottom end of the major axis
                toe_l = [cx + vx * d_major / 2.0, cy + vy * d_major / 2.0]
            except Exception:
                pass
                
        # Extreme-point Fallback if fitEllipse fails
        if toe_l is None and best_cnt_right is not None:
            pts = best_cnt_right.reshape(-1, 2)
            scores = pts[:, 0] + pts[:, 1]
            idx = np.argmax(scores)
            toe_l = pts[idx].tolist()
            dx = toe_l[0] - heel_x
            dy = toe_l[1] - heel_y
            if dy <= 0: dy = 1e-6
            tilt_l = np.degrees(np.arctan2(abs(dx), dy * 2.2))
            
        # 7. Calculate purely visual heel distance via horizontal edge scanning.
        # We scan in a vertical window of 20 pixels around ankle height level
        y_center = int((l_ankle_roi[1] + r_ankle_roi[1]) / 2.0)
        y_min = max(0, y_center - 5)
        y_max = min(thresh.shape[0], y_center + 15)
        
        gaps = []
        heel_centers = []
        for y_scan in range(y_min, y_max):
            row = thresh[y_scan, :]
            white_idx = np.where(row == 255)[0]
            if len(white_idx) >= 2:
                left_idx = white_idx[white_idx < mid_x]
                right_idx = white_idx[white_idx >= mid_x]
                if len(left_idx) > 0 and len(right_idx) > 0:
                    r_edge = left_idx[-1]  # Rightmost edge of left shoe
                    l_edge = right_idx[0]   # Leftmost edge of right shoe
                    gaps.append(max(0, l_edge - r_edge))
                    heel_centers.append((r_edge + l_edge) / 2.0)
                    
        if len(gaps) > 0:
            true_heel_dist = float(np.mean(gaps))
            heel_x = float(np.mean(heel_centers))
        else:
            true_heel_dist = 0.0

        # 8. Compute the official stance angle.
        # For Savdhan, the required angle is the included angle between the two feet,
        # measured from the detected common heel-touch point to each toe tip.
        image_plane_angle = None
        if toe_r is not None and toe_l is not None:
            vec_r = np.array([toe_r[0] - heel_x, toe_r[1] - heel_y], dtype=float)
            vec_l = np.array([toe_l[0] - heel_x, toe_l[1] - heel_y], dtype=float)
            denom = (np.linalg.norm(vec_r) * np.linalg.norm(vec_l)) + 1e-6
            cosine = np.clip(np.dot(vec_r, vec_l) / denom, -1.0, 1.0)
            image_plane_angle = float(np.degrees(np.arccos(cosine)))
        elif tilt_r is not None and tilt_l is not None:
            image_plane_angle = tilt_r + tilt_l
        elif tilt_r is not None:
            image_plane_angle = tilt_r * 2.0
        elif tilt_l is not None:
            image_plane_angle = tilt_l * 2.0

        # 9. Return unified geometry structure (with full-frame heel_touch origin).
        ground_plane_angle = None
        heel_to_heel_in = None
        toe_to_toe_in = None
        if ground_mapper is not None and ground_mapper.is_ready and toe_r is not None and toe_l is not None:
            image_points = np.asarray(
                [
                    [heel_x + offset[0], heel_y + offset[1]],
                    [toe_r[0] + offset[0], toe_r[1] + offset[1]],
                    [toe_l[0] + offset[0], toe_l[1] + offset[1]],
                    [r_ankle_roi[0] + offset[0], r_ankle_roi[1] + offset[1]],
                    [l_ankle_roi[0] + offset[0], l_ankle_roi[1] + offset[1]],
                ],
                dtype=float,
            )
            heel_ground, toe_r_ground, toe_l_ground, r_ankle_ground, l_ankle_ground = ground_mapper.transform_points(image_points)
            vec_r = toe_r_ground - heel_ground
            vec_l = toe_l_ground - heel_ground
            denom = (np.linalg.norm(vec_r) * np.linalg.norm(vec_l)) + 1e-6
            cosine = np.clip(np.dot(vec_r, vec_l) / denom, -1.0, 1.0)
            ground_plane_angle = float(np.degrees(np.arccos(cosine)))
            heel_to_heel_in = float(np.linalg.norm(r_ankle_ground - l_ankle_ground))
            toe_to_toe_in = float(np.linalg.norm(toe_r_ground - toe_l_ground))

        result = {
            "true_heel_dist": true_heel_dist,
            "image_plane_angle": image_plane_angle,
            "ground_plane_angle": ground_plane_angle,
            "heel_to_heel_in": heel_to_heel_in,
            "toe_to_toe_in": toe_to_toe_in,
            "pose_scale": abs(l_ankle_roi[0] - r_ankle_roi[0]),
            "roi_offset": offset,
            "toe_r": [toe_r[0] + offset[0], toe_r[1] + offset[1]] if toe_r else None,
            "toe_l": [toe_l[0] + offset[0], toe_l[1] + offset[1]] if toe_l else None,
            "heel_touch": [heel_x + offset[0], heel_y + offset[1]],
            "r_ankle_roi": r_ankle_roi,
            "l_ankle_roi": l_ankle_roi
        }
        
        # Save cache
        self._last_frame_id = frame_id
        self._last_keypoints = keypoints.copy()
        self._last_result = result
        
        return result
