"""Basic tests for the Tennis Serve AI Analysis CLI."""

import pytest
from pathlib import Path
import tempfile
import shutil
from typer.testing import CliRunner

from serve_ai_analysis.cli import app

runner = CliRunner()

def test_version():
    """Test the version command."""
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "serve-ai-analysis version 0.0.1" in result.stdout

def test_init():
    """Test the init command."""
    with tempfile.TemporaryDirectory() as temp_dir:
        result = runner.invoke(app, ["init", "--output-dir", temp_dir])
        assert result.exit_code == 0
        assert "Ready to go!" in result.stdout
        
        # Check that directories were created
        output_path = Path(temp_dir)
        expected_dirs = ["videos", "poses", "metrics", "dashboards", "reports", "segments"]
        for dir_name in expected_dirs:
            assert (output_path / dir_name).exists()

def test_analyze_help():
    """Test the analyze command help."""
    result = runner.invoke(app, ["analyze", "--help"])
    assert result.exit_code == 0
    assert "Analyze tennis serves from video input" in result.stdout

def test_analyze_missing_video():
    """Test analyze command with missing video file."""
    result = runner.invoke(app, ["analyze", "nonexistent.mp4"])
    assert result.exit_code == 1
    assert "Video file nonexistent.mp4 not found" in result.stdout

def test_segment_help():
    """Test the segment command help."""
    result = runner.invoke(app, ["segment", "--help"])
    assert result.exit_code == 0
    assert "Segment individual serves from a tennis video" in result.stdout

def test_pose_help():
    """Test the pose command help."""
    result = runner.invoke(app, ["pose", "--help"])
    assert result.exit_code == 0
    assert "Estimate poses from video using OpenPose" in result.stdout

def test_metrics_help():
    """Test the metrics command help."""
    result = runner.invoke(app, ["metrics", "--help"])
    assert result.exit_code == 0
    assert "Calculate biomechanical metrics from pose data" in result.stdout

def test_dashboard_help():
    """Test the dashboard command help."""
    result = runner.invoke(app, ["dashboard", "--help"])
    assert result.exit_code == 0
    assert "Generate an interactive dashboard for serve analysis" in result.stdout

def test_report_help():
    """Test the report command help."""
    result = runner.invoke(app, ["report", "--help"])
    assert result.exit_code == 0
    assert "Generate a PDF report for the athlete" in result.stdout
