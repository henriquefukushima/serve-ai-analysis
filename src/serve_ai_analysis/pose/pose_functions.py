"""Functional pose estimation module for tennis serve analysis."""

import cv2
import mediapipe as mp
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import json
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

@dataclass
class PoseLandmark:
    """Represents a single pose landmark."""
    x: float
    y: float
    z: float
    visibility: float
    presence: float

@dataclass
class PoseFrame:
    """Represents pose data for a single frame."""
    frame_number: int
    timestamp: float
    landmarks: Dict[str, PoseLandmark]
    world_landmarks: Optional[Dict[str, PoseLandmark]] = None

# Configuration constants
LANDMARK_NAMES = {
    mp.solutions.pose.PoseLandmark.NOSE: "nose",
    mp.solutions.pose.PoseLandmark.LEFT_SHOULDER: "left_shoulder",
    mp.solutions.pose.PoseLandmark.RIGHT_SHOULDER: "right_shoulder",
    mp.solutions.pose.PoseLandmark.LEFT_ELBOW: "left_elbow",
    mp.solutions.pose.PoseLandmark.RIGHT_ELBOW: "right_elbow",
    mp.solutions.pose.PoseLandmark.LEFT_WRIST: "left_wrist",
    mp.solutions.pose.PoseLandmark.RIGHT_WRIST: "right_wrist",
    mp.solutions.pose.PoseLandmark.LEFT_HIP: "left_hip",
    mp.solutions.pose.PoseLandmark.RIGHT_HIP: "right_hip",
    mp.solutions.pose.PoseLandmark.LEFT_KNEE: "left_knee",
    mp.solutions.pose.PoseLandmark.RIGHT_KNEE: "right_knee",
    mp.solutions.pose.PoseLandmark.LEFT_ANKLE: "left_ankle",
    mp.solutions.pose.PoseLandmark.RIGHT_ANKLE: "right_ankle",
    mp.solutions.pose.PoseLandmark.LEFT_HEEL: "left_heel",
    mp.solutions.pose.PoseLandmark.RIGHT_HEEL: "right_heel",
    mp.solutions.pose.PoseLandmark.LEFT_FOOT_INDEX: "left_foot_index",
    mp.solutions.pose.PoseLandmark.RIGHT_FOOT_INDEX: "right_foot_index",
}

def create_pose_estimator(confidence_threshold: float = 0.5) -> mp.solutions.pose.Pose:
    """Create and configure a MediaPipe Pose estimator."""
    return mp.solutions.pose.Pose(
        static_image_mode=False,
        model_complexity=1,
        smooth_landmarks=True,
        enable_segmentation=False,
        min_detection_confidence=confidence_threshold,
        min_tracking_confidence=confidence_threshold
    )

def extract_landmarks_from_results(results, frame_number: int, timestamp: float) -> Optional[PoseFrame]:
    """Extract landmarks from MediaPipe results and create a PoseFrame."""
    if not results.pose_landmarks:
        return None
    
    landmarks = {}
    world_landmarks = {}
    
    # Extract 2D landmarks
    for i, landmark in enumerate(results.pose_landmarks.landmark):
        if i in LANDMARK_NAMES:
            landmark_name = LANDMARK_NAMES[i]
            landmarks[landmark_name] = PoseLandmark(
                x=landmark.x,
                y=landmark.y,
                z=landmark.z,
                visibility=landmark.visibility,
                presence=landmark.presence
            )
    
    # Extract 3D world landmarks if available
    if results.pose_world_landmarks:
        for i, landmark in enumerate(results.pose_world_landmarks.landmark):
            if i in LANDMARK_NAMES:
                landmark_name = LANDMARK_NAMES[i]
                world_landmarks[landmark_name] = PoseLandmark(
                    x=landmark.x,
                    y=landmark.y,
                    z=landmark.z,
                    visibility=landmark.visibility,
                    presence=landmark.presence
                )
    
    return PoseFrame(
        frame_number=frame_number,
        timestamp=timestamp,
        landmarks=landmarks,
        world_landmarks=world_landmarks if world_landmarks else None
    )

def process_video_frame(frame: np.ndarray, pose: mp.solutions.pose.Pose, frame_number: int = 0, fps: float = 30.0) -> Optional[PoseFrame]:
    """Process a single video frame and extract pose landmarks."""
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(rgb_frame)
    
    if results.pose_landmarks:
        timestamp = frame_number / fps
        return extract_landmarks_from_results(results, frame_number, timestamp)
    
    return None

def estimate_pose_video(video_path: Path, confidence_threshold: float = 0.5) -> List[PoseFrame]:
    """Estimate poses from a video file using functional approach."""
    console.print(f"Estimating poses from {video_path}")
    
    pose = create_pose_estimator(confidence_threshold)
    pose_frames = []
    
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise ValueError(f"Could not open video: {video_path}")
    
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    console.print(f"Processing {total_frames} frames at {fps:.2f} fps")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Processing frames...", total=total_frames)
        
        frame_count = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            timestamp = frame_count / fps
            pose_frame = process_video_frame(frame, pose)
            
            if pose_frame:
                pose_frame.frame_number = frame_count
                pose_frame.timestamp = timestamp
                pose_frames.append(pose_frame)
            
            frame_count += 1
            progress.update(task, advance=1)
            
            if frame_count % 100 == 0:
                console.print(f"Processed {frame_count}/{total_frames} frames")
    
    cap.release()
    pose.close()
    
    console.print(f"✅ Pose estimation completed: {len(pose_frames)} frames with poses")
    return pose_frames

def save_pose_data(pose_frames: List[PoseFrame], output_path: Path):
    """Save pose data to JSON file."""
    data = []
    for frame in pose_frames:
        frame_data = {
            "frame_number": frame.frame_number,
            "timestamp": frame.timestamp,
            "landmarks": {}
        }
        
        for name, landmark in frame.landmarks.items():
            frame_data["landmarks"][name] = {
                "x": landmark.x,
                "y": landmark.y,
                "z": landmark.z,
                "visibility": landmark.visibility,
                "presence": landmark.presence
            }
        
        if frame.world_landmarks:
            frame_data["world_landmarks"] = {}
            for name, landmark in frame.world_landmarks.items():
                frame_data["world_landmarks"][name] = {
                    "x": landmark.x,
                    "y": landmark.y,
                    "z": landmark.z,
                    "visibility": landmark.visibility,
                    "presence": landmark.presence
                }
        
        data.append(frame_data)
    
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2)
    
    console.print(f"📊 Pose data saved to {output_path}")

def load_pose_data(input_path: Path) -> List[PoseFrame]:
    """Load pose data from JSON file."""
    with open(input_path, 'r') as f:
        data = json.load(f)
    
    pose_frames = []
    for frame_data in data:
        landmarks = {}
        for name, landmark_data in frame_data["landmarks"].items():
            landmarks[name] = PoseLandmark(
                x=landmark_data["x"],
                y=landmark_data["y"],
                z=landmark_data["z"],
                visibility=landmark_data["visibility"],
                presence=landmark_data["presence"]
            )
        
        world_landmarks = None
        if "world_landmarks" in frame_data:
            world_landmarks = {}
            for name, landmark_data in frame_data["world_landmarks"].items():
                world_landmarks[name] = PoseLandmark(
                    x=landmark_data["x"],
                    y=landmark_data["y"],
                    z=landmark_data["z"],
                    visibility=landmark_data["visibility"],
                    presence=landmark_data["presence"]
                )
        
        pose_frames.append(PoseFrame(
            frame_number=frame_data["frame_number"],
            timestamp=frame_data["timestamp"],
            landmarks=landmarks,
            world_landmarks=world_landmarks
        ))
    
    return pose_frames

def filter_pose_frames_by_visibility(pose_frames: List[PoseFrame], min_visibility: float = 0.5) -> List[PoseFrame]:
    """Filter pose frames based on landmark visibility."""
    def has_sufficient_visibility(frame: PoseFrame) -> bool:
        required_landmarks = ["left_wrist", "right_elbow", "right_shoulder", "right_wrist", "nose"]
        return all(
            landmark in frame.landmarks and frame.landmarks[landmark].presence >= min_visibility
            for landmark in required_landmarks
        )
    
    return list(filter(has_sufficient_visibility, pose_frames))

def get_landmark_position(pose_frame: PoseFrame, landmark_name: str) -> Optional[Tuple[float, float, float]]:
    """Get the position of a specific landmark from a pose frame."""
    if landmark_name in pose_frame.landmarks:
        landmark = pose_frame.landmarks[landmark_name]
        return (landmark.x, landmark.y, landmark.z)
    return None
