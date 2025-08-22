#!/usr/bin/env python3
"""
Debug script to analyze pose data and understand serve detection issues.
"""

import sys
from pathlib import Path
import json
import numpy as np
import matplotlib.pyplot as plt

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from serve_ai_analysis.video import VideoProcessingPipeline
from serve_ai_analysis.pose import MediaPipePoseEstimator
from rich.console import Console
from rich.panel import Panel

console = Console()

def analyze_pose_data(video_path: Path):
    """Analyze pose data to understand serve detection issues."""
    console.print(Panel.fit(
        f"[bold blue]Analyzing Pose Data: {video_path.name}[/bold blue]",
        title="Debug Analysis"
    ))
    
    # Initialize pose estimator
    pose_estimator = MediaPipePoseEstimator(confidence_threshold=0.5)
    
    # Extract pose data
    pose_frames = pose_estimator.estimate_pose_video(video_path)
    
    if not pose_frames:
        console.print("[red]No pose data detected![/red]")
        return
    
    console.print(f"📊 Extracted {len(pose_frames)} frames with pose data")
    
    # Analyze wrist positions over time
    wrist_positions = []
    timestamps = []
    
    for frame in pose_frames:
        if "right_wrist" in frame.landmarks:
            wrist = frame.landmarks["right_wrist"]
            wrist_positions.append((wrist.x, wrist.y))
            timestamps.append(frame.timestamp)
    
    if not wrist_positions:
        console.print("[red]No wrist positions found![/red]")
        return
    
    console.print(f"📈 Found {len(wrist_positions)} wrist positions")
    
    # Convert to numpy arrays
    wrist_x = np.array([pos[0] for pos in wrist_positions])
    wrist_y = np.array([pos[1] for pos in wrist_positions])
    timestamps = np.array(timestamps)
    
    # Calculate motion scores
    motion_scores = []
    for i in range(len(wrist_positions)):
        if i < 15:  # Skip first 15 frames
            motion_scores.append(0.0)
            continue
        
        # Calculate motion based on wrist position changes
        motion_score = 0.0
        for j in range(max(0, i - 15), i):
            if j < len(wrist_positions):
                dx = wrist_x[i] - wrist_x[j]
                dy = wrist_y[i] - wrist_y[j]
                distance = np.sqrt(dx**2 + dy**2)
                motion_score += distance
        
        motion_scores.append(motion_score)
    
    motion_scores = np.array(motion_scores)
    
    # Find peaks in motion
    from scipy.signal import find_peaks
    peaks, _ = find_peaks(motion_scores, height=np.percentile(motion_scores, 70))
    
    console.print(f"🔍 Found {len(peaks)} motion peaks")
    
    # Analyze each peak
    for i, peak_idx in enumerate(peaks[:5]):  # Show first 5 peaks
        if peak_idx < len(timestamps):
            console.print(f"Peak {i+1}: Time={timestamps[peak_idx]:.1f}s, Motion={motion_scores[peak_idx]:.4f}")
            console.print(f"  Wrist position: ({wrist_x[peak_idx]:.3f}, {wrist_y[peak_idx]:.3f})")
    
    # Save analysis data
    analysis_data = {
        "video_name": video_path.name,
        "total_frames": len(pose_frames),
        "frames_with_pose": len(wrist_positions),
        "motion_peaks": len(peaks),
        "wrist_positions": wrist_positions,
        "motion_scores": motion_scores.tolist(),
        "timestamps": timestamps.tolist(),
        "peak_indices": peaks.tolist()
    }
    
    output_path = Path("debug_analysis") / f"{video_path.stem}_pose_analysis.json"
    output_path.parent.mkdir(exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(analysis_data, f, indent=2)
    
    console.print(f"📊 Analysis saved to {output_path}")
    
    # Create visualization
    create_motion_plot(timestamps, motion_scores, peaks, wrist_y, video_path.stem)

def create_motion_plot(timestamps, motion_scores, peaks, wrist_y, video_name):
    """Create a plot showing motion over time."""
    try:
        plt.figure(figsize=(15, 10))
        
        # Plot motion scores
        plt.subplot(2, 1, 1)
        plt.plot(timestamps, motion_scores, 'b-', label='Motion Score')
        plt.plot(timestamps[peaks], motion_scores[peaks], 'ro', label='Peaks')
        plt.xlabel('Time (s)')
        plt.ylabel('Motion Score')
        plt.title(f'Motion Analysis - {video_name}')
        plt.legend()
        plt.grid(True)
        
        # Plot wrist height
        plt.subplot(2, 1, 2)
        plt.plot(timestamps, wrist_y, 'g-', label='Wrist Height (Y)')
        plt.plot(timestamps[peaks], wrist_y[peaks], 'ro', label='Peaks')
        plt.xlabel('Time (s)')
        plt.ylabel('Wrist Y Position')
        plt.title('Wrist Height Over Time')
        plt.legend()
        plt.grid(True)
        
        plt.tight_layout()
        
        output_path = Path("debug_analysis") / f"{video_name}_motion_plot.png"
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        console.print(f"📈 Motion plot saved to {output_path}")
        
    except ImportError:
        console.print("[yellow]Matplotlib not available, skipping plot generation[/yellow]")

def main():
    """Main debug function."""
    console.print(Panel.fit(
        "[bold blue]Tennis Serve Detection Debug[/bold blue]\n"
        "Analyzing pose data to understand serve detection issues",
        title="Debug Tool"
    ))
    
    # Define paths
    data_dir = Path("data/test")
    processed_dir = Path("processed_serves")
    
    if not data_dir.exists():
        console.print(f"[red]Error: Data directory {data_dir} not found[/red]")
        return
    
    # Find optimized videos
    optimized_videos = list(processed_dir.glob("optimized/*_optimized.mp4"))
    
    if not optimized_videos:
        console.print(f"[red]No optimized videos found in {processed_dir}/optimized/[/red]")
        console.print("Please run the video processing pipeline first")
        return
    
    console.print(f"Found {len(optimized_videos)} optimized videos:")
    for video in optimized_videos:
        console.print(f"  - {video.name}")
    
    # Analyze each video
    for video_path in optimized_videos:
        console.print(f"\n{'='*60}")
        analyze_pose_data(video_path)
    
    console.print(f"\n{'='*60}")
    console.print("[bold green]Debug analysis complete![/bold green]")
    console.print("Check the debug_analysis/ directory for detailed results")

if __name__ == "__main__":
    main()

