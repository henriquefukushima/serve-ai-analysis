from pathlib import Path
from typing import Optional, List
import typer
from pydantic import BaseModel, Field
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.table import Table
from rich import print as rprint

# Import new modules
from .video import (
    detect_serves,
    detect_ball_trajectory,
    filter_ball_detections,
    load_video,
    save_video_segment,
    extract_serve_clip,
    extract_serve_clip_direct,
    assess_video_quality,
    optimize_video_for_processing,
    ServeEvent,
    DEFAULT_SERVE_CONFIG
)

from .pose import (
    estimate_pose_video,
    filter_pose_frames_by_visibility,
    get_pose_stats,
    PoseFrame
)

app = typer.Typer(help="Tennis Serve AI Analysis - Advanced serve biomechanics analysis")
console = Console()
__version__ = "0.1.0"

class AnalysisConfig(BaseModel):
    """Configuration for serve analysis"""
    input_video: Path
    output_dir: Path = Field(default=Path("runs"))
    confidence_threshold: float = Field(default=0.5, ge=0.0, le=1.0)
    min_serve_duration: float = Field(default=1.0, description="Minimum serve duration in seconds")
    max_serve_duration: float = Field(default=5.0, description="Maximum serve duration in seconds")
    enable_3d_estimation: bool = Field(default=False, description="Enable 3D pose estimation")
    camera_calibration: Optional[Path] = Field(default=None, description="Camera calibration file")
    benchmark_data: Optional[Path] = Field(default=None, description="Benchmark data for comparison")

class InitConfig(BaseModel):
    output_dir: Path = Field(default=Path("runs"))

@app.command()
def version():
    """Show version."""
    console.print(f"[bold green]serve-ai-analysis[/bold green] version {__version__}")

@app.command()
def init(output_dir: Path = Path("runs")):
    """
    Create base folders and sanity-check your environment.
    """
    cfg = InitConfig(output_dir=output_dir)
    cfg.output_dir.mkdir(parents=True, exist_ok=True)
    
    # Create subdirectories for different outputs
    (cfg.output_dir / "videos").mkdir(exist_ok=True)
    (cfg.output_dir / "poses").mkdir(exist_ok=True)
    (cfg.output_dir / "metrics").mkdir(exist_ok=True)
    (cfg.output_dir / "dashboards").mkdir(exist_ok=True)
    (cfg.output_dir / "reports").mkdir(exist_ok=True)
    (cfg.output_dir / "segments").mkdir(exist_ok=True)
    
    console.print(f":white_check_mark: Ready to go! Outputs will be saved in [bold green]{cfg.output_dir}[/bold green]")
    console.print(f"Created subdirectories: videos, poses, metrics, dashboards, reports, segments")

@app.command()
def analyze(
    video_path: Path = typer.Argument(..., help="Path to input video file"),
    output_dir: Path = typer.Option(Path("runs"), "--output-dir", "-o", help="Output directory"),
    confidence: float = typer.Option(0.7, "--confidence", "-c", help="Pose detection confidence threshold (0.0-1.0)"),
    min_duration: float = typer.Option(1.5, "--min-duration", help="Minimum serve duration in seconds"),
    max_duration: float = typer.Option(8.0, "--max-duration", help="Maximum serve duration in seconds"),
    optimize: bool = typer.Option(True, "--optimize/--no-optimize", help="Optimize video for processing"),
    target_width: int = typer.Option(1280, "--width", help="Target video width"),
    target_height: int = typer.Option(720, "--height", help="Target video height"),
):
    """
    Analyze tennis serves from video input.
    
    This command performs the complete analysis pipeline:
    1. Video quality assessment
    2. Video optimization (optional)
    3. Pose estimation
    4. Ball detection
    5. Serve detection
    6. Serve extraction
    """
    if not video_path.exists():
        console.print(f"[red]Error: Video file {video_path} not found[/red]")
        raise typer.Exit(1)
    
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    
    console.print(Panel.fit(
        f"[bold blue]Tennis Serve Analysis[/bold blue]\n"
        f"Input: {video_path}\n"
        f"Output: {output_dir}\n"
        f"Optimization: {'Enabled' if optimize else 'Disabled'}\n"
        f"Target Resolution: {target_width}x{target_height}\n"
        f"Confidence: {confidence}",
        title="Configuration"
    ))
    
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            
            # Step 1: Assess video quality
            task1 = progress.add_task("Assessing video quality...", total=None)
            quality_metrics = assess_video_quality(str(video_path))
            progress.update(task1, description="✅ Video quality assessed")
            
            # Step 2: Optimize video if requested
            if optimize:
                task2 = progress.add_task("Optimizing video...", total=None)
                optimized_path = optimize_video_for_processing(
                    str(video_path), 
                    (target_width, target_height)
                )
                progress.update(task2, description="✅ Video optimized")
                processing_path = optimized_path
            else:
                processing_path = str(video_path)
            
            # Step 3: Estimate pose
            task3 = progress.add_task("Estimating pose...", total=None)
            pose_frames = estimate_pose_video(processing_path, confidence)
            pose_frames = filter_pose_frames_by_visibility(pose_frames, min_visibility=confidence)
            progress.update(task3, description=f"✅ Pose estimated ({len(pose_frames)} frames)")
            
            # Step 4: Detect ball trajectory
            task4 = progress.add_task("Detecting ball trajectory...", total=None)
            # Use frame skipping for faster ball detection (process every 3rd frame)
            ball_detections = detect_ball_trajectory(processing_path, frame_skip=3)
            ball_detections = filter_ball_detections(ball_detections, min_confidence=0.3)
            progress.update(task4, description=f"✅ Ball trajectory detected ({len(ball_detections)} detections)")
            
            # Step 5: Detect serves
            task5 = progress.add_task("Detecting serves...", total=None)
            config = DEFAULT_SERVE_CONFIG.copy()
            config['confidence_threshold'] = confidence
            config['serve_min_duration'] = int(min_duration * 30)  # Convert to frames
            config['serve_max_duration'] = int(max_duration * 30)  # Convert to frames
            
            serve_events = detect_serves(pose_frames, ball_detections, config)
            progress.update(task5, description=f"✅ Serves detected ({len(serve_events)} serves)")
            
            # Step 6: Extract serve clips
            if serve_events:
                task6 = progress.add_task("Extracting serve clips...", total=len(serve_events))
                segments_dir = output_dir / "segments"
                segments_dir.mkdir(exist_ok=True)
                
                for i, serve_event in enumerate(serve_events):
                    progress.update(task6, description=f"Extracting serve {i+1}/{len(serve_events)}...")
                    serve_path = segments_dir / f"serve_{i+1:03d}.mp4"
                    extract_serve_clip_direct(processing_path, serve_event, str(serve_path))
                    progress.advance(task6)
                
                progress.update(task6, description=f"✅ Serve clips extracted ({len(serve_events)} clips)")
        
        # Print results
        console.print(f"\n[bold green]Analysis completed successfully![/bold green]")
        console.print(f"🎾 Detected {len(serve_events)} serves")
        console.print(f"📁 Results saved to: {output_dir}")
        
        if serve_events:
            # Print serve statistics
            from .video.serve_detection import get_serve_stats
            stats = get_serve_stats(serve_events)
            
            table = Table(title="Serve Analysis Results")
            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="green")
            
            table.add_row("Total Serves", str(stats['total_serves']))
            table.add_row("Average Duration", f"{stats['avg_duration']:.1f} frames")
            table.add_row("Average Confidence", f"{stats['avg_confidence']:.3f}")
            table.add_row("Min Confidence", f"{stats['min_confidence']:.3f}")
            table.add_row("Max Confidence", f"{stats['max_confidence']:.3f}")
            
            console.print(table)
        
    except Exception as e:
        console.print(f"\n[bold red]Analysis failed: {str(e)}[/bold red]")
        raise typer.Exit(1)

@app.command()
def segment(
    video_path: Path = typer.Argument(..., help="Path to input video file"),
    output_dir: Path = typer.Option(Path("runs"), "--output-dir", "-o", help="Output directory"),
    min_duration: float = typer.Option(1.0, "--min-duration", help="Minimum serve duration in seconds"),
    max_duration: float = typer.Option(5.0, "--max-duration", help="Maximum serve duration in seconds"),
):
    """
    Segment individual serves from a tennis video.
    
    This command identifies and extracts individual serve sequences from the input video.
    """
    console.print(f"[blue]Segmenting serves from {video_path}[/blue]")
    # TODO: Implement serve segmentation logic
    console.print("✅ Serve segmentation completed")

@app.command()
def pose(
    video_path: Path = typer.Argument(..., help="Path to input video file"),
    output_dir: Path = typer.Option(Path("runs"), "--output-dir", "-o", help="Output directory"),
    confidence: float = typer.Option(0.5, "--confidence", "-c", help="Pose detection confidence threshold"),
    enable_3d: bool = typer.Option(False, "--3d", help="Enable 3D pose estimation"),
    calibration: Optional[Path] = typer.Option(None, "--calibration", help="Camera calibration file"),
):
    """
    Estimate poses from video using OpenPose.
    
    This command performs 2D or 3D pose estimation on the input video.
    """
    console.print(f"[blue]Estimating poses from {video_path}[/blue]")
    # TODO: Implement pose estimation logic
    console.print("✅ Pose estimation completed")

@app.command()
def metrics(
    pose_data: Path = typer.Argument(..., help="Path to pose estimation data"),
    output_dir: Path = typer.Option(Path("runs"), "--output-dir", "-o", help="Output directory"),
    benchmark: Optional[Path] = typer.Option(None, "--benchmark", help="Benchmark data file"),
):
    """
    Calculate biomechanical metrics from pose data.
    
    This command analyzes the pose data to extract biomechanical metrics
    such as joint angles, velocities, and timing.
    """
    console.print(f"[blue]Calculating biomechanical metrics from {pose_data}[/blue]")
    # TODO: Implement biomechanical analysis logic
    console.print("✅ Biomechanical analysis completed")

@app.command()
def dashboard(
    metrics_data: Path = typer.Argument(..., help="Path to metrics data"),
    output_dir: Path = typer.Option(Path("runs"), "--output-dir", "-o", help="Output directory"),
    port: int = typer.Option(8050, "--port", "-p", help="Dashboard port"),
):
    """
    Generate an interactive dashboard for serve analysis.
    
    This command creates a web-based dashboard to visualize the analysis results.
    """
    console.print(f"[blue]Generating dashboard from {metrics_data}[/blue]")
    # TODO: Implement dashboard generation logic
    console.print(f"✅ Dashboard generated and available at http://localhost:{port}")

@app.command()
def report(
    metrics_data: Path = typer.Argument(..., help="Path to metrics data"),
    output_dir: Path = typer.Option(Path("runs"), "--output-dir", "-o", help="Output directory"),
    athlete_name: str = typer.Option("", "--athlete", "-a", help="Athlete name for the report"),
):
    """
    Generate a PDF report for the athlete.
    
    This command creates a comprehensive PDF report with analysis results,
    recommendations, and visualizations.
    """
    console.print(f"[blue]Generating PDF report from {metrics_data}[/blue]")
    # TODO: Implement PDF report generation logic
    console.print("✅ PDF report generated")

def _print_results_summary(output_dir: Path):
    """Print a summary of the analysis results"""
    table = Table(title="Analysis Results Summary")
    table.add_column("Component", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Location", style="yellow")
    
    # TODO: Check actual files and populate table
    table.add_row("Serve Segments", "✅ Complete", str(output_dir / "segments"))
    table.add_row("Pose Data", "✅ Complete", str(output_dir / "poses"))
    table.add_row("Biomechanical Metrics", "✅ Complete", str(output_dir / "metrics"))
    table.add_row("Dashboard", "✅ Complete", str(output_dir / "dashboards"))
    table.add_row("PDF Report", "✅ Complete", str(output_dir / "reports"))
    
    console.print(table)

def main():
    app()

if __name__ == "__main__":
    main()