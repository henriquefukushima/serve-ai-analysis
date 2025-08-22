"""Functional video quality assessment module for tennis serve analysis."""

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

def calculate_brightness(frame: np.ndarray) -> float:
    """Calculate the mean brightness of a frame."""
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    return np.mean(gray)

def calculate_contrast(frame: np.ndarray) -> float:
    """Calculate the contrast score of a frame."""
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    return np.std(gray)

def calculate_blur_score(frame: np.ndarray) -> float:
    """Calculate the blur score using Laplacian variance."""
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
    return laplacian_var

def assess_video_quality(video_path: Path, target_resolution: Tuple[int, int] = (1280, 720)) -> VideoQualityMetrics:
    """Assess video quality and return comprehensive metrics."""
    console.print(f"Assessing video quality: {video_path.name}")
    
    # Open video
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise ValueError(f"Could not open video: {video_path}")
    
    # Get basic video properties
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / fps if fps > 0 else 0
    
    # Get resolution
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    resolution = (width, height)
    
    # Calculate file size
    file_size_mb = video_path.stat().st_size / (1024 * 1024)
    
    # Sample frames for quality analysis
    sample_frames = min(100, total_frames)  # Sample up to 100 frames
    step = max(1, total_frames // sample_frames)
    
    brightness_values = []
    contrast_values = []
    blur_values = []
    
    for i in range(0, total_frames, step):
        cap.set(cv2.CAP_PROP_POS_FRAMES, i)
        ret, frame = cap.read()
        if ret:
            brightness_values.append(calculate_brightness(frame))
            contrast_values.append(calculate_contrast(frame))
            blur_values.append(calculate_blur_score(frame))
    
    cap.release()
    
    # Calculate average metrics
    brightness_mean = np.mean(brightness_values) if brightness_values else 0
    contrast_score = np.mean(contrast_values) if contrast_values else 0
    blur_score = np.mean(blur_values) if blur_values else 0
    
    # Calculate compression ratio (simplified)
    target_pixels = target_resolution[0] * target_resolution[1]
    actual_pixels = resolution[0] * resolution[1]
    compression_ratio = actual_pixels / target_pixels if target_pixels > 0 else 1
    
    # Calculate overall quality score (0-100)
    quality_score = calculate_overall_quality_score(
        resolution, fps, duration, brightness_mean, contrast_score, blur_score, compression_ratio
    )
    
    return VideoQualityMetrics(
        resolution=resolution,
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

def calculate_overall_quality_score(
    resolution: Tuple[int, int],
    fps: float,
    duration: float,
    brightness_mean: float,
    contrast_score: float,
    blur_score: float,
    compression_ratio: float
) -> float:
    """Calculate overall quality score from individual metrics."""
    score = 0.0
    
    # Resolution score (0-25 points)
    min_resolution = 640 * 480
    max_resolution = 3840 * 2160
    actual_resolution = resolution[0] * resolution[1]
    resolution_score = min(25, (actual_resolution - min_resolution) / (max_resolution - min_resolution) * 25)
    score += resolution_score
    
    # Frame rate score (0-20 points)
    if fps >= 60:
        fps_score = 20
    elif fps >= 30:
        fps_score = 15
    elif fps >= 24:
        fps_score = 10
    else:
        fps_score = 5
    score += fps_score
    
    # Brightness score (0-20 points)
    if 100 <= brightness_mean <= 200:
        brightness_score = 20
    elif 80 <= brightness_mean <= 220:
        brightness_score = 15
    elif 60 <= brightness_mean <= 240:
        brightness_score = 10
    else:
        brightness_score = 5
    score += brightness_score
    
    # Contrast score (0-15 points)
    if contrast_score >= 50:
        contrast_points = 15
    elif contrast_score >= 30:
        contrast_points = 10
    elif contrast_score >= 20:
        contrast_points = 5
    else:
        contrast_points = 0
    score += contrast_points
    
    # Sharpness score (0-20 points)
    if blur_score >= 100:
        sharpness_score = 20
    elif blur_score >= 50:
        sharpness_score = 15
    elif blur_score >= 25:
        sharpness_score = 10
    else:
        sharpness_score = 5
    score += sharpness_score
    
    return min(100, max(0, score))

def display_quality_report(metrics: VideoQualityMetrics, video_name: str):
    """Display a formatted quality report."""
    table = Table(title=f"Video Quality Report: {video_name}")
    
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="magenta")
    table.add_column("Status", style="green")
    
    # Resolution
    status = "✅ Good" if metrics.resolution[0] >= 1280 and metrics.resolution[1] >= 720 else "⚠️ Low"
    table.add_row("Resolution", f"{metrics.resolution[0]}x{metrics.resolution[1]}", status)
    
    # Frame rate
    status = "✅ Good" if metrics.fps >= 30 else "⚠️ Low"
    table.add_row("Frame Rate", f"{metrics.fps:.1f} fps", status)
    
    # Duration
    table.add_row("Duration", f"{metrics.duration:.1f}s", "📊 Info")
    
    # File size
    table.add_row("File Size", f"{metrics.file_size_mb:.1f} MB", "📊 Info")
    
    # Brightness
    status = "✅ Good" if 100 <= metrics.brightness_mean <= 200 else "⚠️ Poor"
    table.add_row("Brightness", f"{metrics.brightness_mean:.1f}", status)
    
    # Contrast
    status = "✅ Good" if metrics.contrast_score >= 30 else "⚠️ Poor"
    table.add_row("Contrast", f"{metrics.contrast_score:.1f}", status)
    
    # Sharpness
    status = "✅ Sharp" if metrics.blur_score >= 50 else "⚠️ Blurry"
    table.add_row("Sharpness", f"{metrics.blur_score:.1f}", status)
    
    # Overall quality
    if metrics.quality_score >= 70:
        status = "✅ Excellent"
    elif metrics.quality_score >= 50:
        status = "⚠️ Good"
    elif metrics.quality_score >= 30:
        status = "⚠️ Poor"
    else:
        status = "❌ Very Poor"
    table.add_row("Overall Quality", f"{metrics.quality_score:.1f}/100", status)
    
    console.print(table)

def save_quality_report(metrics: VideoQualityMetrics, output_path: Path):
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

def load_quality_report(input_path: Path) -> VideoQualityMetrics:
    """Load quality metrics from JSON file."""
    with open(input_path, 'r') as f:
        data = json.load(f)
    
    return VideoQualityMetrics(
        resolution=tuple(data["resolution"]),
        fps=data["fps"],
        duration=data["duration"],
        total_frames=data["total_frames"],
        file_size_mb=data["file_size_mb"],
        brightness_mean=data["brightness_mean"],
        contrast_score=data["contrast_score"],
        blur_score=data["blur_score"],
        compression_ratio=data["compression_ratio"],
        quality_score=data["quality_score"]
    )

def optimize_video(video_path: Path, output_path: Path, target_resolution: Tuple[int, int] = (1280, 720)) -> bool:
    """Optimize video for processing by resizing and compressing."""
    console.print(f"Optimizing video: {video_path.name}")
    
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        return False
    
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    # Create video writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(str(output_path), fourcc, fps, target_resolution)
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Resize frame to target resolution
        resized_frame = cv2.resize(frame, target_resolution)
        out.write(resized_frame)
    
    cap.release()
    out.release()
    
    console.print(f"✅ Video optimized: {output_path}")
    return True

def is_video_already_optimized(video_path: Path, target_resolution: Tuple[int, int] = (1280, 720)) -> bool:
    """Check if video is already optimized to target resolution."""
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        return False
    
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap.release()
    
    return width == target_resolution[0] and height == target_resolution[1]

def get_video_info(video_path: Path) -> Dict[str, any]:
    """Get basic video information."""
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        return {}
    
    info = {
        "width": int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
        "height": int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
        "fps": cap.get(cv2.CAP_PROP_FPS),
        "total_frames": int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
        "duration": int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) / cap.get(cv2.CAP_PROP_FPS) if cap.get(cv2.CAP_PROP_FPS) > 0 else 0
    }
    
    cap.release()
    return info
