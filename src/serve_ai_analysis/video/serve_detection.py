"""Serve detection module for tennis serve analysis."""

from dataclasses import dataclass
from typing import List, Tuple, Optional, Dict
import numpy as np
from enum import Enum

from ..pose.pose_estimation import PoseFrame, PoseLandmark, get_landmark_position, is_landmark_above
from .ball_detection import BallDetection


@dataclass
class ServeEvent:
    """Represents a detected serve event."""
    start_frame: int
    end_frame: int
    ball_toss_frame: int
    contact_frame: int
    follow_through_frame: int
    confidence: float


class ServePhase(Enum):
    """Serve detection phases."""
    WAITING = "waiting"
    BALL_TOSS = "ball_toss"
    CONTACT = "contact"
    FOLLOW_THROUGH = "follow_through"
    COMPLETED = "completed"


@dataclass
class ServeState:
    """State machine for serve detection."""
    phase: ServePhase
    start_frame: Optional[int] = None
    ball_toss_frame: Optional[int] = None
    contact_frame: Optional[int] = None
    follow_through_frame: Optional[int] = None
    confidence_scores: List[float] = None
    
    def __post_init__(self):
        if self.confidence_scores is None:
            self.confidence_scores = []


# Default configuration for serve detection
DEFAULT_SERVE_CONFIG = {
    'ball_toss_min_frames': 5,  # Minimum frames for ball toss phase
    'contact_min_frames': 3,    # Minimum frames for contact phase
    'follow_through_min_frames': 5,  # Minimum frames for follow-through
    'serve_min_duration': 15,   # Minimum total serve duration (frames)
    'serve_max_duration': 120,  # Maximum total serve duration (frames)
    'confidence_threshold': 0.6,  # Minimum confidence for serve detection
    'nose_threshold': 0.1,      # Vertical threshold for "above nose"
    'shoulder_threshold': 0.05,  # Vertical threshold for "below shoulder"
}


def detect_serves(
    pose_frames: List[PoseFrame],
    ball_detections: List[BallDetection],
    config: Optional[Dict] = None
) -> List[ServeEvent]:
    """
    Detect serves using pose and ball trajectory data.
    
    Args:
        pose_frames: List of pose frames
        ball_detections: List of ball detections
        config: Configuration dictionary
    
    Returns:
        List of detected serve events
    """
    if not pose_frames:
        return []
    
    config = config or DEFAULT_SERVE_CONFIG.copy()
    serve_events = []
    current_state = ServeState(phase=ServePhase.WAITING)
    
    for i, pose_frame in enumerate(pose_frames):
        # Get ball detection for this frame if available
        ball_detection = None
        for ball in ball_detections:
            if ball.frame_idx == pose_frame.frame_idx:
                ball_detection = ball
                break
        
        # Update state machine
        new_state, serve_event = update_serve_state(
            current_state, pose_frame, ball_detection, config
        )
        
        if serve_event:
            serve_events.append(serve_event)
            # Reset state for next serve
            current_state = ServeState(phase=ServePhase.WAITING)
        else:
            current_state = new_state
    
    return serve_events


def update_serve_state(
    current_state: ServeState,
    pose_frame: PoseFrame,
    ball_detection: Optional[BallDetection],
    config: Dict
) -> Tuple[ServeState, Optional[ServeEvent]]:
    """
    Update serve state machine and return completed serve if detected.
    
    Args:
        current_state: Current serve state
        pose_frame: Current pose frame
        ball_detection: Current ball detection (optional)
        config: Configuration dictionary
    
    Returns:
        Tuple of (new_state, serve_event)
    """
    frame_idx = pose_frame.frame_idx
    
    # Get key landmarks
    nose = get_landmark_position(pose_frame, 'nose')
    left_wrist = get_landmark_position(pose_frame, 'left_wrist')
    right_wrist = get_landmark_position(pose_frame, 'right_wrist')
    left_shoulder = get_landmark_position(pose_frame, 'left_shoulder')
    right_shoulder = get_landmark_position(pose_frame, 'right_shoulder')
    
    if not all([nose, left_wrist, right_wrist, left_shoulder, right_shoulder]):
        return current_state, None
    
    # Calculate confidence for this frame
    frame_confidence = calculate_frame_confidence(
        pose_frame, ball_detection, config
    )
    
    if current_state.phase == ServePhase.WAITING:
        # Check for ball toss initiation (left wrist above nose)
        if is_landmark_above(left_wrist, nose, config['nose_threshold']):
            new_state = ServeState(
                phase=ServePhase.BALL_TOSS,
                start_frame=frame_idx,
                ball_toss_frame=frame_idx,
                confidence_scores=[frame_confidence]
            )
            return new_state, None
    
    elif current_state.phase == ServePhase.BALL_TOSS:
        # Continue ball toss phase
        current_state.confidence_scores.append(frame_confidence)
        
        # Check for contact phase (right wrist above nose)
        if is_landmark_above(right_wrist, nose, config['nose_threshold']):
            # Must have minimum ball toss duration
            if len(current_state.confidence_scores) >= config['ball_toss_min_frames']:
                new_state = ServeState(
                    phase=ServePhase.CONTACT,
                    start_frame=current_state.start_frame,
                    ball_toss_frame=current_state.ball_toss_frame,
                    contact_frame=frame_idx,
                    confidence_scores=current_state.confidence_scores + [frame_confidence]
                )
                return new_state, None
        
        # Check if ball toss phase is too long
        if len(current_state.confidence_scores) > config['serve_max_duration']:
            return ServeState(phase=ServePhase.WAITING), None
    
    elif current_state.phase == ServePhase.CONTACT:
        # Continue contact phase
        current_state.confidence_scores.append(frame_confidence)
        
        # Check for follow-through phase (right wrist below shoulder)
        if not is_landmark_above(right_wrist, right_shoulder, config['shoulder_threshold']):
            # Must have minimum contact duration
            if len(current_state.confidence_scores) >= config['contact_min_frames']:
                new_state = ServeState(
                    phase=ServePhase.FOLLOW_THROUGH,
                    start_frame=current_state.start_frame,
                    ball_toss_frame=current_state.ball_toss_frame,
                    contact_frame=current_state.contact_frame,
                    follow_through_frame=frame_idx,
                    confidence_scores=current_state.confidence_scores + [frame_confidence]
                )
                return new_state, None
        
        # Check if contact phase is too long
        if len(current_state.confidence_scores) > config['serve_max_duration']:
            return ServeState(phase=ServePhase.WAITING), None
    
    elif current_state.phase == ServePhase.FOLLOW_THROUGH:
        # Continue follow-through phase
        current_state.confidence_scores.append(frame_confidence)
        
        # Check if follow-through is complete
        if len(current_state.confidence_scores) >= config['follow_through_min_frames']:
            # Validate serve duration
            total_duration = len(current_state.confidence_scores)
            if (config['serve_min_duration'] <= total_duration <= config['serve_max_duration']):
                # Calculate overall confidence
                avg_confidence = np.mean(current_state.confidence_scores)
                
                if avg_confidence >= config['confidence_threshold']:
                    serve_event = ServeEvent(
                        start_frame=current_state.start_frame,
                        end_frame=frame_idx,
                        ball_toss_frame=current_state.ball_toss_frame,
                        contact_frame=current_state.contact_frame,
                        follow_through_frame=current_state.follow_through_frame,
                        confidence=avg_confidence
                    )
                    return ServeState(phase=ServePhase.WAITING), serve_event
        
        # Check if follow-through is too long
        if len(current_state.confidence_scores) > config['serve_max_duration']:
            return ServeState(phase=ServePhase.WAITING), None
    
    # Continue current phase
    current_state.confidence_scores.append(frame_confidence)
    return current_state, None


def calculate_frame_confidence(
    pose_frame: PoseFrame,
    ball_detection: Optional[BallDetection],
    config: Dict
) -> float:
    """
    Calculate confidence score for a frame based on pose and ball data.
    
    Args:
        pose_frame: Current pose frame
        ball_detection: Current ball detection (optional)
        config: Configuration dictionary
    
    Returns:
        Confidence score between 0 and 1
    """
    confidence_scores = []
    
    # Pose confidence (average visibility of key landmarks)
    key_landmarks = ['nose', 'left_wrist', 'right_wrist', 'left_shoulder', 'right_shoulder']
    pose_visibilities = []
    
    for landmark_name in key_landmarks:
        landmark = get_landmark_position(pose_frame, landmark_name)
        if landmark:
            pose_visibilities.append(landmark.visibility)
    
    if pose_visibilities:
        confidence_scores.append(np.mean(pose_visibilities))
    
    # Ball detection confidence
    if ball_detection:
        confidence_scores.append(ball_detection.confidence)
    
    # Return average confidence, or 0.5 if no data
    return np.mean(confidence_scores) if confidence_scores else 0.5





def validate_serve_event(serve_event: ServeEvent, config: Dict) -> bool:
    """
    Validate a detected serve event.
    
    Args:
        serve_event: Serve event to validate
        config: Configuration dictionary
    
    Returns:
        True if serve event is valid
    """
    # Check duration
    duration = serve_event.end_frame - serve_event.start_frame
    if not (config['serve_min_duration'] <= duration <= config['serve_max_duration']):
        return False
    
    # Check sequence order
    if not (serve_event.start_frame <= serve_event.ball_toss_frame <= 
            serve_event.contact_frame <= serve_event.follow_through_frame <= 
            serve_event.end_frame):
        return False
    
    # Check confidence
    if serve_event.confidence < config['confidence_threshold']:
        return False
    
    return True


def get_serve_stats(serve_events: List[ServeEvent]) -> dict:
    """
    Calculate statistics for serve events.
    
    Args:
        serve_events: List of serve events
    
    Returns:
        Dictionary with serve statistics
    """
    if not serve_events:
        return {}
    
    durations = [event.end_frame - event.start_frame for event in serve_events]
    confidences = [event.confidence for event in serve_events]
    
    return {
        'total_serves': len(serve_events),
        'avg_duration': np.mean(durations),
        'avg_confidence': np.mean(confidences),
        'min_confidence': min(confidences),
        'max_confidence': max(confidences)
    }


def extract_serve_segments(
    video_path: str, 
    serves: List[ServeEvent], 
    pose_data: Optional[List[PoseFrame]] = None,
    include_landmarks: bool = True
) -> List[Dict]:
    """
    Extract serve video segments with optional landmark visualization.
    
    Args:
        video_path: Path to the source video
        serves: List of detected serve events
        pose_data: Optional pose estimation data
        include_landmarks: Whether to overlay landmarks on videos
    
    Returns:
        List of serve segment information
    """
    from pathlib import Path
    from .video_utils import extract_serve_clip_direct
    
    segments = []
    
    for i, serve in enumerate(serves):
        # Create output directory for this task
        output_dir = Path("outputs") / f"serve_{i:03d}"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Extract serve clip
        serve_clip_path = output_dir / f"serve_{i:03d}.mp4"
        success = extract_serve_clip_direct(
            video_path, 
            serve, 
            str(serve_clip_path),
            buffer_seconds=1.0
        )
        
        if not success:
            print(f"Warning: Failed to extract serve {i}")
            continue
        
        # Add landmarks if requested and available
        final_clip_path = serve_clip_path
        has_landmarks = False
        
        if include_landmarks and pose_data and len(pose_data) > serve.end_frame:
            try:
                # Extract pose data for this serve
                serve_pose_data = pose_data[serve.start_frame:serve.end_frame + 1]
                
                # Add landmarks to video (placeholder for now)
                # TODO: Implement landmark overlay functionality
                has_landmarks = True
                print(f"Landmarks would be added to serve {i} (not yet implemented)")
            except Exception as e:
                print(f"Warning: Failed to add landmarks to serve {i}: {e}")
        
        segments.append({
            "serve_id": i,
            "start_frame": serve.start_frame,
            "end_frame": serve.end_frame,
            "duration": serve.end_frame - serve.start_frame,
            "confidence": serve.confidence,
            "video_path": str(final_clip_path),
            "has_landmarks": has_landmarks,
            "ball_toss_frame": serve.ball_toss_frame,
            "contact_frame": serve.contact_frame,
            "follow_through_frame": serve.follow_through_frame
        })
    
    return segments
