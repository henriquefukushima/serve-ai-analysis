# Tennis Serve Detection: Sequential Detection Plan

## Overview

This document outlines a comprehensive plan for implementing sequential tennis serve detection using MediaPipe OpenPose. The goal is to detect serves by identifying the three key phases of a tennis serve: **ball toss**, **contact**, and **follow-through**.

## 🎯 **Serve Detection Strategy**

### **Sequential Detection Phases**

Based on the user's requirements, we need to detect serves using this sequential pattern:

1. **Ball Toss Phase**: Left wrist above the head
2. **Contact Phase**: Right wrist goes to hit the ball above the head  
3. **Follow-through Phase**: Right arm/wrist goes down again

### **Key Landmarks for Detection**

- **Left Wrist**: For ball toss detection
- **Right Wrist**: For contact and follow-through detection
- **Nose**: Reference point for "above head" positioning
- **Right Shoulder**: Reference for arm positioning
- **Left Shoulder**: Additional reference for body orientation

## 📋 **Implementation Plan**

### **Phase 1: Enhanced Pose Detection Setup**

#### **1.1 MediaPipe Configuration**
```python
def create_enhanced_pose_estimator(
    confidence_threshold: float = 0.5,
    model_complexity: int = 2,  # Higher complexity for better accuracy
    smooth_landmarks: bool = True,
    enable_segmentation: bool = False
) -> mp.solutions.pose.Pose:
    """Create enhanced MediaPipe pose estimator for serve detection."""
```

#### **1.2 Landmark Validation**
```python
def validate_serve_landmarks(pose_frame: PoseFrame) -> bool:
    """Validate that all required landmarks for serve detection are present."""
    
def get_serve_landmarks(pose_frame: PoseFrame) -> Dict[str, PoseLandmark]:
    """Extract and validate serve-specific landmarks."""
```

### **Phase 2: Sequential Serve Phase Detection**

#### **2.1 Ball Toss Detection**
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

**Detection Logic:**
- Left wrist Y-coordinate < nose Y-coordinate
- Minimum duration: 0.5 seconds (15 frames at 30fps)
- Confidence based on landmark visibility and position stability

#### **2.2 Contact Phase Detection**
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

**Detection Logic:**
- Right wrist Y-coordinate < nose Y-coordinate
- Must occur after ball toss phase
- Maximum duration: 0.3 seconds (9 frames at 30fps)
- High confidence threshold for precise timing

#### **2.3 Follow-through Detection**
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

**Detection Logic:**
- Right wrist Y-coordinate > right shoulder Y-coordinate
- Must occur after contact phase
- Minimum duration: 0.5 seconds (15 frames at 30fps)
- Confirms serve completion

### **Phase 3: State Machine Implementation**

#### **3.1 Serve State Machine**
```python
@dataclass
class ServeState:
    """Represents the current state of serve detection."""
    current_phase: str  # "waiting", "ball_toss", "contact", "follow_through", "completed"
    start_frame: Optional[int] = None
    ball_toss_frame: Optional[int] = None
    contact_frame: Optional[int] = None
    follow_through_frame: Optional[int] = None
    confidence_scores: List[float] = None

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

#### **3.2 Sequential Detection Algorithm**
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

**State Transitions:**
1. **waiting** → **ball_toss**: Ball toss detected
2. **ball_toss** → **contact**: Contact phase detected (after ball toss)
3. **contact** → **follow_through**: Follow-through detected (after contact)
4. **follow_through** → **completed**: Serve completed, create event
5. **any_state** → **waiting**: Reset on timeout or invalid sequence

### **Phase 4: Configuration and Tuning**

#### **4.1 Enhanced Configuration**
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
    "above_head_threshold": 0.1,  # How much above nose
    "below_shoulder_threshold": 0.05,  # How much below shoulder
    
    # State machine parameters
    "state_timeout_frames": 90,  # 3 seconds at 30fps
    "min_gap_between_serves": 2.0,
    "serve_buffer_seconds": 3.0,
}
```

#### **4.2 Adaptive Thresholds**
```python
def calculate_adaptive_thresholds(
    pose_frames: List[PoseFrame],
    config: Dict[str, Any]
) -> Dict[str, float]:
    """Calculate adaptive thresholds based on video characteristics."""
```

### **Phase 5: Video Segmentation**

#### **5.1 Serve Video Extraction**
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

#### **5.2 Segment Quality Assessment**
```python
def assess_serve_segment_quality(
    serve_event: ServeEvent,
    pose_frames: List[PoseFrame]
) -> Dict[str, Any]:
    """Assess the quality of detected serve segments."""
```

### **Phase 6: Validation and Testing**

#### **6.1 Serve Validation**
```python
def validate_serve_event(
    serve_event: ServeEvent,
    pose_frames: List[PoseFrame],
    config: Dict[str, Any]
) -> Tuple[bool, Dict[str, Any]]:
    """Validate detected serve events against quality criteria."""
```

#### **6.2 Overlap Detection and Resolution**
```python
def resolve_serve_overlaps(
    serve_events: List[ServeEvent],
    config: Dict[str, Any]
) -> List[ServeEvent]:
    """Resolve overlapping serve detections."""
```

## 🔧 **Implementation Steps**

### **Step 1: Create Enhanced Detection Functions**
1. Implement `detect_ball_toss()`
2. Implement `detect_contact_phase()`
3. Implement `detect_follow_through()`
4. Create `ServeState` dataclass

### **Step 2: Implement State Machine**
1. Create `update_serve_state()` function
2. Implement state transitions
3. Add timeout and reset logic

### **Step 3: Create Enhanced Sequential Detection**
1. Implement `detect_serves_sequential_enhanced()`
2. Add adaptive threshold calculation
3. Integrate with existing pipeline

### **Step 4: Add Video Segmentation**
1. Implement `extract_serve_segments()`
2. Add quality assessment
3. Create segment validation

### **Step 5: Testing and Validation**
1. Test with sample videos
2. Validate detection accuracy
3. Tune parameters based on results

## 📊 **Expected Outcomes**

### **Detection Accuracy**
- **Ball Toss Detection**: >90% accuracy
- **Contact Phase Detection**: >85% accuracy  
- **Follow-through Detection**: >90% accuracy
- **Complete Serve Detection**: >80% accuracy

### **Performance Metrics**
- **Processing Speed**: Real-time processing (30fps)
- **Memory Usage**: Efficient landmark storage
- **False Positives**: <10% of detected serves
- **False Negatives**: <15% of actual serves

### **Video Segmentation**
- **Individual Serve Clips**: 6-12 seconds each
- **Quality Assessment**: Automatic quality scoring
- **Metadata**: Serve timing, confidence scores, phase breakdown

## 🧪 **Testing Strategy**

### **Test Videos**
1. **Professional Matches**: High-quality serve footage
2. **Amateur Recordings**: Various quality levels
3. **Different Angles**: Side view, front view, back view
4. **Lighting Conditions**: Bright, dim, variable lighting

### **Validation Metrics**
1. **Precision**: True positives / (True positives + False positives)
2. **Recall**: True positives / (True positives + False negatives)
3. **F1-Score**: Harmonic mean of precision and recall
4. **Processing Time**: Frames per second processed

## 🚀 **Future Enhancements**

### **Advanced Features**
1. **Serve Type Classification**: Flat, slice, kick serves
2. **Ball Tracking**: Integrate ball detection for contact validation
3. **Player Identification**: Multiple player detection
4. **Court Position**: Serve position on court

### **Performance Optimizations**
1. **GPU Acceleration**: CUDA support for MediaPipe
2. **Batch Processing**: Multiple video processing
3. **Caching**: Pose data caching for repeated analysis
4. **Parallel Processing**: Multi-threaded detection

## 📝 **Implementation Notes**

### **MediaPipe Considerations**
- Use `model_complexity=2` for better accuracy
- Enable `smooth_landmarks=True` for stability
- Set appropriate confidence thresholds
- Handle landmark visibility properly

### **Performance Considerations**
- Process frames in batches for efficiency
- Cache pose estimation results
- Use numpy for vectorized operations
- Optimize memory usage for large videos

### **Robustness Considerations**
- Handle missing landmarks gracefully
- Implement fallback detection methods
- Add noise filtering for jittery detections
- Validate temporal consistency

This plan provides a comprehensive approach to implementing sequential tennis serve detection using MediaPipe OpenPose, focusing on the specific serve phases mentioned in the requirements.
