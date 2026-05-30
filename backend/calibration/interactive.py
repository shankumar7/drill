import argparse
from pathlib import Path

import cv2
import numpy as np

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
