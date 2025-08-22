"""Video quality assessment and optimization module."""

import cv2
import numpy as np
from pathlib import Path
from typing import Dict, Tuple, Optional
from dataclasses import dataclass
from rich.console import Console
from rich.table import Table
import json

console = Console()

@dataclass
class VideoQualityMetrics:
    """Video quality metrics for assessment."""
    resolution: Tuple[int, int]
    fps: float
    duration: float
    total_frames: int
    file_size_mb: float
    brightness_mean: float
    contrast_score: float
    blur_score: float
    compression_ratio: float
    quality_score: float  # 0-100

class VideoQualityAssessor:
    """Assess and optimize video quality for processing."""
    
    def __init__(self):
        self.target_resolution = (1280, 720)  # 720p for efficiency
        self.target_fps = 30.0
        self.min_quality_score = 70.0
        
    def assess_video_quality(self, video_path: Path) -> VideoQualityMetrics:
        """
        Assess the quality of a video file.
        
        Args:
            video_path: Path to the video file
            
        Returns:
            VideoQualityMetrics object with quality information
        """
        console.print(f"[blue]Assessing video quality: {video_path.name}[/blue]")
        
        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            raise ValueError(f"Could not open video: {video_path}")
        
        # Basic video properties
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = total_frames / fps if fps > 0 else 0
        
        # File size
        file_size_mb = video_path.stat().st_size / (1024 * 1024)
        
        # Quality metrics
        brightness_mean = self._calculate_brightness(cap)
        contrast_score = self._calculate_contrast(cap)
        blur_score = self._calculate_blur(cap)
        compression_ratio = self._calculate_compression_ratio(width, height, fps, file_size_mb)
        
        # Overall quality score
        quality_score = self._calculate_quality_score(
            brightness_mean, contrast_score, blur_score, compression_ratio
        )
        
        cap.release()
        
        metrics = VideoQualityMetrics(
            resolution=(width, height),
            fps=fps,
            duration=duration,
            total_frames=total_frames,
            file_size_mb=file_size_mb,
            brightness_mean=brightness_mean,
            contrast_score=contrast_score,
            blur_score=blur_score,
            compression_ratio=compression_ratio,
            quality_score=quality_score
        )
        
        self._display_quality_report(metrics, video_path.name)
        return metrics
    
    def _calculate_brightness(self, cap: cv2.VideoCapture) -> float:
        """Calculate average brightness of the video."""
        brightness_values = []
        
        # Sample frames for brightness calculation
        sample_frames = min(100, int(cap.get(cv2.CAP_PROP_FRAME_COUNT)))
        step = max(1, int(cap.get(cv2.CAP_PROP_FRAME_COUNT) / sample_frames))
        
        for i in range(0, sample_frames, step):
            cap.set(cv2.CAP_PROP_POS_FRAMES, i)
            ret, frame = cap.read()
            if ret:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                brightness_values.append(np.mean(gray))
        
        return np.mean(brightness_values) if brightness_values else 0
    
    def _calculate_contrast(self, cap: cv2.VideoCapture) -> float:
        """Calculate contrast score of the video."""
        contrast_values = []
        
        # Sample frames for contrast calculation
        sample_frames = min(50, int(cap.get(cv2.CAP_PROP_FRAME_COUNT)))
        step = max(1, int(cap.get(cv2.CAP_PROP_FRAME_COUNT) / sample_frames))
        
        for i in range(0, sample_frames, step):
            cap.set(cv2.CAP_PROP_POS_FRAMES, i)
            ret, frame = cap.read()
            if ret:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                contrast = np.std(gray)  # Standard deviation as contrast measure
                contrast_values.append(contrast)
        
        return np.mean(contrast_values) if contrast_values else 0
    
    def _calculate_blur(self, cap: cv2.VideoCapture) -> float:
        """Calculate blur score using Laplacian variance."""
        blur_values = []
        
        # Sample frames for blur calculation
        sample_frames = min(30, int(cap.get(cv2.CAP_PROP_FRAME_COUNT)))
        step = max(1, int(cap.get(cv2.CAP_PROP_FRAME_COUNT) / sample_frames))
        
        for i in range(0, sample_frames, step):
            cap.set(cv2.CAP_PROP_POS_FRAMES, i)
            ret, frame = cap.read()
            if ret:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                blur = cv2.Laplacian(gray, cv2.CV_64F).var()
                blur_values.append(blur)
        
        return np.mean(blur_values) if blur_values else 0
    
    def _calculate_compression_ratio(self, width: int, height: int, fps: float, file_size_mb: float) -> float:
        """Calculate compression ratio (lower is better)."""
        # Theoretical uncompressed size (assuming 24-bit color)
        theoretical_size = (width * height * fps * 3) / (1024 * 1024)  # MB
        return file_size_mb / theoretical_size if theoretical_size > 0 else 1
    
    def _calculate_quality_score(self, brightness: float, contrast: float, blur: float, compression: float) -> float:
        """Calculate overall quality score (0-100)."""
        # Normalize metrics to 0-100 scale
        brightness_score = min(100, max(0, brightness / 2.55))  # 0-255 to 0-100
        contrast_score = min(100, max(0, contrast / 2.55))
        blur_score = min(100, max(0, blur / 100))  # Higher blur variance = less blur
        compression_score = max(0, 100 - (compression * 50))  # Lower compression = better
        
        # Weighted average
        quality_score = (
            brightness_score * 0.2 +
            contrast_score * 0.3 +
            blur_score * 0.3 +
            compression_score * 0.2
        )
        
        return round(quality_score, 1)
    
    def _display_quality_report(self, metrics: VideoQualityMetrics, filename: str):
        """Display a formatted quality report."""
        table = Table(title=f"Video Quality Report: {filename}")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        table.add_column("Status", style="yellow")
        
        # Resolution
        res_status = "✅ Good" if metrics.resolution[0] >= 1280 else "⚠️ Low"
        table.add_row("Resolution", f"{metrics.resolution[0]}x{metrics.resolution[1]}", res_status)
        
        # FPS
        fps_status = "✅ Good" if metrics.fps >= 25 else "⚠️ Low"
        table.add_row("Frame Rate", f"{metrics.fps:.1f} fps", fps_status)
        
        # Duration
        table.add_row("Duration", f"{metrics.duration:.1f}s", "📊 Info")
        
        # File Size
        table.add_row("File Size", f"{metrics.file_size_mb:.1f} MB", "📊 Info")
        
        # Quality Metrics
        brightness_status = "✅ Good" if 40 <= metrics.brightness_mean <= 200 else "⚠️ Poor"
        table.add_row("Brightness", f"{metrics.brightness_mean:.1f}", brightness_status)
        
        contrast_status = "✅ Good" if metrics.contrast_score > 30 else "⚠️ Low"
        table.add_row("Contrast", f"{metrics.contrast_score:.1f}", contrast_status)
        
        blur_status = "✅ Sharp" if metrics.blur_score > 100 else "⚠️ Blurry"
        table.add_row("Sharpness", f"{metrics.blur_score:.1f}", blur_status)
        
        # Overall Quality
        quality_status = "✅ Excellent" if metrics.quality_score >= 80 else "✅ Good" if metrics.quality_score >= 60 else "⚠️ Poor"
        table.add_row("Overall Quality", f"{metrics.quality_score}/100", quality_status)
        
        console.print(table)
    
    def optimize_video(self, input_path: Path, output_path: Path, target_resolution: Optional[Tuple[int, int]] = None) -> Path:
        """
        Optimize video for processing efficiency.
        
        Args:
            input_path: Path to input video
            output_path: Path for optimized video
            target_resolution: Target resolution (width, height)
            
        Returns:
            Path to optimized video
        """
        if target_resolution is None:
            target_resolution = self.target_resolution
        
        console.print(f"[blue]Optimizing video: {input_path.name}[/blue]")
        
        cap = cv2.VideoCapture(str(input_path))
        if not cap.isOpened():
            raise ValueError(f"Could not open video: {input_path}")
        
        # Get original properties
        orig_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        orig_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        orig_fps = cap.get(cv2.CAP_PROP_FPS)
        
        # Determine if optimization is needed
        needs_resize = (orig_width > target_resolution[0] or orig_height > target_resolution[1])
        needs_fps_reduction = orig_fps > self.target_fps
        
        if not needs_resize and not needs_fps_reduction:
            console.print("✅ Video already optimized, copying original")
            cap.release()
            import shutil
            shutil.copy2(input_path, output_path)
            return output_path
        
        # Create video writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(str(output_path), fourcc, self.target_fps, target_resolution)
        
        frame_count = 0
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            # Resize if needed
            if needs_resize:
                frame = cv2.resize(frame, target_resolution, interpolation=cv2.INTER_AREA)
            
            # Write frame (fps reduction happens automatically)
            out.write(frame)
            frame_count += 1
            
            if frame_count % 100 == 0:
                progress = (frame_count / total_frames) * 100
                console.print(f"Progress: {progress:.1f}% ({frame_count}/{total_frames})")
        
        cap.release()
        out.release()
        
        # Calculate optimization results
        original_size = input_path.stat().st_size / (1024 * 1024)
        optimized_size = output_path.stat().st_size / (1024 * 1024)
        reduction = ((original_size - optimized_size) / original_size) * 100
        
        console.print(f"✅ Optimization complete:")
        console.print(f"   Original: {original_size:.1f} MB")
        console.print(f"   Optimized: {optimized_size:.1f} MB")
        console.print(f"   Reduction: {reduction:.1f}%")
        
        return output_path
    
    def save_quality_report(self, metrics: VideoQualityMetrics, output_path: Path):
        """Save quality metrics to JSON file."""
        data = {
            "resolution": metrics.resolution,
            "fps": metrics.fps,
            "duration": metrics.duration,
            "total_frames": metrics.total_frames,
            "file_size_mb": metrics.file_size_mb,
            "brightness_mean": metrics.brightness_mean,
            "contrast_score": metrics.contrast_score,
            "blur_score": metrics.blur_score,
            "compression_ratio": metrics.compression_ratio,
            "quality_score": metrics.quality_score
        }
        
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        console.print(f"📊 Quality report saved to {output_path}")

