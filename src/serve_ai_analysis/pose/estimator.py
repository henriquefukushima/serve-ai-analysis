"""Base pose estimator class for tennis serve analysis."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List
from rich.console import Console

from .mediapipe_pose import PoseFrame

console = Console()

class PoseEstimator(ABC):
    """Abstract base class for pose estimators."""
    
    @abstractmethod
    def estimate_pose_video(self, video_path: Path) -> List[PoseFrame]:
        """Estimate poses from a video file."""
        pass
    
    @abstractmethod
    def save_pose_data(self, pose_frames: List[PoseFrame], output_path: Path):
        """Save pose data to file."""
        pass
