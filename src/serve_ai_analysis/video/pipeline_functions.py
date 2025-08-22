"""Functional video processing pipeline for tennis serve analysis."""

import time
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .quality_functions import (
    assess_video_quality, 
    display_quality_report, 
    save_quality_report,
    optimize_video,
    is_video_already_optimized,
    VideoQualityMetrics
)
from .serve_functions import (
    detect_serves,
    save_serve_events,
    extract_serve_videos_with_pose,
    ServeEvent
)

console = Console()

@dataclass
class ProcessingResult:
    """Result of video processing pipeline."""
    original_video: Path
    optimized_video: Path
    quality_metrics: VideoQualityMetrics
    serve_events: List[ServeEvent]
    extracted_serves: List[Path]
    processing_time: float
    success: bool
    error_message: Optional[str] = None

# Default configuration
DEFAULT_PIPELINE_CONFIG = {
    "optimize_videos": True,
    "target_resolution": (1280, 720),
    "min_serve_duration": 1.5,
    "max_serve_duration": 4.0,
    "confidence_threshold": 0.7
}

def create_output_structure(output_dir: Path):
    """Create the output directory structure."""
    directories = [
        "original",
        "optimized", 
        "quality_reports",
        "serve_events",
        "extracted_serves",
        "processed"
    ]
    
    for dir_name in directories:
        (output_dir / dir_name).mkdir(parents=True, exist_ok=True)
    
    console.print(f"📁 Created output structure in {output_dir}")

def process_single_video(
    video_path: Path, 
    output_dir: Path, 
    config: Dict[str, Any] = None
) -> ProcessingResult:
    """Process a single video through the complete pipeline."""
    if config is None:
        config = DEFAULT_PIPELINE_CONFIG
    
    start_time = time.time()
    
    try:
        console.print(Panel.fit(
            f"[bold blue]Video Processing Pipeline[/bold blue]\n"
            f"Processing Video: {video_path.name}\n"
            f"Output Directory: {output_dir}",
            title="Video Processing"
        ))
        
        # Step 1: Copy original video
        original_copy = output_dir / "original" / video_path.name
        if not original_copy.exists():
            import shutil
            shutil.copy2(video_path, original_copy)
            console.print(f"📋 Original video copied: {original_copy}")
        else:
            console.print(f"📋 Original video already exists: {original_copy}")
        
        # Step 2: Quality assessment
        console.print("\n[bold]Step 1: Video Quality Assessment[/bold]")
        quality_metrics = assess_video_quality(video_path, config["target_resolution"])
        display_quality_report(quality_metrics, video_path.name)
        
        # Save quality report
        quality_report_path = output_dir / "quality_reports" / f"{video_path.stem}_quality.json"
        save_quality_report(quality_metrics, quality_report_path)
        
        # Step 3: Video optimization
        optimized_video = output_dir / "optimized" / f"{video_path.stem}_optimized.mp4"
        
        if config["optimize_videos"]:
            if not optimized_video.exists() and not is_video_already_optimized(video_path, config["target_resolution"]):
                console.print("\n[bold]Step 2: Video Optimization[/bold]")
                if optimize_video(video_path, optimized_video, config["target_resolution"]):
                    console.print(f"✅ Video optimized: {optimized_video}")
                else:
                    console.print(f"❌ Failed to optimize video")
                    optimized_video = original_copy
            else:
                console.print(f"✅ Video already optimized: {optimized_video}")
        else:
            optimized_video = original_copy
        
        # Step 4: Serve detection
        console.print("\n[bold]Step 3: Serve Detection[/bold]")
        serve_config = {
            "min_serve_duration": config["min_serve_duration"],
            "max_serve_duration": config["max_serve_duration"],
            "confidence_threshold": config["confidence_threshold"],
            "min_visibility": 0.5,
            "serve_buffer_seconds": 3.0,
            "detection_cooldown_frames": 90,
            "min_gap_between_serves": 2.0
        }
        
        serve_events = detect_serves(optimized_video, serve_config)
        
        # Save serve events
        serve_events_path = output_dir / "serve_events" / f"{video_path.stem}_serves.json"
        save_serve_events(serve_events, serve_events_path)
        
        # Step 5: Extract individual serves
        extracted_serves = []
        if serve_events:
            console.print("\n[bold]Step 4: Serve Extraction[/bold]")
            serves_dir = output_dir / "extracted_serves" / video_path.stem
            serves_dir.mkdir(parents=True, exist_ok=True)
            
            extracted_serves = extract_serve_videos_with_pose(
                optimized_video, serve_events, serves_dir
            )
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Create result
        result = ProcessingResult(
            original_video=original_copy,
            optimized_video=optimized_video,
            quality_metrics=quality_metrics,
            serve_events=serve_events,
            extracted_serves=extracted_serves,
            processing_time=processing_time,
            success=True
        )
        
        # Display summary
        display_processing_summary(result)
        
        return result
        
    except Exception as e:
        processing_time = time.time() - start_time
        console.print(f"[red]Error processing {video_path.name}: {str(e)}[/red]")
        
        return ProcessingResult(
            original_video=video_path,
            optimized_video=video_path,
            quality_metrics=VideoQualityMetrics(
                resolution=(0, 0),
                fps=0.0,
                duration=0.0,
                total_frames=0,
                file_size_mb=0.0,
                brightness_mean=0.0,
                contrast_score=0.0,
                blur_score=0.0,
                compression_ratio=0.0,
                quality_score=0.0
            ),
            serve_events=[],
            extracted_serves=[],
            processing_time=processing_time,
            success=False,
            error_message=str(e)
        )

def process_videos(
    video_paths: List[Path], 
    output_dir: Path, 
    config: Dict[str, Any] = None
) -> List[ProcessingResult]:
    """Process multiple videos through the pipeline."""
    if config is None:
        config = DEFAULT_PIPELINE_CONFIG
    
    # Create output structure
    create_output_structure(output_dir)
    
    console.print(Panel.fit(
        f"[bold blue]Batch Video Processing[/bold blue]\n"
        f"Processing {len(video_paths)} Videos\n"
        f"Output Directory: {output_dir}",
        title="Batch Processing"
    ))
    
    results = []
    
    for i, video_path in enumerate(video_paths, 1):
        console.print(f"\nProcessing video {i}/{len(video_paths)}: {video_path.name}")
        result = process_single_video(video_path, output_dir, config)
        results.append(result)
    
    # Display batch summary
    display_batch_summary(results)
    
    return results

def display_processing_summary(result: ProcessingResult):
    """Display a summary of the processing results."""
    table = Table(title="Processing Summary")
    
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="magenta")
    
    table.add_row("Original Video", result.original_video.name)
    table.add_row("Optimized Video", result.optimized_video.name)
    table.add_row("Quality Score", f"{result.quality_metrics.quality_score:.1f}/100")
    table.add_row("Resolution", f"{result.quality_metrics.resolution[0]}x{result.quality_metrics.resolution[1]}")
    table.add_row("Duration", f"{result.quality_metrics.duration:.1f}s")
    table.add_row("Detected Serves", str(len(result.serve_events)))
    table.add_row("Extracted Serves", str(len(result.extracted_serves)))
    table.add_row("Processing Time", f"{result.processing_time:.1f}s")
    table.add_row("Status", "✅ Success" if result.success else "❌ Failed")
    
    console.print(table)
    
    # Display serve details if any were detected
    if result.serve_events:
        serve_table = Table(title="Detected Serves")
        serve_table.add_column("Serve #", style="cyan")
        serve_table.add_column("Type", style="magenta")
        serve_table.add_column("Duration", style="green")
        serve_table.add_column("Confidence", style="yellow")
        
        for i, serve in enumerate(result.serve_events, 1):
            serve_table.add_row(
                str(i),
                serve.serve_type,
                f"{serve.duration:.1f}s",
                f"{serve.confidence:.2f}"
            )
        
        console.print(serve_table)
    
    console.print(f"✅ Completed {result.original_video.name}")

def display_batch_summary(results: List[ProcessingResult]):
    """Display a summary of batch processing results."""
    successful = [r for r in results if r.success]
    failed = [r for r in results if not r.success]
    total_serves = sum(len(r.serve_events) for r in successful)
    total_time = sum(r.processing_time for r in results)
    
    table = Table(title="Batch Processing Summary")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="magenta")
    
    table.add_row("Total Videos", str(len(results)))
    table.add_row("Successful", str(len(successful)))
    table.add_row("Failed", str(len(failed)))
    table.add_row("Total Serves Detected", str(total_serves))
    table.add_row("Total Processing Time", f"{total_time:.1f}s")
    table.add_row("Average Time per Video", f"{total_time/len(results):.1f}s" if results else "0s")
    
    console.print(table)

def generate_processing_report(results: List[ProcessingResult], output_path: Path):
    """Generate a comprehensive processing report."""
    import json
    
    report_data = {
        "summary": {
            "total_videos": len(results),
            "successful": len([r for r in results if r.success]),
            "failed": len([r for r in results if not r.success]),
            "total_serves": sum(len(r.serve_events) for r in results if r.success),
            "total_processing_time": sum(r.processing_time for r in results)
        },
        "videos": []
    }
    
    for result in results:
        video_data = {
            "filename": result.original_video.name,
            "success": result.success,
            "processing_time": result.processing_time,
            "quality_score": result.quality_metrics.quality_score,
            "detected_serves": len(result.serve_events),
            "extracted_serves": len(result.extracted_serves),
            "error_message": result.error_message
        }
        report_data["videos"].append(video_data)
    
    with open(output_path, 'w') as f:
        json.dump(report_data, f, indent=2)
    
    console.print(f"📊 Processing report saved to {output_path}")

def load_processing_report(input_path: Path) -> Dict[str, Any]:
    """Load a processing report from JSON file."""
    import json
    
    with open(input_path, 'r') as f:
        return json.load(f)
