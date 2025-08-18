#!/usr/bin/env python3
"""
Demo script for Tennis Serve AI Analysis.

This script demonstrates how to use the analysis pipeline programmatically.
"""

import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from serve_ai_analysis.video.segmentation import ServeSegmenter
from serve_ai_analysis.pose.mediapipe_pose import MediaPipePoseEstimator
from serve_ai_analysis.metrics.calculator import BiomechanicalCalculator
from rich.console import Console

console = Console()

def main():
    """Run the demo analysis pipeline."""
    console.print("[bold blue]Tennis Serve AI Analysis Demo[/bold blue]")
    console.print("=" * 50)
    
    # Example video path (you would replace this with your actual video)
    video_path = Path("examples/sample_serve.mp4")
    
    # Check if video exists
    if not video_path.exists():
        console.print(f"[yellow]Warning: Sample video not found at {video_path}[/yellow]")
        console.print("This is a demo script. In a real scenario, you would:")
        console.print("1. Provide a tennis serve video")
        console.print("2. Run the analysis pipeline")
        console.print("3. Get biomechanical insights")
        return
    
    # Initialize components
    segmenter = ServeSegmenter(
        min_duration=1.5,
        max_duration=4.0,
        confidence_threshold=0.7
    )
    
    pose_estimator = MediaPipePoseEstimator(
        confidence_threshold=0.7
    )
    
    metrics_calculator = BiomechanicalCalculator()
    
    # Step 1: Segment serves
    console.print("\n[bold]Step 1: Serve Segmentation[/bold]")
    segments = segmenter.segment_video(video_path)
    
    # Step 2: Pose estimation for each segment
    console.print("\n[bold]Step 2: Pose Estimation[/bold]")
    all_pose_frames = []
    
    for i, segment in enumerate(segments):
        console.print(f"Processing segment {i+1}/{len(segments)}")
        
        # Extract segment video (in real implementation)
        # segment_video_path = output_dir / f"segment_{i+1}.mp4"
        # segmenter.extract_segment_video(video_path, segment, segment_video_path)
        
        # For demo, use the full video
        pose_frames = pose_estimator.estimate_pose_video(video_path)
        all_pose_frames.extend(pose_frames)
    
    # Step 3: Calculate biomechanical metrics
    console.print("\n[bold]Step 3: Biomechanical Analysis[/bold]")
    metrics = metrics_calculator.calculate_serve_metrics(all_pose_frames)
    
    # Display results
    console.print("\n[bold green]Analysis Results:[/bold green]")
    console.print(f"• Serve Duration: {metrics.duration:.2f} seconds")
    console.print(f"• Ball Toss Height: {metrics.ball_toss_height:.2f} meters")
    console.print(f"• Contact Point Height: {metrics.contact_point_height:.2f} meters")
    console.print(f"• Racket Speed: {metrics.racket_speed_at_contact:.1f} m/s")
    console.print(f"• Performance Score: {metrics.performance_score:.1f}/100")
    
    # Display timing metrics
    console.print("\n[bold]Timing Metrics:[/bold]")
    for key, value in metrics.timing_metrics.items():
        console.print(f"• {key.replace('_', ' ').title()}: {value:.2f}s")
    
    # Display joint angle ranges
    console.print("\n[bold]Joint Angle Ranges:[/bold]")
    joint_angles_by_name = {}
    for ja in metrics.joint_angles:
        if ja.joint_name not in joint_angles_by_name:
            joint_angles_by_name[ja.joint_name] = []
        joint_angles_by_name[ja.joint_name].append(ja.angle)
    
    for joint_name, angles in joint_angles_by_name.items():
        min_angle = min(angles)
        max_angle = max(angles)
        console.print(f"• {joint_name.replace('_', ' ').title()}: {min_angle:.1f}° - {max_angle:.1f}°")
    
    console.print("\n[bold green]Demo completed successfully![/bold green]")
    console.print("\nTo run the full analysis with your own video:")
    console.print("serve-ai analyze your_video.mp4 --output-dir ./results")

if __name__ == "__main__":
    main()
