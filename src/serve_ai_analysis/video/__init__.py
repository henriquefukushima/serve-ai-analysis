"""Video processing module for tennis serve analysis (Functional Programming)."""

# Functional programming modules
from ..pose.pose_functions import (
    estimate_pose_video,
    save_pose_data,
    load_pose_data,
    filter_pose_frames_by_visibility,
    get_landmark_position,
    PoseFrame,
    PoseLandmark
)

from .serve_functions import (
    detect_serves,
    save_serve_events,
    load_serve_events,
    extract_serve_video,
    extract_serve_videos_with_pose,
    remove_overlapping_serves,
    validate_serve_segment,
    is_serve_contact_moment,
    ServeEvent,
    DEFAULT_CONFIG
)

from .quality_functions import (
    assess_video_quality,
    display_quality_report,
    save_quality_report,
    load_quality_report,
    optimize_video,
    is_video_already_optimized,
    get_video_info,
    VideoQualityMetrics
)

from .pipeline_functions import (
    process_single_video,
    process_videos,
    create_output_structure,
    display_processing_summary,
    display_batch_summary,
    generate_processing_report,
    load_processing_report,
    ProcessingResult,
    DEFAULT_PIPELINE_CONFIG
)

__all__ = [
    # Pose functions
    "estimate_pose_video",
    "save_pose_data",
    "load_pose_data",
    "filter_pose_frames_by_visibility",
    "get_landmark_position",
    "PoseFrame",
    "PoseLandmark",
    
    # Serve functions
    "detect_serves",
    "save_serve_events",
    "load_serve_events",
    "extract_serve_video",
    "extract_serve_videos_with_pose",
    "remove_overlapping_serves",
    "validate_serve_segment",
    "is_serve_contact_moment",
    "ServeEvent",
    "DEFAULT_CONFIG",
    
    # Quality functions
    "assess_video_quality",
    "display_quality_report",
    "save_quality_report",
    "load_quality_report",
    "optimize_video",
    "is_video_already_optimized",
    "get_video_info",
    "VideoQualityMetrics",
    
    # Pipeline functions
    "process_single_video",
    "process_videos",
    "create_output_structure",
    "display_processing_summary",
    "display_batch_summary",
    "generate_processing_report",
    "load_processing_report",
    "ProcessingResult",
    "DEFAULT_PIPELINE_CONFIG"
]
