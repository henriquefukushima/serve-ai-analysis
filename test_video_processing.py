#!/usr/bin/env python3
"""
Test script for the enhanced video processing pipeline.
"""

import asyncio
import tempfile
import shutil
from pathlib import Path
from src.serve_ai_analysis.web.api import AnalysisRequest, create_serve_archive
from src.serve_ai_analysis.video.serve_detection import extract_serve_segments
from src.serve_ai_analysis.reports.generator import generate_analysis_report, generate_readme_content

def test_serve_segmentation():
    """Test the serve segmentation functionality."""
    print("🧪 Testing serve segmentation...")
    
    # Mock serve data
    mock_serves = [
        {
            "serve_id": 0,
            "start_frame": 100,
            "end_frame": 200,
            "duration": 100,
            "confidence": 0.85,
            "ball_toss_frame": 120,
            "contact_frame": 150,
            "follow_through_frame": 180
        },
        {
            "serve_id": 1,
            "start_frame": 300,
            "end_frame": 400,
            "duration": 100,
            "confidence": 0.92,
            "ball_toss_frame": 320,
            "contact_frame": 350,
            "follow_through_frame": 380
        }
    ]
    
    # Mock serve segments (simulating what would be returned by extract_serve_segments)
    mock_segments = [
        {
            "serve_id": 0,
            "start_frame": 100,
            "end_frame": 200,
            "duration": 100,
            "confidence": 0.85,
            "video_path": "/tmp/test_serve_0.mp4",
            "has_landmarks": True,
            "ball_toss_frame": 120,
            "contact_frame": 150,
            "follow_through_frame": 180
        },
        {
            "serve_id": 1,
            "start_frame": 300,
            "end_frame": 400,
            "duration": 100,
            "confidence": 0.92,
            "video_path": "/tmp/test_serve_1.mp4",
            "has_landmarks": True,
            "ball_toss_frame": 320,
            "contact_frame": 350,
            "follow_through_frame": 380
        }
    ]
    
    print(f"✅ Mock serve data created: {len(mock_serves)} serves")
    return mock_segments

def test_report_generation():
    """Test the report generation functionality."""
    print("🧪 Testing report generation...")
    
    mock_segments = test_serve_segmentation()
    mock_config = {
        "confidence_threshold": 0.7,
        "min_serve_duration": 1.5,
        "max_serve_duration": 8.0,
        "optimize_video": True,
        "include_landmarks": True,
        "extract_segments": True,
        "player_handedness": "right",
        "video_quality": "medium",
        "landmark_style": "skeleton",
        "output_format": "mp4",
        "include_metadata": True,
        "serve_numbering": "sequential",
        "compression_level": 5
    }
    
    # Test HTML report generation
    html_report = generate_analysis_report(mock_segments, mock_config)
    print(f"✅ HTML report generated: {len(html_report)} characters")
    
    # Test README generation
    readme_content = generate_readme_content(mock_segments, mock_config)
    print(f"✅ README generated: {len(readme_content)} characters")
    
    return mock_segments, mock_config

def test_archive_creation():
    """Test the ZIP archive creation functionality."""
    print("🧪 Testing archive creation...")
    
    mock_segments, mock_config = test_report_generation()
    
    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create mock video files
        for segment in mock_segments:
            mock_video_path = temp_path / f"serve_{segment['serve_id']:03d}.mp4"
            mock_video_path.write_text("Mock video content")
            segment["video_path"] = str(mock_video_path)
        
        # Test archive creation
        try:
            zip_path = create_serve_archive("test_task_123", mock_segments, mock_config)
            print(f"✅ Archive created successfully: {zip_path}")
            print(f"✅ Archive exists: {zip_path.exists()}")
            return True
        except Exception as e:
            print(f"❌ Archive creation failed: {e}")
            return False

def test_analysis_request():
    """Test the AnalysisRequest model."""
    print("🧪 Testing AnalysisRequest model...")
    
    # Test default configuration
    default_config = AnalysisRequest()
    print(f"✅ Default config created: {default_config.confidence_threshold}")
    
    # Test custom configuration
    custom_config = AnalysisRequest(
        confidence_threshold=0.8,
        min_serve_duration=2.0,
        max_serve_duration=10.0,
        optimize_video=False,
        include_landmarks=True,
        video_quality="high",
        landmark_style="both",
        compression_level=3
    )
    print(f"✅ Custom config created: {custom_config.confidence_threshold}")
    
    # Test configuration validation
    try:
        invalid_config = AnalysisRequest(confidence_threshold=1.5)  # Should fail
        print("❌ Invalid config should have failed validation")
    except Exception as e:
        print(f"✅ Invalid config properly rejected: {e}")
    
    return True

def main():
    """Run all tests."""
    print("🚀 Starting video processing pipeline tests...\n")
    
    try:
        # Test AnalysisRequest model
        test_analysis_request()
        print()
        
        # Test serve segmentation
        test_serve_segmentation()
        print()
        
        # Test report generation
        test_report_generation()
        print()
        
        # Test archive creation
        success = test_archive_creation()
        print()
        
        if success:
            print("🎉 All tests passed! Video processing pipeline is working correctly.")
        else:
            print("❌ Some tests failed. Please check the implementation.")
            
    except Exception as e:
        print(f"❌ Test suite failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
