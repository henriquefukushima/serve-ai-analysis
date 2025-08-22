"""Ball detection module for tennis serve analysis."""

import cv2
import numpy as np
from dataclasses import dataclass
from typing import List, Tuple, Optional
from pathlib import Path


@dataclass
class BallDetection:
    """Represents a detected ball in a frame."""
    frame_idx: int
    x: float
    y: float
    confidence: float
    radius: float


def detect_ball_trajectory(
    video_path: str,
    min_radius: int = 5,
    max_radius: int = 50,
    color_lower: Tuple[int, int, int] = (0, 100, 100),  # HSV for tennis ball
    color_upper: Tuple[int, int, int] = (20, 255, 255),
    frame_skip: int = 1
) -> List[BallDetection]:
    """
    Detect tennis ball trajectory using color-based detection.
    
    Args:
        video_path: Path to input video
        min_radius: Minimum ball radius to detect
        max_radius: Maximum ball radius to detect
        color_lower: Lower HSV threshold for ball color
        color_upper: Upper HSV threshold for ball color
    
    Returns:
        List of ball detections with frame indices and positions
    """
    video_path = Path(video_path)
    if not video_path.exists():
        raise FileNotFoundError(f"Video file not found: {video_path}")
    
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise ValueError(f"Could not open video: {video_path}")
    
    detections = []
    frame_idx = 0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Skip frames if frame_skip > 1
            if frame_idx % frame_skip != 0:
                frame_idx += 1
                continue
            
            # Convert to HSV color space
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            
            # Create mask for ball color
            mask = cv2.inRange(hsv, color_lower, color_upper)
            
            # Apply morphological operations to reduce noise
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
            
            # Find contours
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Filter contours by circularity and size
            for contour in contours:
                area = cv2.contourArea(contour)
                if area < np.pi * min_radius**2 or area > np.pi * max_radius**2:
                    continue
                
                # Calculate circularity
                perimeter = cv2.arcLength(contour, True)
                if perimeter == 0:
                    continue
                
                circularity = 4 * np.pi * area / (perimeter * perimeter)
                if circularity < 0.7:  # Minimum circularity threshold
                    continue
                
                # Get bounding circle
                (x, y), radius = cv2.minEnclosingCircle(contour)
                
                if min_radius <= radius <= max_radius:
                    # Calculate confidence based on circularity and area
                    confidence = min(circularity * (area / (np.pi * max_radius**2)), 1.0)
                    
                    detection = BallDetection(
                        frame_idx=frame_idx,
                        x=float(x),
                        y=float(y),
                        confidence=confidence,
                        radius=float(radius)
                    )
                    detections.append(detection)
            
            frame_idx += 1
            
    finally:
        cap.release()
    
    return detections


def filter_ball_detections(
    detections: List[BallDetection],
    min_confidence: float = 0.3,
    max_jump_distance: float = 100.0
) -> List[BallDetection]:
    """
    Filter ball detections to remove noise and improve trajectory.
    
    Args:
        detections: List of ball detections
        min_confidence: Minimum confidence threshold
        max_jump_distance: Maximum allowed distance between consecutive detections
    
    Returns:
        Filtered list of ball detections
    """
    if not detections:
        return []
    
    # Filter by confidence
    filtered = [d for d in detections if d.confidence >= min_confidence]
    
    if len(filtered) < 2:
        return filtered
    
    # Filter by jump distance
    result = [filtered[0]]
    
    for i in range(1, len(filtered)):
        prev = result[-1]
        curr = filtered[i]
        
        # Calculate distance between consecutive detections
        distance = np.sqrt((curr.x - prev.x)**2 + (curr.y - prev.y)**2)
        
        if distance <= max_jump_distance:
            result.append(curr)
    
    return result


def get_ball_trajectory_stats(detections: List[BallDetection]) -> dict:
    """
    Calculate statistics for ball trajectory.
    
    Args:
        detections: List of ball detections
    
    Returns:
        Dictionary with trajectory statistics
    """
    if not detections:
        return {}
    
    x_coords = [d.x for d in detections]
    y_coords = [d.y for d in detections]
    confidences = [d.confidence for d in detections]
    
    return {
        'total_detections': len(detections),
        'avg_confidence': np.mean(confidences),
        'x_range': (min(x_coords), max(x_coords)),
        'y_range': (min(y_coords), max(y_coords)),
        'trajectory_length': len(detections),
        'frame_span': detections[-1].frame_idx - detections[0].frame_idx + 1
    }
