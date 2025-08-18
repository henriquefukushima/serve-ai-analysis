"""Serve segmentation module for tennis video analysis."""

import cv2
import numpy as np
from pathlib import Path
from typing import List, Tuple, Dict, Any
from dataclasses import dataclass
import json
from rich.console import Console

console = Console()

@dataclass
class ServeSegment:
    """Represents a single serve segment from a video."""
    start_frame: int
    end_frame: int
    start_time: float
    end_time: float
    duration: float
    confidence: float
    bbox: Tuple[int, int, int, int]  # x, y, width, height

class ServeSegmenter:
    """Segments individual serves from tennis videos."""
    
    def __init__(
        self,
        min_duration: float = 1.0,
        max_duration: float = 5.0,
        confidence_threshold: float = 0.5
    ):
        self.min_duration = min_duration
        self.max_duration = max_duration
        self.confidence_threshold = confidence_threshold
        
    def segment_video(self, video_path: Path) -> List[ServeSegment]:
        """
        Segment serves from a tennis video.
        
        Args:
            video_path: Path to the input video file
            
        Returns:
            List of ServeSegment objects
        """
        console.print(f"[blue]Segmenting serves from {video_path}[/blue]")
        
        # Open video
        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            raise ValueError(f"Could not open video file: {video_path}")
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        console.print(f"Video info: {total_frames} frames, {fps:.2f} fps")
        
        # TODO: Implement actual serve detection logic
        # For now, return dummy segments
        segments = self._create_dummy_segments(fps, total_frames)
        
        cap.release()
        return segments
    
    def _create_dummy_segments(self, fps: float, total_frames: int) -> List[ServeSegment]:
        """Create dummy serve segments for testing."""
        segments = []
        
        # Create 3 dummy serves
        for i in range(3):
            start_frame = int(i * total_frames / 4)
            end_frame = int((i + 1) * total_frames / 4)
            start_time = start_frame / fps
            end_time = end_frame / fps
            duration = end_time - start_time
            
            if self.min_duration <= duration <= self.max_duration:
                segment = ServeSegment(
                    start_frame=start_frame,
                    end_frame=end_frame,
                    start_time=start_time,
                    end_time=end_time,
                    duration=duration,
                    confidence=0.8,
                    bbox=(100, 100, 400, 600)
                )
                segments.append(segment)
        
        console.print(f"Found {len(segments)} serve segments")
        return segments
    
    def save_segments(self, segments: List[ServeSegment], output_path: Path):
        """Save serve segments metadata to JSON file."""
        data = []
        for segment in segments:
            data.append({
                "start_frame": segment.start_frame,
                "end_frame": segment.end_frame,
                "start_time": segment.start_time,
                "end_time": segment.end_time,
                "duration": segment.duration,
                "confidence": segment.confidence,
                "bbox": segment.bbox
            })
        
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        console.print(f"Saved {len(segments)} segments to {output_path}")
    
    def extract_segment_video(
        self, 
        video_path: Path, 
        segment: ServeSegment, 
        output_path: Path
    ) -> bool:
        """
        Extract a single serve segment as a separate video file.
        
        Args:
            video_path: Path to the input video
            segment: ServeSegment to extract
            output_path: Path for the output video
            
        Returns:
            True if successful, False otherwise
        """
        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            return False
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        # Create video writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))
        
        # Extract frames
        cap.set(cv2.CAP_PROP_POS_FRAMES, segment.start_frame)
        
        for frame_idx in range(segment.start_frame, segment.end_frame + 1):
            ret, frame = cap.read()
            if not ret:
                break
            out.write(frame)
        
        cap.release()
        out.release()
        
        console.print(f"Extracted segment to {output_path}")
        return True
