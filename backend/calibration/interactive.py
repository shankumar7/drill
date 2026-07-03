import argparse
from pathlib import Path

import cv2
import numpy as np
import json
import os

# Path to camera mapping config
CAMERA_MAPPING_FILE = os.path.join(os.path.dirname(__file__), "..", "..", "camera_mapping.json")

def load_camera_mapping():
    """Load camera mapping from JSON file if it exists, else default mapping."""
    default = {"front": 0, "back": 1, "side": 2}
    try:
        with open(CAMERA_MAPPING_FILE, "r") as f:
            data = json.load(f)
            # Ensure all required keys exist
            for key in default:
                if key not in data:
                    data[key] = default[key]
            return data
    except Exception:
        return default

# Global mapping dictionary
camera_mapping = load_camera_mapping()

def set_camera_mapping(front: int, back: int, side: int):
    """Update the global camera mapping and persist to file."""
    global camera_mapping
    camera_mapping = {"front": front, "back": back, "side": side}
    try:
        with open(CAMERA_MAPPING_FILE, "w") as f:
            json.dump(camera_mapping, f, indent=2)
    except Exception as e:
        print(f"Failed to save camera mapping: {e}")

def get_camera_mapping():
    """Return current camera mapping."""
    return camera_mapping


from backend.calibration.ground_plane import GroundPlaneMapper


WINDOW = "Floor Calibration - click TL, TR, BR, BL"


def calibrate_from_frame(frame, output_path: str, width_in: float, depth_in: float) -> None:
    clicked: list[tuple[int, int]] = []

    def on_mouse(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN and len(clicked) < 4:
            clicked.append((x, y))

    while True:
        canvas = frame.copy()
        for index, point in enumerate(clicked):
            cv2.circle(canvas, point, 6, (0, 0, 255), -1)
            cv2.putText(canvas, str(index + 1), (point[0] + 8, point[1] - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        cv2.putText(canvas, "Click floor corners: TL, TR, BR, BL | s=save r=reset q=quit", (15, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2)
        cv2.imshow(WINDOW, canvas)
        cv2.setMouseCallback(WINDOW, on_mouse)
        key = cv2.waitKey(20) & 0xFF
        if key == ord("r"):
            clicked.clear()
        elif key == ord("q"):
            break
        elif key == ord("s") and len(clicked) == 4:
            image_points = np.asarray(clicked, dtype=float)
            floor_points = np.asarray(
                [[0.0, 0.0], [width_in, 0.0], [width_in, depth_in], [0.0, depth_in]],
                dtype=float,
            )
            mapper = GroundPlaneMapper.estimate(image_points, floor_points)
            mapper.save(output_path)
            break
    cv2.destroyAllWindows()


def main() -> None:
    parser = argparse.ArgumentParser(description="Create floor homography calibration")
    parser.add_argument("--source", default="0")
    parser.add_argument("--output", default="calibration/floor_homography.yaml")
    parser.add_argument("--width-in", type=float, required=True)
    parser.add_argument("--depth-in", type=float, required=True)
    args = parser.parse_args()
    source = int(args.source) if args.source.isdigit() else args.source
    capture = cv2.VideoCapture(source)
    ok, frame = capture.read()
    capture.release()
    if not ok:
        raise RuntimeError(f"Unable to capture calibration frame from source: {source}")
    calibrate_from_frame(frame, args.output, args.width_in, args.depth_in)


if __name__ == "__main__":
    main()
