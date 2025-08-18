"""MediaPipe pose estimation for tennis serve analysis."""

import cv2
import mediapipe as mp
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import json
from rich.console import Console

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

class MediaPipePoseEstimator:
    """Pose estimation using MediaPipe Pose."""
    
    def __init__(self, confidence_threshold: float = 0.5):
        self.confidence_threshold = confidence_threshold
        
        # Initialize MediaPipe Pose
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=2,  # 0, 1, or 2
            smooth_landmarks=True,
            enable_segmentation=False,
            smooth_segmentation=True,
            min_detection_confidence=confidence_threshold,
            min_tracking_confidence=confidence_threshold
        )
        
        # Landmark names for tennis serve analysis
        self.landmark_names = {
            self.mp_pose.PoseLandmark.NOSE: "nose",
            self.mp_pose.PoseLandmark.LEFT_SHOULDER: "left_shoulder",
            self.mp_pose.PoseLandmark.RIGHT_SHOULDER: "right_shoulder",
            self.mp_pose.PoseLandmark.LEFT_ELBOW: "left_elbow",
            self.mp_pose.PoseLandmark.RIGHT_ELBOW: "right_elbow",
            self.mp_pose.PoseLandmark.LEFT_WRIST: "left_wrist",
            self.mp_pose.PoseLandmark.RIGHT_WRIST: "right_wrist",
            self.mp_pose.PoseLandmark.LEFT_HIP: "left_hip",
            self.mp_pose.PoseLandmark.RIGHT_HIP: "right_hip",
            self.mp_pose.PoseLandmark.LEFT_KNEE: "left_knee",
            self.mp_pose.PoseLandmark.RIGHT_KNEE: "right_knee",
            self.mp_pose.PoseLandmark.LEFT_ANKLE: "left_ankle",
            self.mp_pose.PoseLandmark.RIGHT_ANKLE: "right_ankle",
            self.mp_pose.PoseLandmark.LEFT_HEEL: "left_heel",
            self.mp_pose.PoseLandmark.RIGHT_HEEL: "right_heel",
            self.mp_pose.PoseLandmark.LEFT_FOOT_INDEX: "left_foot_index",
            self.mp_pose.PoseLandmark.RIGHT_FOOT_INDEX: "right_foot_index",
        }
    
    def estimate_pose_video(self, video_path: Path) -> List[PoseFrame]:
        """
        Estimate poses from a video file.
        
        Args:
            video_path: Path to the input video
            
        Returns:
            List of PoseFrame objects
        """
        console.print(f"[blue]Estimating poses from {video_path}[/blue]")
        
        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            raise ValueError(f"Could not open video file: {video_path}")
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        console.print(f"Processing {total_frames} frames at {fps:.2f} fps")
        
        pose_frames = []
        frame_count = 0
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            # Convert BGR to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Process frame
            results = self.pose.process(rgb_frame)
            
            if results.pose_landmarks:
                pose_frame = self._process_landmarks(
                    results, frame_count, frame_count / fps
                )
                pose_frames.append(pose_frame)
            
            frame_count += 1
            
            if frame_count % 100 == 0:
                console.print(f"Processed {frame_count}/{total_frames} frames")
        
        cap.release()
        self.pose.close()
        
        console.print(f"✅ Pose estimation completed: {len(pose_frames)} frames with poses")
        return pose_frames
    
    def _process_landmarks(
        self, 
        results: Any, 
        frame_number: int, 
        timestamp: float
    ) -> PoseFrame:
        """Process MediaPipe pose landmarks."""
        landmarks = {}
        world_landmarks = {}
        
        # Process 2D landmarks
        if results.pose_landmarks:
            for landmark_id, landmark in enumerate(results.pose_landmarks.landmark):
                if landmark_id in self.landmark_names:
                    name = self.landmark_names[landmark_id]
                    landmarks[name] = PoseLandmark(
                        x=landmark.x,
                        y=landmark.y,
                        z=landmark.z,
                        visibility=landmark.visibility,
                        presence=1.0
                    )
        
        # Process 3D world landmarks
        if results.pose_world_landmarks:
            for landmark_id, landmark in enumerate(results.pose_world_landmarks.landmark):
                if landmark_id in self.landmark_names:
                    name = self.landmark_names[landmark_id]
                    world_landmarks[name] = PoseLandmark(
                        x=landmark.x,
                        y=landmark.y,
                        z=landmark.z,
                        visibility=landmark.visibility,
                        presence=1.0
                    )
        
        return PoseFrame(
            frame_number=frame_number,
            timestamp=timestamp,
            landmarks=landmarks,
            world_landmarks=world_landmarks if world_landmarks else None
        )
    
    def save_pose_data(self, pose_frames: List[PoseFrame], output_path: Path):
        """Save pose data to JSON file."""
        data = []
        for frame in pose_frames:
            frame_data = {
                "frame_number": frame.frame_number,
                "timestamp": frame.timestamp,
                "landmarks": {}
            }
            
            # Convert landmarks to dict
            for name, landmark in frame.landmarks.items():
                frame_data["landmarks"][name] = {
                    "x": landmark.x,
                    "y": landmark.y,
                    "z": landmark.z,
                    "visibility": landmark.visibility,
                    "presence": landmark.presence
                }
            
            # Add world landmarks if available
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
        
        console.print(f"Saved pose data to {output_path}")
    
    def visualize_pose(
        self, 
        frame: np.ndarray, 
        pose_frame: PoseFrame,
        draw_connections: bool = True
    ) -> np.ndarray:
        """Visualize pose landmarks on a frame."""
        # Create a copy of the frame
        vis_frame = frame.copy()
        
        # Draw landmarks
        for name, landmark in pose_frame.landmarks.items():
            if landmark.visibility > self.confidence_threshold:
                x = int(landmark.x * frame.shape[1])
                y = int(landmark.y * frame.shape[0])
                cv2.circle(vis_frame, (x, y), 5, (0, 255, 0), -1)
                cv2.putText(vis_frame, name, (x + 10, y), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # TODO: Draw connections between landmarks
        if draw_connections:
            # Define connections for tennis serve analysis
            connections = [
                ("left_shoulder", "right_shoulder"),
                ("left_shoulder", "left_elbow"),
                ("left_elbow", "left_wrist"),
                ("right_shoulder", "right_elbow"),
                ("right_elbow", "right_wrist"),
                ("left_shoulder", "left_hip"),
                ("right_shoulder", "right_hip"),
                ("left_hip", "right_hip"),
                ("left_hip", "left_knee"),
                ("left_knee", "left_ankle"),
                ("right_hip", "right_knee"),
                ("right_knee", "right_ankle"),
            ]
            
            for start_name, end_name in connections:
                if start_name in pose_frame.landmarks and end_name in pose_frame.landmarks:
                    start_landmark = pose_frame.landmarks[start_name]
                    end_landmark = pose_frame.landmarks[end_name]
                    
                    if (start_landmark.visibility > self.confidence_threshold and 
                        end_landmark.visibility > self.confidence_threshold):
                        
                        start_x = int(start_landmark.x * frame.shape[1])
                        start_y = int(start_landmark.y * frame.shape[0])
                        end_x = int(end_landmark.x * frame.shape[1])
                        end_y = int(end_landmark.y * frame.shape[0])
                        
                        cv2.line(vis_frame, (start_x, start_y), (end_x, end_y), 
                                (255, 0, 0), 2)
        
        return vis_frame
