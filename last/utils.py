# backend/app/utils.py
import cv2
import numpy as np
from mediapipe.python.solutions import pose as mp_pose

mp_pose_module = mp_pose

def detect_pose_landmarks_from_bgr(image_bgr):
    """
    Returns dictionary of landmark pixel coords: {'left_shoulder':(x,y), ...}
    or None if no person detected.
    """
    with mp_pose_module.Pose(static_image_mode=True, min_detection_confidence=0.5) as pose:
        img_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
        results = pose.process(img_rgb)
        if not results.pose_landmarks:
            return None
        h, w, _ = image_bgr.shape
        lm = results.pose_landmarks.landmark
        mapping = {
            'left_shoulder': mp_pose_module.PoseLandmark.LEFT_SHOULDER,
            'right_shoulder': mp_pose_module.PoseLandmark.RIGHT_SHOULDER,
            'left_hip': mp_pose_module.PoseLandmark.LEFT_HIP,
            'right_hip': mp_pose_module.PoseLandmark.RIGHT_HIP,
            'left_knee': mp_pose_module.PoseLandmark.LEFT_KNEE,
            'right_knee': mp_pose_module.PoseLandmark.RIGHT_KNEE,
            'left_ankle': mp_pose_module.PoseLandmark.LEFT_ANKLE,
            'right_ankle': mp_pose_module.PoseLandmark.RIGHT_ANKLE
        }
        out = {}
        for name, idx in mapping.items():
            lm_i = lm[idx.value]
            out[name] = (float(lm_i.x * w), float(lm_i.y * h))
        return out
