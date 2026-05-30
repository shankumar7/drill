import torch
from ultralytics import YOLO
import numpy as np

class MilitaryPoseEngine:
    def __init__(self, pose_model="yolo11n-pose.pt", seg_model="yolo11n-seg.pt"):
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print(f"Initializing Military AI Engine on {self.device}")
        
        if self.device == 'cpu':
            print("WARNING: CUDA not detected. Performance will be limited. Re-install torch with CUDA support.")
        
        self.pose_model = YOLO(pose_model).to(self.device)
        self.seg_model = YOLO(seg_model).to(self.device)
        
        # Optimization: Frame counting for segmentation skipping
        self.frame_count = 0
        self.last_seg_results = None
        
    def predict(self, frame):
        """
        Runs Pose every frame, but Segment only every N frames to boost FPS.
        """
        self.frame_count += 1
        
        # 1. Run Pose (Every frame)
        # imgsz=480 instead of 640 to increase speed significantly
        pose_results = self.pose_model.predict(
            source=frame, 
            conf=0.4, 
            device=self.device, 
            verbose=False,
            imgsz=480, 
            half=(self.device == 'cuda')
        )
        
        # 2. Run Segmentation (Only every 4th frame)
        if self.frame_count % 4 == 0 or self.last_seg_results is None:
            self.last_seg_results = self.seg_model.predict(
                source=frame, 
                conf=0.4, 
                classes=[0], 
                device=self.device, 
                verbose=False,
                imgsz=480,
                half=(self.device == 'cuda')
            )
        
        return pose_results, self.last_seg_results

    def process_results(self, pose_results, seg_results):
        cadets = []
        for result in pose_results:
            if result.keypoints is None: continue
            kpts = result.keypoints.data.cpu().numpy()
            boxes = result.boxes.data.cpu().numpy()
            ids = result.boxes.id.cpu().numpy() if result.boxes.id is not None else [None]*len(boxes)
            
            for i in range(len(kpts)):
                cadet = {
                    'id': int(ids[i]) if ids[i] is not None else i,
                    'bbox': boxes[i][:4],
                    'conf': boxes[i][4],
                    'keypoints': kpts[i],
                    'mask': None
                }
                
                # Match mask (from the last cached segmentation)
                if seg_results and seg_results[0].masks is not None:
                    masks = seg_results[0].masks.data.cpu().numpy()
                    best_iou = 0
                    for m_idx, mask in enumerate(masks):
                        # Simple bbox approximation for speed
                        m_y, m_x = np.where(mask > 0.5)
                        if len(m_y) == 0: continue
                        m_bbox = [np.min(m_x), np.min(m_y), np.max(m_x), np.max(m_y)]
                        
                        iou = self._calculate_iou(cadet['bbox'], m_bbox)
                        if iou > best_iou:
                            best_iou = iou
                            cadet['mask'] = mask
                
                cadets.append(cadet)
        return cadets

    def _calculate_iou(self, boxA, boxB):
        xA, yA, xB, yB = max(boxA[0], boxB[0]), max(boxA[1], boxB[1]), min(boxA[2], boxB[2]), min(boxA[3], boxB[3])
        interArea = max(0, xB - xA + 1) * max(0, yB - yA + 1)
        if interArea == 0: return 0
        boxAArea = (boxA[2] - boxA[0] + 1) * (boxA[3] - boxA[1] + 1)
        boxBArea = (boxB[2] - boxB[0] + 1) * (boxB[3] - boxB[1] + 1)
        return interArea / float(boxAArea + boxBArea - interArea)
