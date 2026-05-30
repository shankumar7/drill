import torch
from ultralytics import YOLO
import numpy as np

class YOLOPoseEstimator:
    def __init__(self, model_path="yolo11n-pose.pt", device=None):
        """
        Initializes the YOLO Pose Estimator.
        :param model_path: Path to the YOLO pose model (e.g., yolo11n-pose.pt)
        :param device: 'cuda' or 'cpu'. If None, automatically detects.
        """
        if device is None:
            self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        else:
            self.device = device
            
        print(f"Loading YOLO Pose model: {model_path} on {self.device}")
        self.model = YOLO(model_path)
        self.model.to(self.device)

    def predict(self, frame, conf=0.5, verbose=False):
        """
        Runs inference on a single frame.
        :param frame: OpenCV image (BGR)
        :param conf: Confidence threshold
        :return: list of results containing keypoints and bounding boxes
        """
        results = self.model.predict(
            source=frame, 
            conf=conf, 
            device=self.device, 
            verbose=verbose,
            half=(self.device == 'cuda')  # Use FP16 for speed on GPU
        )
        return results

    def extract_keypoints(self, results):
        """
        Extracts keypoints in a structured format.
        :param results: YOLO results object
        :return: List of dicts, each containing 'id', 'bbox', 'keypoints', 'conf'
        """
        processed_data = []
        for result in results:
            if result.keypoints is None:
                continue
                
            # result.keypoints.data is [num_persons, num_keypoints, 3] (x, y, conf)
            # result.boxes.data is [num_persons, 6] (x1, y1, x2, y2, conf, cls)
            
            keypoints_data = result.keypoints.data.cpu().numpy()
            boxes_data = result.boxes.data.cpu().numpy()
            
            # If tracking is enabled, IDs might be available
            ids = result.boxes.id.cpu().numpy() if result.boxes.id is not None else [None] * len(boxes_data)

            for i in range(len(keypoints_data)):
                processed_data.append({
                    'id': int(ids[i]) if ids[i] is not None else i,
                    'bbox': boxes_data[i][:4],
                    'box_conf': boxes_data[i][4],
                    'keypoints': keypoints_data[i], # [17, 3]
                })
        
        return processed_data
