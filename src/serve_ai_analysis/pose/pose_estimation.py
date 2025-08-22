"""Pose estimation module for tennis serve analysis."""

import mediapipe as mp
import cv2
import numpy as np
from dataclasses import dataclass
from typing import List, Dict, Optional
from pathlib import Path


@dataclass
class PoseLandmark:
    """Represents a single pose landmark."""
    x: float
    y: float
    z: float
    visibility: float


@dataclass
class PoseFrame:
    """Represents pose data for a single frame."""
    frame_idx: int
    landmarks: Dict[str, PoseLandmark]
    timestamp: float


# MediaPipe landmark names for serve analysis
LANDMARK_NAMES = {
    'nose': 0,
    'left_shoulder': 11,
    'right_shoulder': 12,
    'left_elbow': 13,
    'right_elbow': 14,
    'left_wrist': 15,
    'right_wrist': 16,
    'left_hip': 23,
    'right_hip': 24,
    'left_knee': 25,
    'right_knee': 26,
    'left_ankle': 27,
    'right_ankle': 28
}


def estimate_pose_video(
    video_path: str,
    confidence_threshold: float = 0.5,
    model_complexity: int = 1
) -> List[PoseFrame]:
    """
    Estimate pose from video using MediaPipe.
    
    Args:
        video_path: Path to input video
        confidence_threshold: Minimum confidence for landmark detection
        model_complexity: MediaPipe model complexity (0, 1, 2)
    
    Returns:
        List of pose frames with landmarks
    """
    video_path = Path(video_path)
    if not video_path.exists():
        raise FileNotFoundError(f"Video file not found: {video_path}")
    
    # Initialize MediaPipe Pose
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose(
        static_image_mode=False,
        model_complexity=model_complexity,
        smooth_landmarks=True,
        enable_segmentation=False,
        smooth_segmentation=True,
        min_detection_confidence=confidence_threshold,
        min_tracking_confidence=confidence_threshold
    )
    
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise ValueError(f"Could not open video: {video_path}")
    
    fps = cap.get(cv2.CAP_PROP_FPS)
    pose_frames = []
    frame_idx = 0
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Convert BGR to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Process frame
            results = pose.process(rgb_frame)
            
            if results.pose_landmarks:
                landmarks = {}
                
                # Extract landmarks for serve analysis
                for name, landmark_id in LANDMARK_NAMES.items():
                    if landmark_id < len(results.pose_landmarks.landmark):
                        landmark = results.pose_landmarks.landmark[landmark_id]
                        
                        # Only include landmarks with sufficient visibility
                        if landmark.visibility >= confidence_threshold:
                            landmarks[name] = PoseLandmark(
                                x=landmark.x,
                                y=landmark.y,
                                z=landmark.z,
                                visibility=landmark.visibility
                            )
                
                # Only add frame if we have key landmarks for serve detection
                if len(landmarks) >= 5:  # At least nose, shoulders, and wrists
                    pose_frame = PoseFrame(
                        frame_idx=frame_idx,
                        landmarks=landmarks,
                        timestamp=frame_idx / fps
                    )
                    pose_frames.append(pose_frame)
            
            frame_idx += 1
            
    finally:
        cap.release()
        pose.close()
    
    return pose_frames


def filter_pose_frames_by_visibility(
    pose_frames: List[PoseFrame],
    min_landmarks: int = 5,
    min_visibility: float = 0.5
) -> List[PoseFrame]:
    """
    Filter pose frames based on landmark visibility.
    
    Args:
        pose_frames: List of pose frames
        min_landmarks: Minimum number of landmarks required
        min_visibility: Minimum visibility threshold
    
    Returns:
        Filtered list of pose frames
    """
    filtered = []
    
    for frame in pose_frames:
        # Count landmarks with sufficient visibility
        visible_landmarks = sum(
            1 for landmark in frame.landmarks.values()
            if landmark.visibility >= min_visibility
        )
        
        if visible_landmarks >= min_landmarks:
            filtered.append(frame)
    
    return filtered


def get_landmark_position(
    pose_frame: PoseFrame,
    landmark_name: str
) -> Optional[PoseLandmark]:
    """
    Get position of a specific landmark from a pose frame.
    
    Args:
        pose_frame: Pose frame data
        landmark_name: Name of the landmark to retrieve
    
    Returns:
        PoseLandmark if found, None otherwise
    """
    return pose_frame.landmarks.get(landmark_name)


def calculate_landmark_distance(
    landmark1: PoseLandmark,
    landmark2: PoseLandmark
) -> float:
    """
    Calculate Euclidean distance between two landmarks.
    
    Args:
        landmark1: First landmark
        landmark2: Second landmark
    
    Returns:
        Distance between landmarks
    """
    return np.sqrt(
        (landmark1.x - landmark2.x)**2 +
        (landmark1.y - landmark2.y)**2 +
        (landmark1.z - landmark2.z)**2
    )


def is_landmark_above(
    upper_landmark: PoseLandmark,
    lower_landmark: PoseLandmark,
    threshold: float = 0.1
) -> bool:
    """
    Check if one landmark is above another.
    
    Args:
        upper_landmark: Landmark that should be above
        lower_landmark: Landmark that should be below
        threshold: Minimum vertical distance threshold
    
    Returns:
        True if upper_landmark is above lower_landmark
    """
    return upper_landmark.y < lower_landmark.y - threshold


def get_pose_stats(pose_frames: List[PoseFrame]) -> dict:
    """
    Calculate statistics for pose data.
    
    Args:
        pose_frames: List of pose frames
    
    Returns:
        Dictionary with pose statistics
    """
    if not pose_frames:
        return {}
    
    total_frames = len(pose_frames)
    landmark_counts = []
    
    for frame in pose_frames:
        landmark_counts.append(len(frame.landmarks))
    
    return {
        'total_frames': total_frames,
        'avg_landmarks_per_frame': np.mean(landmark_counts),
        'min_landmarks': min(landmark_counts),
        'max_landmarks': max(landmark_counts),
        'frame_span': pose_frames[-1].frame_idx - pose_frames[0].frame_idx + 1,
        'time_span': pose_frames[-1].timestamp - pose_frames[0].timestamp
    }
