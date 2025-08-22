# Tennis Serve AI Analysis

A comprehensive tennis serve analysis system that uses MediaPipe OpenPose to detect and analyze tennis serves from video footage. The system has been refactored to use **pure Functional Programming** and now includes **enhanced sequential serve detection** based on the serve detection plan.

## 🎾 **Enhanced Serve Detection**

The system now implements **sequential tennis serve detection** that identifies the three key phases of a tennis serve:

1. **Ball Toss Phase**: Left wrist above the head (above nose)
2. **Contact Phase**: Right wrist goes to hit the ball above the head  
3. **Follow-through Phase**: Right arm/wrist goes down again

### **Key Features**

- ✅ **Sequential Detection**: State machine approach for reliable serve detection
- ✅ **Enhanced Pose Estimation**: Higher model complexity for better accuracy
- ✅ **Quality Assessment**: Automatic validation and quality scoring
- ✅ **Video Segmentation**: Extract individual serve clips with metadata
- ✅ **Comprehensive Analysis**: Detailed reports with phase breakdown
- ✅ **Overlap Resolution**: Automatic handling of overlapping detections

## 🏗️ **Architecture**

The codebase uses **pure Functional Programming** with no side effects:

### **Core Modules**
- **Pose Estimation**: `src/serve_ai_analysis/pose/pose_functions.py`
- **Enhanced Serve Detection**: `src/serve_ai_analysis/video/serve_functions.py`
- **Video Processing**: `src/serve_ai_analysis/video/pipeline_functions.py`
- **Quality Assessment**: `src/serve_ai_analysis/video/quality_functions.py`

### **Enhanced Detection Functions**

```python
# Enhanced serve detection with state machine
serve_events = detect_serves_enhanced(video_path, config)

# Validate and assess quality
is_valid, validation_result = validate_serve_event(serve_event, pose_frames, config)
quality_metrics = assess_serve_segment_quality(serve_event, pose_frames)

# Extract serve segments with metadata
extracted_segments = extract_serve_segments(video_path, serve_events, output_dir, config)

# Generate comprehensive analysis report
analysis_report = generate_serve_analysis_report(serve_events, pose_frames, video_path, config)
```

## 🚀 **Quick Start**

### **Installation**

```bash
# Clone the repository
git clone <repository-url>
cd serve-ai-analysis

# Install dependencies
pip install -r requirements.txt
```

### **Basic Usage**

```python
from serve_ai_analysis.video.serve_functions import detect_serves_enhanced, ENHANCED_SERVE_CONFIG
from pathlib import Path

# Detect serves using enhanced algorithm
video_path = Path("path/to/tennis_video.mp4")
serve_events = detect_serves_enhanced(video_path, ENHANCED_SERVE_CONFIG)

print(f"Detected {len(serve_events)} serves")
```

### **Enhanced Demo**

Run the enhanced serve detection demo:

```bash
python examples/enhanced_serve_detection_demo.py
```

## 📊 **Enhanced Configuration**

The enhanced serve detection uses optimized parameters:

```python
ENHANCED_SERVE_CONFIG = {
    # Timing parameters
    "min_serve_duration": 1.5,
    "max_serve_duration": 8.0,
    "ball_toss_min_duration": 0.5,
    "contact_max_duration": 0.3,
    "follow_through_min_duration": 0.5,
    
    # Detection thresholds
    "confidence_threshold": 0.5,
    "min_visibility": 0.3,
    "ball_toss_confidence": 0.6,
    "contact_confidence": 0.7,
    "follow_through_confidence": 0.6,
    
    # Spatial thresholds
    "above_head_threshold": 0.1,
    "below_shoulder_threshold": 0.05,
    
    # State machine parameters
    "state_timeout_frames": 90,
    "min_gap_between_serves": 2.0,
    "serve_buffer_seconds": 3.0,
}
```

## 📈 **Analysis Reports**

The enhanced system generates comprehensive analysis reports including:

- **Serve Detection Summary**: Total serves, average duration, confidence
- **Quality Analysis**: High/medium/low quality breakdown
- **Phase Detection**: Ball toss, contact, follow-through validation
- **Common Issues**: Automatic identification of detection problems
- **Recommendations**: Suggestions for improving detection quality

## 🎯 **Detection Accuracy**

Expected performance metrics:

- **Ball Toss Detection**: >90% accuracy
- **Contact Phase Detection**: >85% accuracy  
- **Follow-through Detection**: >90% accuracy
- **Complete Serve Detection**: >80% accuracy
- **False Positives**: <10% of detected serves
- **False Negatives**: <15% of actual serves

## 🔧 **Advanced Usage**

### **Custom Configuration**

```python
from serve_ai_analysis.video.serve_functions import ENHANCED_SERVE_CONFIG

# Customize configuration
custom_config = ENHANCED_SERVE_CONFIG.copy()
custom_config["confidence_threshold"] = 0.6
custom_config["ball_toss_min_duration"] = 0.7

serve_events = detect_serves_enhanced(video_path, custom_config)
```

### **Quality Assessment**

```python
from serve_ai_analysis.video.serve_functions import (
    validate_serve_event, 
    assess_serve_segment_quality,
    resolve_serve_overlaps
)

# Validate serves
for serve_event in serve_events:
    is_valid, validation = validate_serve_event(serve_event, pose_frames, config)
    quality = assess_serve_segment_quality(serve_event, pose_frames)
    
    print(f"Serve valid: {is_valid}, Quality score: {quality['overall_score']:.2f}")

# Resolve overlaps
serve_events = resolve_serve_overlaps(serve_events, config)
```

### **Video Segmentation**

```python
from serve_ai_analysis.video.serve_functions import extract_serve_segments

# Extract serve segments with metadata
extracted_segments = extract_serve_segments(
    video_path, 
    serve_events, 
    output_dir, 
    config
)

# Each segment includes:
# - 3 seconds before serve start
# - Complete serve duration  
# - 3 seconds after serve end
# - Detailed metadata and quality metrics
```

## 📁 **Output Structure**

```
processed_serves_enhanced/
├── extracted_serves/
│   └── video_name/
│       ├── video_name_serve_001.mp4
│       ├── video_name_serve_002.mp4
│       └── video_name_serve_metadata.json
├── quality_reports/
│   └── video_name_serve_analysis.json
└── serve_events/
    └── video_name_serves.json
```

## 🧪 **Testing**

Run the test suite:

```bash
python -m pytest tests/
```

## 📚 **Documentation**

- **[SERVE_DETECTION_PLAN.md](docs/SERVE_DETECTION_PLAN.md)**: Comprehensive technical plan
- **[IMPLEMENTATION_ROADMAP.md](docs/IMPLEMENTATION_ROADMAP.md)**: Detailed implementation roadmap
- **[FUNCTIONAL_REFACTORING.md](docs/FUNCTIONAL_REFACTORING.md)**: OOP to FP refactoring details

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 **License**

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 **Acknowledgments**

- MediaPipe for pose estimation
- OpenCV for video processing
- Rich for beautiful console output
