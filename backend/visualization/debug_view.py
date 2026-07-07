import cv2
from backend.core.types import PipelineResult


SKELETON = [
    (5, 6), (5, 7), (7, 9), (6, 8), (8, 10),
    (5, 11), (6, 12), (11, 12), (11, 13), (13, 15), (12, 14), (14, 16),
]


def _draw_skeleton(frame, keypoints, color_name="green", opacity=0.8):
    color_map = {
        "green": (0, 255, 0),
        "red": (0, 0, 255),
        "blue": (255, 0, 0),
        "yellow": (0, 255, 255),
        "cyan": (255, 255, 0),
        "orange": (0, 140, 255),
        "white": (255, 255, 255)
    }
    color = color_map.get(color_name.lower(), (0, 255, 0))
    
    overlay = frame.copy() if opacity < 1.0 else frame
    
    for start, end in SKELETON:
        if start < len(keypoints) and end < len(keypoints):
            p1, p2 = keypoints[start], keypoints[end]
            if p1[2] > 0.25 and p2[2] > 0.25:
                cv2.line(overlay, tuple(p1[:2].astype(int)), tuple(p2[:2].astype(int)), color, 2)
    for point in keypoints:
        if point[2] > 0.25:
            cv2.circle(overlay, tuple(point[:2].astype(int)), 3, color, -1)
            
    if opacity < 1.0:
        cv2.addWeighted(overlay, opacity, frame, 1 - opacity, 0, frame)

def render_debug_view(result: PipelineResult, show_foot_debug: bool = False):
    frame = result.packet.image.copy()
    for detection in result.detections:
        if detection.mask is not None:
            mask = detection.mask
            if mask.shape[:2] != frame.shape[:2]:
                mask = cv2.resize(mask, (frame.shape[1], frame.shape[0]), interpolation=cv2.INTER_NEAREST)
            mask = mask > 0.5
            colored = frame.copy()
            colored[mask] = (0, 120, 0)
            frame = cv2.addWeighted(colored, 0.35, frame, 0.65, 0)
        x1, y1, x2, y2 = detection.bbox.astype(int)
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(
            frame,
            f"ID {detection.track_id} {detection.confidence:.2f}",
            (x1, max(20, y1 - 8)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 255, 0),
            1,
        )
        if detection.evaluation is not None:
            label = detection.evaluation.status.upper()
            if detection.evaluation.overall_score is not None:
                label += f" {detection.evaluation.overall_score:.1f}"
            cv2.putText(
                frame,
                label,
                (x1, min(frame.shape[0] - 10, y2 + 18)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 255),
                1,
            )
            panel_x = max(8, x1)
            panel_y = max(48, y1)
            visible_rules = [rule for rule in detection.evaluation.rules if rule.status != "pass"]
            for offset, rule in enumerate(visible_rules):
                if rule.status == "pass":
                    color = (0, 255, 0)
                    marker = "PASS"
                elif rule.status == "fail":
                    color = (0, 0, 255)
                    marker = "FAIL"
                else:
                    color = (0, 215, 255)
                    marker = "N/A"
                text = f"{rule.name}: {marker}"
                if rule.score is not None:
                    text += f" {rule.score:.1f}"
                cv2.putText(
                    frame,
                    text,
                    (panel_x, panel_y + (offset * 18)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.45,
                    color,
                    1,
                )
        if show_foot_debug and detection.foot_geometry is not None:
            import numpy as np
            geometry = detection.foot_geometry
            heel = geometry.get("heel_touch")
            toe_l = geometry.get("toe_l")
            toe_r = geometry.get("toe_r")
            image_angle = geometry.get("image_plane_angle")
            if heel is not None:
                heel_pt = tuple(np.asarray(heel, dtype=int))
                cv2.circle(frame, heel_pt, 5, (255, 0, 255), -1)
                cv2.putText(
                    frame,
                    "HEEL",
                    (heel_pt[0] + 6, heel_pt[1] - 6),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.4,
                    (255, 0, 255),
                    1,
                )
                if toe_l is not None:
                    toe_l_pt = tuple(np.asarray(toe_l, dtype=int))
                    cv2.circle(frame, toe_l_pt, 5, (255, 255, 0), -1)
                    cv2.line(frame, heel_pt, toe_l_pt, (255, 255, 0), 2)
                    cv2.putText(frame, "L TOE", (toe_l_pt[0] + 6, toe_l_pt[1]), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 0), 1)
                if toe_r is not None:
                    toe_r_pt = tuple(np.asarray(toe_r, dtype=int))
                    cv2.circle(frame, toe_r_pt, 5, (255, 255, 0), -1)
                    cv2.line(frame, heel_pt, toe_r_pt, (255, 255, 0), 2)
                    cv2.putText(frame, "R TOE", (toe_r_pt[0] + 6, toe_r_pt[1]), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 0), 1)
                if image_angle is not None:
                    cv2.putText(
                        frame,
                        f"IMAGE ANGLE {image_angle:.1f} deg",
                        (heel_pt[0] - 40, heel_pt[1] - 18),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        (255, 255, 0),
                        1,
                    )
        for start, end in SKELETON:
            p1, p2 = detection.keypoints[start], detection.keypoints[end]
            if p1[2] > 0.25 and p2[2] > 0.25:
                cv2.line(frame, tuple(p1[:2].astype(int)), tuple(p2[:2].astype(int)), (255, 180, 0), 2)
        for point in detection.keypoints:
            if point[2] > 0.25:
                cv2.circle(frame, tuple(point[:2].astype(int)), 3, (0, 0, 255), -1)
    cv2.putText(
        frame,
        f"FPS {result.fps:.1f} | infer {result.inference_ms:.1f} ms | queue {result.queue_latency_ms:.1f} ms | drops {result.dropped_frames}",
        (12, 24),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (255, 255, 255),
        2,
    )
    return frame
