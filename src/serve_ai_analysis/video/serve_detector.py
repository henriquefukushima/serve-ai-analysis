"""Tennis serve detection using pose landmarks."""

import cv2
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
import json
import mediapipe as mp
from collections import deque

from ..pose.mediapipe_pose import MediaPipePoseEstimator, PoseFrame

console = Console()

@dataclass
class ServeEvent:
    """Represents a detected serve event."""
    start_frame: int
    end_frame: int
    start_time: float
    end_time: float
    duration: float
    confidence: float
    serve_type: str
    ball_toss_frame: Optional[int] = None
    contact_frame: Optional[int] = None
    follow_through_frame: Optional[int] = None

class ServeDetector:
    """Detect tennis serves using the proven 3-condition approach."""
    
    def __init__(
        self,
        min_serve_duration: float = 1.5,
        max_serve_duration: float = 8.0,  # Increased to accommodate 6s buffer
        confidence_threshold: float = 0.5,
        min_visibility: float = 0.5,
        serve_buffer_seconds: float = 3.0,  # Capture 3s before and after
        detection_cooldown_frames: int = 90,  # 3 seconds at 30fps to prevent multiple detections
        min_gap_between_serves: float = 2.0  # Minimum 2 seconds between serves
    ):
        self.min_serve_duration = min_serve_duration
        self.max_serve_duration = max_serve_duration
        self.confidence_threshold = confidence_threshold
        self.min_visibility = min_visibility
        self.serve_buffer_seconds = serve_buffer_seconds
        self.detection_cooldown_frames = detection_cooldown_frames
        self.min_gap_between_serves = min_gap_between_serves
        
        # Initialize pose estimator
        self.pose_estimator = MediaPipePoseEstimator(confidence_threshold=confidence_threshold)
        
    def detect_serves(self, video_path: Path) -> List[ServeEvent]:
        """
        Detect serves using the proven 3-condition approach.
        
        Args:
            video_path: Path to the input video
            
        Returns:
            List of detected serve events
        """
        console.print(f"[blue]Detecting serves in {video_path.name}[/blue]")
        
        # Extract pose data
        pose_frames = self.pose_estimator.estimate_pose_video(video_path)
        
        if not pose_frames:
            console.print("[yellow]No pose data detected. Check video quality and person visibility.[/yellow]")
            return []
        
        console.print(f"📊 Extracted {len(pose_frames)} frames with pose data")
        
        # Detect serves using the refined approach
        serve_events = self._detect_serves_refined(pose_frames, video_path.stem)
        
        # Remove overlapping serves
        serve_events = self._remove_overlapping_serves(serve_events)
        
        console.print(f"✅ Detected {len(serve_events)} serves")
        return serve_events
    
    def _detect_serves_refined(self, pose_frames: List[PoseFrame], video_name: str) -> List[ServeEvent]:
        """
        Detect serves using a refined approach:
        1. Find ball toss preparation (left wrist above nose)
        2. Find serve windup (right elbow above right shoulder)
        3. Find serve contact moment (right wrist at highest point with forward motion)
        4. Capture 3s before and 3s after contact moment
        """
        serve_events = []
        
        # Initialize tracking variables
        serve_count = 0
        fps = 30.0  # Approximate fps
        buffer_frames = int(self.serve_buffer_seconds * fps)
        min_gap_frames = int(self.min_gap_between_serves * fps)
        last_detection_frame = -self.detection_cooldown_frames  # Initialize to allow first detection
        
        # Track serve phases
        ball_toss_detected = False
        windup_detected = False
        contact_detected = False
        contact_frame = None
        
        # Track the end frame of the last detected serve to prevent overlap
        last_serve_end_frame = -1
        
        # Process each frame
        for frame_idx, frame in enumerate(pose_frames):
            # Skip if we're still within the last serve's range
            if frame_idx <= last_serve_end_frame:
                continue
                
            # Check if we have the required landmarks
            required_landmarks = ["left_wrist", "right_elbow", "right_shoulder", "right_wrist", "nose"]
            if not all(landmark in frame.landmarks for landmark in required_landmarks):
                continue
            
            # Get landmark positions
            left_wrist = frame.landmarks["left_wrist"]
            right_elbow = frame.landmarks["right_elbow"]
            right_shoulder = frame.landmarks["right_shoulder"]
            right_wrist = frame.landmarks["right_wrist"]
            nose = frame.landmarks["nose"]
            
            # Check visibility
            if (left_wrist.presence < self.min_visibility or 
                right_elbow.presence < self.min_visibility or 
                right_shoulder.presence < self.min_visibility or
                right_wrist.presence < self.min_visibility or
                nose.presence < self.min_visibility):
                continue
            
            # Check cooldown period to prevent multiple detections
            if frame_idx - last_detection_frame < self.detection_cooldown_frames:
                continue
            
            # Phase 1: Ball toss preparation (left wrist above nose)
            if left_wrist.y < nose.y:
                ball_toss_detected = True
            
            # Phase 2: Serve windup (right elbow above right shoulder)
            if ball_toss_detected and right_elbow.y < right_shoulder.y:
                windup_detected = True
            
            # Phase 3: Serve contact moment (right wrist at highest point with forward motion)
            if windup_detected and not contact_detected:
                # Check if this is the serve contact moment
                if self._is_serve_contact_moment(pose_frames, frame_idx, right_wrist, right_shoulder):
                    contact_detected = True
                    contact_frame = frame_idx
                    serve_count += 1
                    last_detection_frame = frame_idx  # Update last detection frame
                    console.print(f"🎾 Serve {serve_count} contact detected at frame {frame_idx}")
                    
                    # Calculate serve boundaries with contact as center
                    start_frame = max(last_serve_end_frame + 1, contact_frame - buffer_frames)
                    end_frame = min(len(pose_frames) - 1, contact_frame + buffer_frames)
                    
                    # Update last serve end frame to prevent overlap
                    last_serve_end_frame = end_frame
                    
                    # Calculate serve duration
                    serve_duration = pose_frames[end_frame].timestamp - pose_frames[start_frame].timestamp
                    
                    # Debug information
                    console.print(f"🔍 Serve {serve_count} duration: {serve_duration:.1f}s (frames {start_frame}-{end_frame})")
                    
                    if self.min_serve_duration <= serve_duration <= self.max_serve_duration:
                        # Validate the serve segment
                        if self._validate_serve_segment(start_frame, end_frame, pose_frames):
                            # Create serve event using video name as serve type
                            serve_event = ServeEvent(
                                start_frame=start_frame,
                                end_frame=end_frame,
                                start_time=pose_frames[start_frame].timestamp,
                                end_time=pose_frames[end_frame].timestamp,
                                duration=serve_duration,
                                confidence=1.0,
                                serve_type=video_name,  # Use video name instead of direction classification
                                contact_frame=contact_frame
                            )
                            
                            serve_events.append(serve_event)
                            console.print(f"✅ Serve {serve_count} completed: {serve_duration:.1f}s (frames {start_frame}-{end_frame})")
                        else:
                            console.print(f"❌ Serve {serve_count} rejected: insufficient serve motion")
                    else:
                        console.print(f"❌ Serve {serve_count} rejected: duration {serve_duration:.1f}s outside range [{self.min_serve_duration}, {self.max_serve_duration}]")
                    
                    # Reset for next serve
                    ball_toss_detected = windup_detected = contact_detected = False
                    contact_frame = None
        
        return serve_events
    
    def _is_serve_contact_moment(self, pose_frames: List[PoseFrame], frame_idx: int, right_wrist, right_shoulder) -> bool:
        """
        Determine if this frame represents the serve contact moment.
        Contact moment is when the wrist is at its highest point with forward motion.
        """
        # Add more stringent conditions
        if right_wrist.y >= right_shoulder.y:
            return False
        
        # Check for sustained high position (not just a momentary peak)
        window_size = 10
        start_idx = max(0, frame_idx - window_size)
        end_idx = min(len(pose_frames), frame_idx + window_size)
        
        high_position_frames = 0
        for i in range(start_idx, end_idx):
            if "right_wrist" in pose_frames[i].landmarks:
                wrist = pose_frames[i].landmarks["right_wrist"]
                if wrist.y < right_shoulder.y:
                    high_position_frames += 1
        
        # Require at least 60% of frames in window to be in high position
        if high_position_frames < (end_idx - start_idx) * 0.6:
            return False
        
        # Look for the highest point of the wrist in recent frames
        window_size = 15  # Look at 15 frames around current frame
        start_idx = max(0, frame_idx - window_size)
        end_idx = min(len(pose_frames), frame_idx + window_size)
        
        highest_wrist_y = float('inf')
        highest_frame = frame_idx
        
        for i in range(start_idx, end_idx):
            if "right_wrist" in pose_frames[i].landmarks:
                wrist = pose_frames[i].landmarks["right_wrist"]
                if wrist.y < highest_wrist_y:
                    highest_wrist_y = wrist.y
                    highest_frame = i
        
        # Check if current frame is at or near the highest point
        if abs(frame_idx - highest_frame) <= 3:  # Within 3 frames of highest point
            # Check for forward motion (wrist moving forward)
            if frame_idx > 0 and frame_idx < len(pose_frames) - 1:
                prev_wrist = pose_frames[frame_idx - 1].landmarks["right_wrist"]
                next_wrist = pose_frames[frame_idx + 1].landmarks["right_wrist"]
                
                # Forward motion: x position increasing
                if next_wrist.x > prev_wrist.x:
                    return True
        
        return False
    
    def _validate_serve_segment(self, start_frame: int, end_frame: int, pose_frames: List[PoseFrame]) -> bool:
        """Validate that a serve segment contains actual serve motion."""
        
        # Check for minimum motion in the serve segment
        motion_frames = 0
        total_frames = end_frame - start_frame + 1
        
        for i in range(start_frame, min(end_frame + 1, len(pose_frames))):
            if "right_wrist" in pose_frames[i].landmarks:
                wrist = pose_frames[i].landmarks["right_wrist"]
                # Check if wrist is in serve position (above shoulder)
                if i > start_frame and "right_shoulder" in pose_frames[i-1].landmarks:
                    prev_shoulder = pose_frames[i-1].landmarks["right_shoulder"]
                    if wrist.y < prev_shoulder.y:
                        motion_frames += 1
        
        # Require at least 30% of frames to show serve motion
        return motion_frames >= total_frames * 0.3
    
    def _remove_overlapping_serves(self, serve_events: List[ServeEvent]) -> List[ServeEvent]:
        """Remove overlapping serve events, keeping the one with higher confidence."""
        if not serve_events:
            return serve_events
        
        # Sort by start frame
        serve_events.sort(key=lambda x: x.start_frame)
        
        filtered_events = [serve_events[0]]
        
        for current_serve in serve_events[1:]:
            last_serve = filtered_events[-1]
            
            # Check for overlap
            if current_serve.start_frame <= last_serve.end_frame:
                # Overlap detected - keep the one with higher confidence
                if current_serve.confidence > last_serve.confidence:
                    filtered_events[-1] = current_serve
            else:
                filtered_events.append(current_serve)
        
        return filtered_events
    
    def save_serve_events(self, serve_events: List[ServeEvent], output_path: Path):
        """Save serve events to JSON file."""
        data = []
        for event in serve_events:
            event_data = {
                "start_frame": event.start_frame,
                "end_frame": event.end_frame,
                "start_time": event.start_time,
                "end_time": event.end_time,
                "duration": event.duration,
                "confidence": event.confidence,
                "serve_type": event.serve_type,
                "ball_toss_frame": event.ball_toss_frame,
                "contact_frame": event.contact_frame,
                "follow_through_frame": event.follow_through_frame
            }
            data.append(event_data)
        
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        console.print(f"📊 Serve events saved to {output_path}")
    
    def extract_serve_videos_with_pose(
        self, 
        video_path: Path, 
        serve_events: List[ServeEvent], 
        output_dir: Path
    ) -> List[Path]:
        """Extract individual serve videos with pose visualization in portrait orientation."""
        output_paths = []
        
        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            raise ValueError(f"Could not open video: {video_path}")
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        # For portrait orientation, swap width and height
        portrait_width = height
        portrait_height = width
        
        # Initialize MediaPipe for pose visualization
        mp_pose = mp.solutions.pose
        mp_drawing = mp.solutions.drawing_utils
        pose = mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            smooth_landmarks=True,
            enable_segmentation=False,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        for i, serve_event in enumerate(serve_events):
            # Use video name and serve number for naming
            video_name = serve_event.serve_type
            output_path = output_dir / f"{video_name}_{i+1}.mp4"
            
            # Create video writer for portrait orientation
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(str(output_path), fourcc, fps, (portrait_width, portrait_height))
            
            # Extract frames with pose visualization
            cap.set(cv2.CAP_PROP_POS_FRAMES, serve_event.start_frame)
            
            for frame_idx in range(serve_event.start_frame, serve_event.end_frame + 1):
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Rotate frame to portrait orientation (90 degrees clockwise)
                frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
                
                # Add pose visualization
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = pose.process(rgb_frame)
                
                # Draw pose landmarks
                if results.pose_landmarks:
                    mp_drawing.draw_landmarks(
                        frame, 
                        results.pose_landmarks, 
                        mp_pose.POSE_CONNECTIONS,
                        mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                        mp_drawing.DrawingSpec(color=(255, 0, 0), thickness=2)
                    )
                
                # Add frame info
                cv2.putText(frame, f"Frame: {frame_idx}", (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                cv2.putText(frame, f"Serve {i+1} ({video_name})", (10, 70), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                
                # Highlight contact frame if available
                if serve_event.contact_frame and frame_idx == serve_event.contact_frame:
                    cv2.putText(frame, "CONTACT!", (10, 110), 
                               cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
                
                out.write(frame)
            
            out.release()
            output_paths.append(output_path)
            
            console.print(f"✅ Extracted serve {i+1} ({video_name}) to {output_path.name}")
        
        cap.release()
        pose.close()
        return output_paths
    
    def extract_serve_videos(
        self, 
        video_path: Path, 
        serve_events: List[ServeEvent], 
        output_dir: Path
    ) -> List[Path]:
        """Extract individual serve videos (legacy method for compatibility)."""
        return self.extract_serve_videos_with_pose(video_path, serve_events, output_dir)
