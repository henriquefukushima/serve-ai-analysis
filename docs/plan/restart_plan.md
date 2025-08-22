
## 📋 **Implementation Plan**

### **Phase 1: Foundation Setup (Week 1)**

#### **Task 1.1: Clean Repository Structure**
**Files to Remove:**
- `src/serve_ai_analysis/video/serve_functions.py` (1196 lines - too complex)
- `src/serve_ai_analysis/video/pipeline_functions.py` (334 lines - rebuild)
- `src/serve_ai_analysis/video/quality_functions.py` (321 lines - rebuild)
- `src/serve_ai_analysis/pose/pose_functions.py` (rebuild)
- All debug files in root directory
- Complex examples that don't work

**Files to Keep:**
- `src/serve_ai_analysis/cli.py` (222 lines - good CLI framework)
- `pyproject.toml` (dependencies)
- `README.md` (update)
- `data/test_detection/` (test videos)

#### **Task 1.2: Create New Module Structure**
```python
# src/serve_ai_analysis/video/__init__.py
from .serve_detection import detect_serves, ServeEvent
from .ball_detection import detect_ball_trajectory
from .video_utils import load_video, save_video_segment

__all__ = [
    'detect_serves',
    'ServeEvent', 
    'detect_ball_trajectory',
    'load_video',
    'save_video_segment'
]
```

#### **Task 1.3: Update CLI Integration**
```python
# src/serve_ai_analysis/cli.py - Update imports
from .video import detect_serves, ServeEvent
from .pose import estimate_pose_video
from .metrics import calculate_biomechanics
from .reports import generate_report
```

### **Phase 2: Core Serve Detection (Week 2)**

#### **Task 2.1: Implement Ball Detection**
**File**: `src/serve_ai_analysis/video/ball_detection.py`
**Based on**: Referenced repository's ball detection approach

```python
import cv2
import numpy as np
from dataclasses import dataclass
from typing import List, Tuple, Optional

@dataclass
class BallDetection:
    """Represents a detected ball in a frame."""
    frame_idx: int
    x: float
    y: float
    confidence: float
    radius: float

def detect_ball_trajectory(
    video_path: str,
    min_radius: int = 5,
    max_radius: int = 50,
    color_lower: Tuple[int, int, int] = (0, 100, 100),  # HSV for tennis ball
    color_upper: Tuple[int, int, int] = (20, 255, 255)
) -> List[BallDetection]:
    """
    Detect tennis ball trajectory using color-based detection.
    
    Args:
        video_path: Path to input video
        min_radius: Minimum ball radius to detect
        max_radius: Maximum ball radius to detect
        color_lower: Lower HSV threshold for ball color
        color_upper: Upper HSV threshold for ball color
    
    Returns:
        List of ball detections with frame indices and positions
    """
```

**Implementation Steps:**
1. Load video frames
2. Convert to HSV color space
3. Apply color thresholding for tennis ball
4. Find contours and filter by circularity
5. Track ball across frames
6. Return trajectory with confidence scores

#### **Task 2.2: Implement Pose Estimation**
**File**: `src/serve_ai_analysis/pose/pose_estimation.py`

```python
import mediapipe as mp
import cv2
import numpy as np
from dataclasses import dataclass
from typing import List, Dict, Optional

@dataclass
class PoseLandmark:
    """Represents a single pose landmark."""
    x: float
    y: float
    z: float
    visibility: float

@dataclass
class PoseFrame:
    """Represents pose data for a single frame."""
    frame_idx: int
    landmarks: Dict[str, PoseLandmark]
    timestamp: float

def estimate_pose_video(
    video_path: str,
    confidence_threshold: float = 0.5,
    model_complexity: int = 1
) -> List[PoseFrame]:
    """
    Estimate pose from video using MediaPipe.
    
    Args:
        video_path: Path to input video
        confidence_threshold: Minimum confidence for landmark detection
        model_complexity: MediaPipe model complexity (0, 1, 2)
    
    Returns:
        List of pose frames with landmarks
    """
```

**Implementation Steps:**
1. Initialize MediaPipe Pose
2. Process video frame by frame
3. Extract landmarks for serve detection (wrists, shoulders, nose)
4. Filter by confidence threshold
5. Return structured pose data

### **Phase 3: Serve Detection Algorithm (Week 3)**

#### **Task 3.1: Implement Serve Detection Logic**
**File**: `src/serve_ai_analysis/video/serve_detection.py`

```python
from dataclasses import dataclass
from typing import List, Tuple, Optional
import numpy as np

@dataclass
class ServeEvent:
    """Represents a detected serve event."""
    start_frame: int
    end_frame: int
    ball_toss_frame: int
    contact_frame: int
    follow_through_frame: int
    confidence: float
    serve_type: str  # "flat", "slice", "kick"

def detect_serves(
    pose_frames: List[PoseFrame],
    ball_detections: List[BallDetection],
    config: Optional[Dict] = None
) -> List[ServeEvent]:
    """
    Detect serves using pose and ball trajectory data.
    
    Algorithm based on referenced repository:
    1. Detect ball toss (left wrist above head)
    2. Detect contact (right wrist above head + ball position)
    3. Detect follow-through (right wrist below shoulder)
    4. Validate serve duration and sequence
    """
```

**Detection Algorithm:**
1. **Ball Toss Detection**: Left wrist above nose for minimum duration
2. **Contact Detection**: Right wrist above nose + ball in contact zone
3. **Follow-through Detection**: Right wrist below shoulder
4. **Validation**: Check sequence order and timing constraints

#### **Task 3.2: Implement State Machine**
```python
from enum import Enum

class ServePhase(Enum):
    WAITING = "waiting"
    BALL_TOSS = "ball_toss"
    CONTACT = "contact"
    FOLLOW_THROUGH = "follow_through"
    COMPLETED = "completed"

@dataclass
class ServeState:
    """State machine for serve detection."""
    phase: ServePhase
    start_frame: Optional[int] = None
    ball_toss_frame: Optional[int] = None
    contact_frame: Optional[int] = None
    follow_through_frame: Optional[int] = None
    confidence_scores: List[float] = None

def update_serve_state(
    current_state: ServeState,
    pose_frame: PoseFrame,
    ball_detection: Optional[BallDetection],
    config: Dict
) -> Tuple[ServeState, Optional[ServeEvent]]:
    """Update serve state machine and return completed serve if detected."""
```

### **Phase 4: Video Processing Utilities (Week 4)**

#### **Task 4.1: Video Loading and Saving**
**File**: `src/serve_ai_analysis/video/video_utils.py`

```python
import cv2
from pathlib import Path
from typing import Tuple, List

def load_video(video_path: str) -> Tuple[List[np.ndarray], float]:
    """Load video and return frames with FPS."""
    
def save_video_segment(
    frames: List[np.ndarray],
    output_path: str,
    fps: float = 30.0
) -> bool:
    """Save video segment to file."""
    
def extract_serve_clip(
    video_path: str,
    serve_event: ServeEvent,
    buffer_seconds: float = 1.0
) -> List[np.ndarray]:
    """Extract serve clip with buffer before and after."""
```

#### **Task 4.2: Video Quality Assessment**
```python
def assess_video_quality(video_path: str) -> Dict[str, float]:
    """Assess video quality for serve detection."""
    
def optimize_video_for_processing(
    video_path: str,
    target_resolution: Tuple[int, int] = (1280, 720)
) -> str:
    """Optimize video for processing."""
```

### **Phase 5: Biomechanical Analysis (Week 5)**

#### **Task 5.1: Basic Metrics**
**File**: `src/serve_ai_analysis/metrics/biomechanics.py`

```python
def calculate_serve_metrics(
    pose_frames: List[PoseFrame],
    serve_event: ServeEvent
) -> Dict[str, float]:
    """Calculate basic serve biomechanical metrics."""
    
def calculate_joint_angles(
    pose_frames: List[PoseFrame],
    serve_event: ServeEvent
) -> Dict[str, List[float]]:
    """Calculate joint angles during serve."""
    
def calculate_velocity_metrics(
    pose_frames: List[PoseFrame],
    serve_event: ServeEvent
) -> Dict[str, float]:
    """Calculate velocity and acceleration metrics."""
```

### **Phase 6: Reporting and Dashboard (Week 6)**

#### **Task 6.1: Report Generation**
**File**: `src/serve_ai_analysis/reports/report_generator.py`

```python
def generate_serve_report(
    serve_events: List[ServeEvent],
    metrics: Dict[str, float],
    output_path: str
) -> bool:
    """Generate comprehensive serve analysis report."""
```

#### **Task 6.2: Dashboard**
**File**: `src/serve_ai_analysis/dashboard/dashboard.py`

```python
def create_serve_dashboard(
    serve_events: List[ServeEvent],
    video_path: str,
    output_path: str
) -> bool:
    """Create interactive dashboard for serve analysis."""
```

## �� **Testing Strategy**

### **Unit Tests**
```python
# tests/test_serve_detection.py
def test_ball_detection():
    """Test ball detection on sample video."""
    
def test_pose_estimation():
    """Test pose estimation accuracy."""
    
def test_serve_detection():
    """Test serve detection algorithm."""
    
def test_state_machine():
    """Test serve state machine transitions."""
```

### **Integration Tests**
```python
# tests/test_integration.py
def test_full_pipeline():
    """Test complete serve analysis pipeline."""
    
def test_cli_commands():
    """Test all CLI commands with test videos."""
```

### **Test Data**
- Use `data/test_detection/serve_back_test.mp4`
- Use `data/test_detection/serve_right_test.mp4`
- Create synthetic test cases for edge cases

## 📊 **Success Metrics**

### **Technical Metrics**
- **Serve Detection Accuracy**: > 90% on test videos
- **Processing Speed**: < 2x real-time for 1080p video
- **Memory Usage**: < 4GB for standard video processing
- **Code Coverage**: > 80% test coverage

### **Quality Metrics**
- **Code Quality**: Pass all linting checks
- **Documentation**: 100% function documentation
- **Error Handling**: Graceful handling of edge cases
- **User Experience**: Clear error messages and progress indicators

## 🚀 **Implementation Timeline**

### **Week 1: Foundation**
- [ ] Clean repository structure
- [ ] Create new module architecture
- [ ] Update CLI integration
- [ ] Set up testing framework

### **Week 2: Core Detection**
- [ ] Implement ball detection
- [ ] Implement pose estimation
- [ ] Basic integration testing

### **Week 3: Serve Detection**
- [ ] Implement serve detection algorithm
- [ ] Implement state machine
- [ ] Test on sample videos

### **Week 4: Video Processing**
- [ ] Implement video utilities
- [ ] Implement quality assessment
- [ ] Optimize performance

### **Week 5: Analysis**
- [ ] Implement biomechanical metrics
- [ ] Create analysis functions
- [ ] Validate calculations

### **Week 6: Reporting**
- [ ] Implement report generation
- [ ] Create dashboard
- [ ] Final testing and documentation

## 📚 **Documentation Plan**

### **User Documentation**
- Update README with new functionality
- Create user guide with examples
- Add video tutorials for common use cases

### **Developer Documentation**
- API documentation for all modules
- Architecture diagrams
- Contributing guidelines
- Code style guide

## 🔧 **Technical Decisions**

### **Dependencies**
- **MediaPipe**: For pose estimation (proven, reliable)
- **OpenCV**: For video processing and ball detection
- **NumPy**: For numerical computations
- **Pydantic**: For data validation
- **Rich**: For CLI output formatting

### **Architecture Patterns**
- **Functional Programming**: Pure functions with no side effects
- **Data Classes**: For structured data representation
- **Configuration Objects**: For parameter management
- **State Machines**: For serve detection logic

### **Performance Considerations**
- **Batch Processing**: Process frames in batches
- **Memory Management**: Stream video processing
- **Caching**: Cache intermediate results
- **Parallel Processing**: Use multiprocessing where appropriate

## �� **Next Steps**

1. **Immediate**: Start with Phase 1 (Foundation Setup)
2. **Short-term**: Implement core detection algorithms
3. **Medium-term**: Add advanced features and optimization
4. **Long-term**: Machine learning enhancements

## 📝 **Notes**

- This plan preserves the existing CLI framework while rebuilding the core functionality
- The approach is based on the proven methods from the referenced repository
- Implementation will be test-driven with comprehensive coverage
- Documentation will be maintained throughout the development process
- Performance and accuracy are prioritized over feature complexity

---

**Created**: 2025-01-27  
**Last Updated**: 2025-01-27  
**Status**: Planning Phase  
**Next Review**: After Phase 1 completion