"""Video utilities module for tennis serve analysis."""

import cv2
import numpy as np
from pathlib import Path
from typing import Tuple, List, Dict, Optional
from .serve_detection import ServeEvent


def load_video(video_path: str) -> Tuple[List[np.ndarray], float]:
    """
    Load video and return frames with FPS.
    
    Args:
        video_path: Path to input video
    
    Returns:
        Tuple of (frames, fps)
    """
    video_path = Path(video_path)
    if not video_path.exists():
        raise FileNotFoundError(f"Video file not found: {video_path}")
    
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise ValueError(f"Could not open video: {video_path}")
    
    fps = cap.get(cv2.CAP_PROP_FPS)
    frames = []
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            frames.append(frame)
    finally:
        cap.release()
    
    return frames, fps


def save_video_segment(
    frames: List[np.ndarray],
    output_path: str,
    fps: float = 30.0
) -> bool:
    """
    Save video segment to file.
    
    Args:
        frames: List of video frames
        output_path: Output video path
        fps: Frames per second
    
    Returns:
        True if successful
    """
    if not frames:
        return False
    
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    height, width = frames[0].shape[:2]
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    
    out = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))
    
    try:
        for frame in frames:
            out.write(frame)
        return True
    finally:
        out.release()


def extract_serve_clip(
    video_path: str,
    serve_event: ServeEvent,
    buffer_seconds: float = 1.0
) -> List[np.ndarray]:
    """
    Extract serve clip with buffer before and after.
    
    Args:
        video_path: Path to input video
        serve_event: Serve event to extract
        buffer_seconds: Buffer time in seconds before and after serve
    
    Returns:
        List of frames for the serve clip
    """
    # Get video info to determine FPS
    info = get_video_info(video_path)
    fps = info['fps']
    
    # Calculate buffer frames
    buffer_frames = int(buffer_seconds * fps)
    
    # Calculate start and end frame indices
    start_frame = max(0, serve_event.start_frame - buffer_frames)
    end_frame = serve_event.end_frame + buffer_frames
    
    # Extract frames directly from video without loading everything
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"Could not open video: {video_path}")
    
    frames = []
    try:
        # Seek to start frame
        cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
        
        # Read frames until end frame
        frame_idx = start_frame
        while frame_idx <= end_frame:
            ret, frame = cap.read()
            if not ret:
                break
            frames.append(frame)
            frame_idx += 1
            
    finally:
        cap.release()
    
    return frames


def extract_serve_clip_direct(
    video_path: str,
    serve_event: ServeEvent,
    output_path: str,
    buffer_seconds: float = 1.0
) -> bool:
    """
    Extract serve clip directly to file without loading frames into memory.
    
    Args:
        video_path: Path to input video
        serve_event: Serve event to extract
        output_path: Path to output video file
        buffer_seconds: Buffer time in seconds before and after serve
    
    Returns:
        True if successful
    """
    # Get video info to determine FPS
    info = get_video_info(video_path)
    fps = info['fps']
    
    # Calculate buffer frames
    buffer_frames = int(buffer_seconds * fps)
    
    # Calculate start and end frame indices
    start_frame = max(0, serve_event.start_frame - buffer_frames)
    end_frame = serve_event.end_frame + buffer_frames
    
    # Extract frames directly from video without loading everything
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"Could not open video: {video_path}")
    
    # Get video properties
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    # Create output directory
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Setup video writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))
    
    try:
        # Seek to start frame
        cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
        
        # Read frames until end frame
        frame_idx = start_frame
        while frame_idx <= end_frame:
            ret, frame = cap.read()
            if not ret:
                break
            out.write(frame)
            frame_idx += 1
            
    finally:
        cap.release()
        out.release()
    
    return True


def get_video_info(video_path: str) -> Dict[str, any]:
    """
    Get video information.
    
    Args:
        video_path: Path to video file
    
    Returns:
        Dictionary with video information
    """
    video_path = Path(video_path)
    if not video_path.exists():
        raise FileNotFoundError(f"Video file not found: {video_path}")
    
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise ValueError(f"Could not open video: {video_path}")
    
    try:
        info = {
            'path': str(video_path),
            'filename': video_path.name,
            'size_bytes': video_path.stat().st_size,
            'width': int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            'height': int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            'fps': cap.get(cv2.CAP_PROP_FPS),
            'frame_count': int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
            'duration_seconds': cap.get(cv2.CAP_PROP_FRAME_COUNT) / cap.get(cv2.CAP_PROP_FPS),
            'codec': int(cap.get(cv2.CAP_PROP_FOURCC))
        }
        
        # Convert codec to string
        codec_bytes = info['codec'].to_bytes(4, byteorder='little')
        info['codec_str'] = codec_bytes.decode('ascii', errors='ignore')
        
        return info
    finally:
        cap.release()


def assess_video_quality(video_path: str) -> Dict[str, float]:
    """
    Assess video quality for serve detection.
    
    Args:
        video_path: Path to video file
    
    Returns:
        Dictionary with quality metrics
    """
    info = get_video_info(video_path)
    
    # Calculate quality metrics
    resolution_score = min(1.0, (info['width'] * info['height']) / (1920 * 1080))
    fps_score = min(1.0, info['fps'] / 30.0)
    duration_score = min(1.0, info['duration_seconds'] / 60.0)  # Prefer videos under 1 minute
    
    # Overall quality score
    quality_score = (resolution_score + fps_score + duration_score) / 3
    
    return {
        'overall_quality': quality_score,
        'resolution_score': resolution_score,
        'fps_score': fps_score,
        'duration_score': duration_score,
        'width': info['width'],
        'height': info['height'],
        'fps': info['fps'],
        'duration_seconds': info['duration_seconds']
    }


def optimize_video_for_processing(
    video_path: str,
    target_resolution: Tuple[int, int] = (1280, 720),
    target_fps: float = 30.0
) -> str:
    """
    Optimize video for processing.
    
    Args:
        video_path: Path to input video
        target_resolution: Target resolution (width, height)
        target_fps: Target frames per second
    
    Returns:
        Path to optimized video
    """
    input_path = Path(video_path)
    output_path = input_path.parent / f"{input_path.stem}_optimized{input_path.suffix}"
    
    cap = cv2.VideoCapture(str(input_path))
    if not cap.isOpened():
        raise ValueError(f"Could not open video: {input_path}")
    
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(str(output_path), fourcc, target_fps, target_resolution)
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Resize frame
            resized_frame = cv2.resize(frame, target_resolution)
            out.write(resized_frame)
    finally:
        cap.release()
        out.release()
    
    return str(output_path)


def create_video_preview(
    video_path: str,
    output_path: str,
    max_frames: int = 100,
    frame_interval: int = 10
) -> bool:
    """
    Create a preview video with reduced frames.
    
    Args:
        video_path: Path to input video
        output_path: Path to output preview video
        max_frames: Maximum number of frames in preview
        frame_interval: Interval between frames to include
    
    Returns:
        True if successful
    """
    frames, fps = load_video(video_path)
    
    if not frames:
        return False
    
    # Select frames at intervals
    selected_frames = frames[::frame_interval][:max_frames]
    
    if not selected_frames:
        return False
    
    # Save preview
    return save_video_segment(selected_frames, output_path, fps / frame_interval)


def extract_frame_at_time(
    video_path: str,
    timestamp_seconds: float
) -> Optional[np.ndarray]:
    """
    Extract a single frame at a specific timestamp.
    
    Args:
        video_path: Path to video file
        timestamp_seconds: Timestamp in seconds
    
    Returns:
        Frame at timestamp, or None if not found
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return None
    
    try:
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_number = int(timestamp_seconds * fps)
        
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        ret, frame = cap.read()
        
        return frame if ret else None
    finally:
        cap.release()


def get_video_thumbnail(
    video_path: str,
    output_path: str,
    timestamp_seconds: float = 5.0
) -> bool:
    """
    Create a thumbnail from video.
    
    Args:
        video_path: Path to video file
        output_path: Path to output thumbnail
        timestamp_seconds: Timestamp to extract frame from
    
    Returns:
        True if successful
    """
    frame = extract_frame_at_time(video_path, timestamp_seconds)
    if frame is None:
        return False
    
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    return cv2.imwrite(str(output_path), frame)
