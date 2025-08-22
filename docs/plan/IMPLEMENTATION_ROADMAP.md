# Tennis Serve Detection: Implementation Roadmap

## Overview

This document provides a detailed technical roadmap for implementing the sequential tennis serve detection system. It breaks down the implementation into specific coding tasks with clear deliverables and dependencies.

## 🎯 **Implementation Phases**

### **Phase 1: Core Detection Functions (Week 1)**

#### **Task 1.1: Enhanced Pose Estimator**
**File**: `src/serve_ai_analysis/pose/pose_functions.py`
**Deliverable**: Enhanced MediaPipe configuration

```python
def create_enhanced_pose_estimator(
    confidence_threshold: float = 0.5,
    model_complexity: int = 2,
    smooth_landmarks: bool = True,
    enable_segmentation: bool = False
) -> mp.solutions.pose.Pose:
    """Create enhanced MediaPipe pose estimator for serve detection."""
```

**Implementation Steps**:
1. Update `create_pose_estimator()` function
2. Add model complexity parameter
3. Test with different complexity levels
4. Benchmark performance vs accuracy

#### **Task 1.2: Landmark Validation Functions**
**File**: `src/serve_ai_analysis/pose/pose_functions.py`
**Deliverable**: Serve-specific landmark validation

```python
def validate_serve_landmarks(pose_frame: PoseFrame) -> bool:
    """Validate that all required landmarks for serve detection are present."""

def get_serve_landmarks(pose_frame: PoseFrame) -> Dict[str, PoseLandmark]:
    """Extract and validate serve-specific landmarks."""
```

**Implementation Steps**:
1. Define required landmarks for serve detection
2. Implement visibility threshold checking
3. Add confidence validation
4. Create landmark extraction helper

#### **Task 1.3: Serve State Data Structure**
**File**: `src/serve_ai_analysis/video/serve_functions.py`
**Deliverable**: ServeState dataclass

```python
@dataclass
class ServeState:
    """Represents the current state of serve detection."""
    current_phase: str
    start_frame: Optional[int] = None
    ball_toss_frame: Optional[int] = None
    contact_frame: Optional[int] = None
    follow_through_frame: Optional[int] = None
    confidence_scores: List[float] = None
```

**Implementation Steps**:
1. Create ServeState dataclass
2. Add phase enumeration
3. Include confidence tracking
4. Add validation methods

### **Phase 2: Phase Detection Functions (Week 2)**

#### **Task 2.1: Ball Toss Detection**
**File**: `src/serve_ai_analysis/video/serve_functions.py`
**Deliverable**: Ball toss detection function

```python
def detect_ball_toss(
    pose_frames: List[PoseFrame], 
    frame_idx: int, 
    config: Dict[str, Any]
) -> Tuple[bool, float]:
    """
    Detect ball toss phase:
    - Left wrist above the head (above nose)
    - Sustained for minimum duration
    - Returns (detected, confidence_score)
    """
```

**Implementation Steps**:
1. Implement left wrist above nose detection
2. Add duration validation (0.5 seconds minimum)
3. Calculate confidence based on visibility and stability
4. Add temporal smoothing for jitter reduction

#### **Task 2.2: Contact Phase Detection**
**File**: `src/serve_ai_analysis/video/serve_functions.py`
**Deliverable**: Contact phase detection function

```python
def detect_contact_phase(
    pose_frames: List[PoseFrame], 
    frame_idx: int, 
    config: Dict[str, Any]
) -> Tuple[bool, float]:
    """
    Detect contact phase:
    - Right wrist above the head (above nose)
    - Occurs after ball toss
    - Returns (detected, confidence_score)
    """
```

**Implementation Steps**:
1. Implement right wrist above nose detection
2. Add sequential validation (must follow ball toss)
3. Implement maximum duration check (0.3 seconds)
4. Add high confidence threshold for precise timing

#### **Task 2.3: Follow-through Detection**
**File**: `src/serve_ai_analysis/video/serve_functions.py`
**Deliverable**: Follow-through detection function

```python
def detect_follow_through(
    pose_frames: List[PoseFrame], 
    frame_idx: int, 
    config: Dict[str, Any]
) -> Tuple[bool, float]:
    """
    Detect follow-through phase:
    - Right wrist/arm goes down (below shoulder)
    - Occurs after contact phase
    - Returns (detected, confidence_score)
    """
```

**Implementation Steps**:
1. Implement right wrist below shoulder detection
2. Add sequential validation (must follow contact)
3. Implement minimum duration check (0.5 seconds)
4. Add serve completion validation

### **Phase 3: State Machine Implementation (Week 3)**

#### **Task 3.1: State Update Function**
**File**: `src/serve_ai_analysis/video/serve_functions.py`
**Deliverable**: State machine update logic

```python
def update_serve_state(
    current_state: ServeState,
    pose_frames: List[PoseFrame],
    frame_idx: int,
    config: Dict[str, Any]
) -> Tuple[ServeState, Optional[ServeEvent]]:
    """
    Update serve state machine based on current frame detection.
    Returns (updated_state, serve_event_if_completed)
    """
```

**Implementation Steps**:
1. Implement state transition logic
2. Add timeout handling for each state
3. Implement serve completion detection
4. Add confidence score tracking

#### **Task 3.2: Enhanced Sequential Detection**
**File**: `src/serve_ai_analysis/video/serve_functions.py`
**Deliverable**: Main sequential detection algorithm

```python
def detect_serves_sequential_enhanced(
    pose_frames: List[PoseFrame], 
    video_name: str, 
    config: Dict[str, Any] = None
) -> List[ServeEvent]:
    """
    Enhanced sequential serve detection using state machine approach.
    """
```

**Implementation Steps**:
1. Initialize serve state machine
2. Process frames sequentially
3. Update state based on phase detection
4. Create serve events when completed
5. Handle multiple serves in sequence

### **Phase 4: Configuration and Tuning (Week 4)**

#### **Task 4.1: Enhanced Configuration**
**File**: `src/serve_ai_analysis/video/serve_functions.py`
**Deliverable**: Comprehensive configuration system

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

**Implementation Steps**:
1. Define comprehensive configuration structure
2. Add parameter validation
3. Create configuration merging utilities
4. Add configuration documentation

#### **Task 4.2: Adaptive Thresholds**
**File**: `src/serve_ai_analysis/video/serve_functions.py`
**Deliverable**: Adaptive threshold calculation

```python
def calculate_adaptive_thresholds(
    pose_frames: List[PoseFrame],
    config: Dict[str, Any]
) -> Dict[str, float]:
    """Calculate adaptive thresholds based on video characteristics."""
```

**Implementation Steps**:
1. Analyze video characteristics (lighting, movement, etc.)
2. Calculate dynamic thresholds
3. Implement threshold adjustment logic
4. Add threshold validation

### **Phase 5: Video Segmentation (Week 5)**

#### **Task 5.1: Enhanced Video Extraction**
**File**: `src/serve_ai_analysis/video/serve_functions.py`
**Deliverable**: Improved serve video extraction

```python
def extract_serve_segments(
    video_path: Path,
    serve_events: List[ServeEvent],
    output_dir: Path,
    config: Dict[str, Any] = None
) -> List[Path]:
    """
    Extract individual serve video segments.
    Each segment includes:
    - 3 seconds before serve start
    - Complete serve duration
    - 3 seconds after serve end
    """
```

**Implementation Steps**:
1. Enhance existing `extract_serve_video()` function
2. Add buffer time calculation
3. Implement segment naming convention
4. Add progress tracking for batch processing

#### **Task 5.2: Quality Assessment**
**File**: `src/serve_ai_analysis/video/serve_functions.py`
**Deliverable**: Serve segment quality assessment

```python
def assess_serve_segment_quality(
    serve_event: ServeEvent,
    pose_frames: List[PoseFrame]
) -> Dict[str, Any]:
    """Assess the quality of detected serve segments."""
```

**Implementation Steps**:
1. Calculate pose data quality metrics
2. Assess landmark visibility throughout segment
3. Calculate confidence scores
4. Generate quality report

### **Phase 6: Validation and Testing (Week 6)**

#### **Task 6.1: Serve Validation**
**File**: `src/serve_ai_analysis/video/serve_functions.py`
**Deliverable**: Serve event validation

```python
def validate_serve_event(
    serve_event: ServeEvent,
    pose_frames: List[PoseFrame],
    config: Dict[str, Any]
) -> Tuple[bool, Dict[str, Any]]:
    """Validate detected serve events against quality criteria."""
```

**Implementation Steps**:
1. Implement quality criteria checking
2. Add duration validation
3. Check landmark visibility
4. Generate validation report

#### **Task 6.2: Overlap Resolution**
**File**: `src/serve_ai_analysis/video/serve_functions.py`
**Deliverable**: Overlap detection and resolution

```python
def resolve_serve_overlaps(
    serve_events: List[ServeEvent],
    config: Dict[str, Any]
) -> List[ServeEvent]:
    """Resolve overlapping serve detections."""
```

**Implementation Steps**:
1. Detect overlapping serve events
2. Implement overlap resolution logic
3. Merge or split overlapping serves
4. Validate resolved serves

## 🧪 **Testing Strategy**

### **Unit Testing**
**File**: `tests/test_serve_detection.py`
**Deliverable**: Comprehensive test suite

```python
def test_detect_ball_toss():
    """Test ball toss detection with mock data."""

def test_detect_contact_phase():
    """Test contact phase detection."""

def test_detect_follow_through():
    """Test follow-through detection."""

def test_serve_state_machine():
    """Test state machine transitions."""

def test_sequential_detection():
    """Test complete sequential detection."""
```

### **Integration Testing**
**File**: `tests/test_integration.py`
**Deliverable**: End-to-end testing

```python
def test_complete_pipeline():
    """Test complete serve detection pipeline."""

def test_video_segmentation():
    """Test video segmentation functionality."""

def test_quality_assessment():
    """Test quality assessment functionality."""
```

### **Performance Testing**
**File**: `tests/test_performance.py`
**Deliverable**: Performance benchmarks

```python
def test_processing_speed():
    """Test processing speed with various video lengths."""

def test_memory_usage():
    """Test memory usage during processing."""

def test_accuracy_benchmarks():
    """Test detection accuracy with known datasets."""
```

## 📊 **Success Metrics**

### **Detection Accuracy**
- **Ball Toss Detection**: >90% accuracy
- **Contact Phase Detection**: >85% accuracy
- **Follow-through Detection**: >90% accuracy
- **Complete Serve Detection**: >80% accuracy

### **Performance Metrics**
- **Processing Speed**: Real-time processing (30fps)
- **Memory Usage**: <2GB for 1-hour video
- **False Positives**: <10% of detected serves
- **False Negatives**: <15% of actual serves

### **Code Quality**
- **Test Coverage**: >90% code coverage
- **Documentation**: All functions documented
- **Type Hints**: 100% type annotation coverage
- **Code Style**: PEP 8 compliance

## 🚀 **Deployment Plan**

### **Phase 1: Development Environment**
1. Set up development environment
2. Install dependencies
3. Configure testing framework
4. Set up CI/CD pipeline

### **Phase 2: Testing Environment**
1. Create test video dataset
2. Set up automated testing
3. Configure performance monitoring
4. Implement error tracking

### **Phase 3: Production Deployment**
1. Optimize for production use
2. Add logging and monitoring
3. Implement error handling
4. Create deployment documentation

## 📝 **Documentation Requirements**

### **Code Documentation**
- Function docstrings with examples
- Type hints for all functions
- Inline comments for complex logic
- README updates

### **User Documentation**
- Installation guide
- Usage examples
- Configuration guide
- Troubleshooting guide

### **API Documentation**
- Function signatures
- Parameter descriptions
- Return value documentation
- Error handling documentation

This roadmap provides a clear path for implementing the sequential tennis serve detection system with specific tasks, deliverables, and success metrics for each phase.
