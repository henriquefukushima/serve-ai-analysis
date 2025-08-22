"""Comprehensive video processing pipeline for tennis serve analysis."""

import cv2
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.table import Table
import json
import shutil

from .quality_assessor import VideoQualityAssessor, VideoQualityMetrics
from .serve_detector import ServeDetector, ServeEvent
from .preprocessing import VideoPreprocessor

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

class VideoProcessingPipeline:
    """Complete video processing pipeline for tennis serve analysis."""
    
    def __init__(
        self,
        output_dir: Path,
        optimize_videos: bool = True,
        target_resolution: tuple = (1280, 720),
        min_serve_duration: float = 1.5,
        max_serve_duration: float = 4.0,
        confidence_threshold: float = 0.7
    ):
        self.output_dir = output_dir
        self.optimize_videos = optimize_videos
        self.target_resolution = target_resolution
        self.min_serve_duration = min_serve_duration
        self.max_serve_duration = max_serve_duration
        self.confidence_threshold = confidence_threshold
        
        # Initialize components
        self.quality_assessor = VideoQualityAssessor()
        self.quality_assessor.target_resolution = target_resolution
        self.preprocessor = VideoPreprocessor()
        self.serve_detector = ServeDetector(
            min_serve_duration=min_serve_duration,
            max_serve_duration=max_serve_duration,
            confidence_threshold=confidence_threshold
        )
        
        # Create output directory structure
        self._create_output_structure()
    
    def _create_output_structure(self):
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
            (self.output_dir / dir_name).mkdir(parents=True, exist_ok=True)
        
        console.print(f"📁 Created output structure in {self.output_dir}")
    
    def _is_video_already_optimized(self, video_path: Path) -> Optional[Path]:
        """Check if video has already been optimized."""
        optimized_path = self.output_dir / "optimized" / f"{video_path.stem}_optimized.mp4"
        if optimized_path.exists():
            # Check if the optimized file is newer than the original
            if optimized_path.stat().st_mtime > video_path.stat().st_mtime:
                return optimized_path
        return None
    
    def process_video(self, video_path: Path) -> ProcessingResult:
        """
        Process a single video through the complete pipeline.
        
        Args:
            video_path: Path to the input video
            
        Returns:
            ProcessingResult with all processing information
        """
        import time
        start_time = time.time()
        
        console.print(Panel.fit(
            f"[bold blue]Processing Video: {video_path.name}[/bold blue]\n"
            f"Output Directory: {self.output_dir}",
            title="Video Processing Pipeline"
        ))
        
        try:
            # Step 1: Copy original video
            original_copy = self.output_dir / "original" / video_path.name
            if not original_copy.exists():
                shutil.copy2(video_path, original_copy)
                console.print(f"📋 Copied original video to {original_copy}")
            else:
                console.print(f"📋 Original video already exists: {original_copy}")
            
            # Step 2: Assess video quality
            console.print("\n[bold]Step 1: Video Quality Assessment[/bold]")
            quality_metrics = self.quality_assessor.assess_video_quality(video_path)
            
            # Save quality report
            quality_report_path = self.output_dir / "quality_reports" / f"{video_path.stem}_quality.json"
            self.quality_assessor.save_quality_report(quality_metrics, quality_report_path)
            
            # Step 3: Optimize video if needed
            optimized_video = original_copy
            if self.optimize_videos:
                # Check if already optimized
                existing_optimized = self._is_video_already_optimized(video_path)
                if existing_optimized:
                    console.print(f"✅ Video already optimized: {existing_optimized.name}")
                    optimized_video = existing_optimized
                elif quality_metrics.quality_score < 80:
                    console.print("\n[bold]Step 2: Video Optimization[/bold]")
                    optimized_path = self.output_dir / "optimized" / f"{video_path.stem}_optimized.mp4"
                    optimized_video = self.quality_assessor.optimize_video(
                        original_copy, optimized_path, self.target_resolution
                    )
                else:
                    console.print("✅ Video quality is good, skipping optimization")
            
            # Step 4: Detect serves
            console.print("\n[bold]Step 3: Serve Detection[/bold]")
            serve_events = self.serve_detector.detect_serves(optimized_video)
            
            # Save serve events
            serve_events_path = self.output_dir / "serve_events" / f"{video_path.stem}_serves.json"
            self.serve_detector.save_serve_events(serve_events, serve_events_path)
            
            # Step 5: Extract individual serves
            extracted_serves = []
            if serve_events:
                console.print("\n[bold]Step 4: Serve Extraction[/bold]")
                serves_dir = self.output_dir / "extracted_serves" / video_path.stem
                serves_dir.mkdir(parents=True, exist_ok=True)
                
                extracted_serves = self.serve_detector.extract_serve_videos(
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
            self._display_processing_summary(result)
            
            return result
            
        except Exception as e:
            processing_time = time.time() - start_time
            console.print(f"[red]❌ Error processing video: {str(e)}[/red]")
            
            return ProcessingResult(
                original_video=video_path,
                optimized_video=video_path,
                quality_metrics=VideoQualityMetrics(0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
                serve_events=[],
                extracted_serves=[],
                processing_time=processing_time,
                success=False,
                error_message=str(e)
            )
    
    def process_videos(self, video_paths: List[Path]) -> List[ProcessingResult]:
        """
        Process multiple videos through the pipeline.
        
        Args:
            video_paths: List of video paths to process
            
        Returns:
            List of ProcessingResult objects
        """
        results = []
        
        console.print(Panel.fit(
            f"[bold blue]Processing {len(video_paths)} Videos[/bold blue]\n"
            f"Output Directory: {self.output_dir}",
            title="Batch Video Processing"
        ))
        
        for i, video_path in enumerate(video_paths):
            console.print(f"\n[bold]Processing video {i+1}/{len(video_paths)}: {video_path.name}[/bold]")
            
            result = self.process_video(video_path)
            results.append(result)
            
            console.print(f"✅ Completed {video_path.name}")
        
        # Display batch summary
        self._display_batch_summary(results)
        
        return results
    
    def _display_processing_summary(self, result: ProcessingResult):
        """Display a summary of the processing results."""
        table = Table(title="Processing Summary")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Original Video", str(result.original_video.name))
        table.add_row("Optimized Video", str(result.optimized_video.name))
        table.add_row("Quality Score", f"{result.quality_metrics.quality_score}/100")
        table.add_row("Resolution", f"{result.quality_metrics.resolution[0]}x{result.quality_metrics.resolution[1]}")
        table.add_row("Duration", f"{result.quality_metrics.duration:.1f}s")
        table.add_row("Detected Serves", str(len(result.serve_events)))
        table.add_row("Extracted Serves", str(len(result.extracted_serves)))
        table.add_row("Processing Time", f"{result.processing_time:.1f}s")
        table.add_row("Status", "✅ Success" if result.success else "❌ Failed")
        
        console.print(table)
        
        if result.serve_events:
            serve_table = Table(title="Detected Serves")
            serve_table.add_column("Serve #", style="cyan")
            serve_table.add_column("Type", style="green")
            serve_table.add_column("Duration", style="yellow")
            serve_table.add_column("Confidence", style="blue")
            
            for i, serve in enumerate(result.serve_events):
                serve_table.add_row(
                    str(i + 1),
                    serve.serve_type,
                    f"{serve.duration:.1f}s",
                    f"{serve.confidence:.2f}"
                )
            
            console.print(serve_table)
    
    def _display_batch_summary(self, results: List[ProcessingResult]):
        """Display a summary of batch processing results."""
        successful = [r for r in results if r.success]
        failed = [r for r in results if not r.success]
        
        total_serves = sum(len(r.serve_events) for r in successful)
        total_processing_time = sum(r.processing_time for r in results)
        
        table = Table(title="Batch Processing Summary")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Total Videos", str(len(results)))
        table.add_row("Successful", str(len(successful)))
        table.add_row("Failed", str(len(failed)))
        table.add_row("Total Serves Detected", str(total_serves))
        table.add_row("Total Processing Time", f"{total_processing_time:.1f}s")
        table.add_row("Average Time per Video", f"{total_processing_time/len(results):.1f}s")
        
        console.print(table)
        
        if failed:
            console.print("\n[red]Failed Videos:[/red]")
            for result in failed:
                console.print(f"  - {result.original_video.name}: {result.error_message}")
    
    def generate_processing_report(self, results: List[ProcessingResult], output_path: Path):
        """Generate a comprehensive processing report."""
        successful = [r for r in results if r.success]
        
        report_data = {
            "summary": {
                "total_videos": len(results),
                "successful": len(successful),
                "failed": len(results) - len(successful),
                "total_serves": sum(len(r.serve_events) for r in successful),
                "total_processing_time": sum(r.processing_time for r in results)
            },
            "videos": []
        }
        
        for result in results:
            video_data = {
                "filename": result.original_video.name,
                "success": result.success,
                "quality_score": result.quality_metrics.quality_score,
                "resolution": result.quality_metrics.resolution,
                "duration": result.quality_metrics.duration,
                "detected_serves": len(result.serve_events),
                "processing_time": result.processing_time,
                "error_message": result.error_message
            }
            
            if result.serve_events:
                video_data["serves"] = [
                    {
                        "serve_type": serve.serve_type,
                        "duration": serve.duration,
                        "confidence": serve.confidence,
                        "ball_toss_frame": serve.ball_toss_frame,
                        "contact_frame": serve.contact_frame
                    }
                    for serve in result.serve_events
                ]
            
            report_data["videos"].append(video_data)
        
        with open(output_path, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        console.print(f"📊 Processing report saved to {output_path}")
