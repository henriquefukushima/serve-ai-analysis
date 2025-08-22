#!/usr/bin/env python3
"""
Process tennis serve videos using the enhanced video processing pipeline.

This script demonstrates the complete pipeline:
1. Video quality assessment
2. Video optimization (if needed)
3. Serve detection using pose landmarks
4. Serve extraction and classification
"""

import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from serve_ai_analysis.video import VideoProcessingPipeline
from rich.console import Console
from rich.panel import Panel

console = Console()

def main():
    """Process the serve videos in the data/test directory."""
    console.print(Panel.fit(
        "[bold blue]Tennis Serve Video Processing Pipeline[/bold blue]\n"
        "Processing serve videos with quality assessment and pose-based detection",
        title="Serve Analysis"
    ))
    
    # Define paths
    data_dir = Path("data/test")
    output_dir = Path("processed_serves")
    
    # Check if data directory exists
    if not data_dir.exists():
        console.print(f"[red]Error: Data directory {data_dir} not found[/red]")
        console.print("Please make sure you have uploaded the serve videos to data/test/")
        return
    
    # Find all video files
    video_extensions = [".mp4", ".avi", ".mov", ".mkv"]
    video_files = []
    
    for ext in video_extensions:
        video_files.extend(data_dir.glob(f"*{ext}"))
    
    if not video_files:
        console.print(f"[red]No video files found in {data_dir}[/red]")
        console.print("Expected files: serve_right.mp4, serve_left.mp4, serve_back.mp4")
        return
    
    console.print(f"Found {len(video_files)} video files:")
    for video_file in video_files:
        console.print(f"  - {video_file.name}")
    
    # Initialize the processing pipeline
    pipeline = VideoProcessingPipeline(
        output_dir=output_dir,
        optimize_videos=True,
        target_resolution=(1280, 720),
        min_serve_duration=1.5,
        max_serve_duration=8.0,
        confidence_threshold=0.7
    )
    
    # Process all videos
    console.print(f"\n[bold]Starting video processing...[/bold]")
    results = pipeline.process_videos(video_files)
    
    # Generate comprehensive report
    report_path = output_dir / "processing_report.json"
    pipeline.generate_processing_report(results, report_path)
    
    # Display final summary
    successful = [r for r in results if r.success]
    total_serves = sum(len(r.serve_events) for r in successful)
    
    console.print(Panel.fit(
        f"[bold green]Processing Complete![/bold green]\n"
        f"✅ Successfully processed {len(successful)}/{len(video_files)} videos\n"
        f"🎾 Detected {total_serves} serves total\n"
        f"📁 Results saved to: {output_dir}\n"
        f"📊 Report: {report_path}",
        title="Final Results"
    ))
    
    # Show what was created
    console.print("\n[bold]Generated Files:[/bold]")
    if output_dir.exists():
        for item in output_dir.rglob("*"):
            if item.is_file():
                relative_path = item.relative_to(output_dir)
                console.print(f"  📄 {relative_path}")
    
    console.print(f"\n[bold]Next Steps:[/bold]")
    console.print("1. Review the extracted serve videos in processed_serves/extracted_serves/")
    console.print("2. Check the quality reports in processed_serves/quality_reports/")
    console.print("3. Analyze the serve events data in processed_serves/serve_events/")
    console.print("4. Run biomechanical analysis on the extracted serves")

if __name__ == "__main__":
    main()
