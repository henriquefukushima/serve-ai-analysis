"""Video processing module for tennis serve analysis."""

# Core detection modules
from .serve_detection import (
    detect_serves,
    ServeEvent,
    ServeState,
    ServePhase,
    validate_serve_event,
    get_serve_stats,
    DEFAULT_SERVE_CONFIG
)

from .ball_detection import (
    detect_ball_trajectory,
    filter_ball_detections,
    get_ball_trajectory_stats,
    BallDetection
)

from .video_utils import (
    load_video,
    save_video_segment,
    extract_serve_clip,
    extract_serve_clip_direct,
    get_video_info,
    assess_video_quality,
    optimize_video_for_processing,
    create_video_preview,
    extract_frame_at_time,
    get_video_thumbnail
)

__all__ = [
    # Serve detection
    "detect_serves",
    "ServeEvent",
    "ServeState", 
    "ServePhase",
    "validate_serve_event",
    "get_serve_stats",
    "DEFAULT_SERVE_CONFIG",
    
    # Ball detection
    "detect_ball_trajectory",
    "filter_ball_detections",
    "get_ball_trajectory_stats",
    "BallDetection",
    
    # Video utilities
    "load_video",
    "save_video_segment",
    "extract_serve_clip",
    "extract_serve_clip_direct",
    "get_video_info",
    "assess_video_quality",
    "optimize_video_for_processing",
    "create_video_preview",
    "extract_frame_at_time",
    "get_video_thumbnail"
]
