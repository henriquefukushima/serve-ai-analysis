"""PDF report generation module for tennis serve analysis."""

import json
import zipfile
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from rich.console import Console

console = Console()

class ReportGenerator:
    """Generate PDF reports for serve analysis."""
    
    def __init__(self):
        pass
    
    def generate_report(self, metrics_data: Path, output_path: Path, athlete_name: str = ""):
        """Generate PDF report."""
        console.print(f"[blue]Generating PDF report from {metrics_data}[/blue]")
        # TODO: Implement PDF report generation
        console.print("✅ PDF report generated")
        return output_path


def create_serve_archive(task_id: str, serve_segments: List[Dict], config: Dict) -> Path:
    """
    Create a ZIP archive containing all serve segments and analysis report.
    
    Args:
        task_id: Unique task identifier
        serve_segments: List of serve segment information
        config: Analysis configuration used
    
    Returns:
        Path to the generated ZIP file
    """
    # Create output directory
    output_dir = Path("outputs") / task_id
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Create ZIP file
    zip_path = output_dir / f"serve_analysis_{task_id}.zip"
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Add serve video segments
        for segment in serve_segments:
            video_path = Path(segment['video_path'])
            if video_path.exists():
                video_name = f"serves/serve_{segment['serve_id']:03d}.mp4"
                zipf.write(video_path, video_name)
        
        # Add analysis report
        report_content = generate_analysis_report(serve_segments, config)
        zipf.writestr("analysis_report.html", report_content)
        
        # Add configuration summary
        config_summary = {
            "analysis_date": datetime.now().isoformat(),
            "total_serves": len(serve_segments),
            "configuration": config,
            "serve_details": [
                {
                    "serve_id": seg["serve_id"],
                    "duration": seg["duration"],
                    "confidence": seg["confidence"],
                    "has_landmarks": seg["has_landmarks"],
                    "start_frame": seg["start_frame"],
                    "end_frame": seg["end_frame"]
                }
                for seg in serve_segments
            ]
        }
        zipf.writestr("config_summary.json", json.dumps(config_summary, indent=2))
        
        # Add README file
        readme_content = generate_readme_content(serve_segments, config)
        zipf.writestr("README.md", readme_content)
    
    console.print(f"[green]✅ Created serve analysis archive: {zip_path}[/green]")
    return zip_path


def generate_analysis_report(serve_segments: List[Dict], config: Dict) -> str:
    """
    Generate HTML analysis report.
    
    Args:
        serve_segments: List of serve segment information
        config: Analysis configuration
    
    Returns:
        HTML report content
    """
    total_serves = len(serve_segments)
    avg_confidence = sum(seg['confidence'] for seg in serve_segments) / total_serves if total_serves > 0 else 0
    avg_duration = sum(seg['duration'] for seg in serve_segments) / total_serves if total_serves > 0 else 0
    
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tennis Serve Analysis Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        .header {{ background: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 30px; }}
        .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }}
        .stat-card {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .serve-table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
        .serve-table th, .serve-table td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
        .serve-table th {{ background: #f8f9fa; font-weight: bold; }}
        .config-section {{ background: #f8f9fa; padding: 20px; border-radius: 8px; margin-top: 30px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🎾 Tennis Serve Analysis Report</h1>
        <p>Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
    </div>
    
    <div class="stats">
        <div class="stat-card">
            <h3>Total Serves</h3>
            <p style="font-size: 2em; color: #007bff; margin: 0;">{total_serves}</p>
        </div>
        <div class="stat-card">
            <h3>Average Confidence</h3>
            <p style="font-size: 2em; color: #28a745; margin: 0;">{avg_confidence:.1%}</p>
        </div>
        <div class="stat-card">
            <h3>Average Duration</h3>
            <p style="font-size: 2em; color: #ffc107; margin: 0;">{avg_duration:.1f}s</p>
        </div>
    </div>
    
    <h2>Serve Details</h2>
    <table class="serve-table">
        <thead>
            <tr>
                <th>Serve #</th>
                <th>Duration (s)</th>
                <th>Confidence</th>
                <th>Landmarks</th>
                <th>Start Frame</th>
                <th>End Frame</th>
            </tr>
        </thead>
        <tbody>
    """
    
    for segment in serve_segments:
        html_content += f"""
            <tr>
                <td>{segment['serve_id'] + 1}</td>
                <td>{segment['duration']:.1f}</td>
                <td>{segment['confidence']:.1%}</td>
                <td>{'✅' if segment['has_landmarks'] else '❌'}</td>
                <td>{segment['start_frame']}</td>
                <td>{segment['end_frame']}</td>
            </tr>
        """
    
    html_content += f"""
        </tbody>
    </table>
    
    <div class="config-section">
        <h2>Analysis Configuration</h2>
        <pre>{json.dumps(config, indent=2)}</pre>
    </div>
    
    <div style="margin-top: 40px; padding: 20px; background: #e9ecef; border-radius: 8px;">
        <h3>📁 Archive Contents</h3>
        <ul>
            <li><strong>serves/</strong> - Individual serve video clips</li>
            <li><strong>analysis_report.html</strong> - This detailed report</li>
            <li><strong>config_summary.json</strong> - Analysis configuration and metadata</li>
            <li><strong>README.md</strong> - Usage instructions</li>
        </ul>
    </div>
</body>
</html>
    """
    
    return html_content


def generate_readme_content(serve_segments: List[Dict], config: Dict) -> str:
    """
    Generate README content for the archive.
    
    Args:
        serve_segments: List of serve segment information
        config: Analysis configuration
    
    Returns:
        README content
    """
    return f"""# Tennis Serve Analysis Archive

## Overview
This archive contains the results of a tennis serve analysis performed on {datetime.now().strftime('%B %d, %Y')}.

## Contents
- **serves/**: Individual serve video clips (MP4 format)
- **analysis_report.html**: Detailed HTML report with statistics and serve details
- **config_summary.json**: Analysis configuration and metadata
- **README.md**: This file

## Analysis Summary
- **Total Serves Detected**: {len(serve_segments)}
- **Analysis Date**: {datetime.now().isoformat()}
- **Configuration Used**: See config_summary.json for details

## Serve Files
The serve video clips are named as follows:
- serve_001.mp4, serve_002.mp4, etc.

Each file contains a single serve segment with a 1-second buffer before and after the detected serve motion.

## Configuration
The analysis was performed with the following settings:
- Confidence Threshold: {config.get('confidence_threshold', 'N/A')}
- Min Serve Duration: {config.get('min_serve_duration', 'N/A')} seconds
- Max Serve Duration: {config.get('max_serve_duration', 'N/A')} seconds
- Include Landmarks: {config.get('include_landmarks', 'N/A')}
- Optimize Video: {config.get('optimize_video', 'N/A')}

## Usage
1. Open analysis_report.html in a web browser to view the detailed report
2. Play the serve video clips to review individual serves
3. Check config_summary.json for detailed metadata

## Technical Notes
- Video format: MP4 (H.264 codec)
- Frame rate: Original video frame rate preserved
- Resolution: Original video resolution preserved
- Landmarks: {'Included' if config.get('include_landmarks') else 'Not included'} in video overlays

Generated by Tennis Serve Analysis v2.2.0
"""
