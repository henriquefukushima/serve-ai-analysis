"""Unit tests for serve detection module."""

import pytest
import numpy as np
from unittest.mock import Mock, patch

from serve_ai_analysis.video.serve_detection import (
    ServeEvent,
    ServeState,
    ServePhase,
    detect_serves,
    update_serve_state,
    calculate_frame_confidence,
    validate_serve_event,
    get_serve_stats,
    DEFAULT_SERVE_CONFIG
)

from serve_ai_analysis.pose.pose_estimation import (
    PoseFrame,
    PoseLandmark
)

from serve_ai_analysis.video.ball_detection import BallDetection


class TestServeEvent:
    """Test ServeEvent dataclass."""
    
    def test_serve_event_creation(self):
        """Test creating a ServeEvent."""
        serve = ServeEvent(
            start_frame=10,
            end_frame=50,
            ball_toss_frame=15,
            contact_frame=30,
            follow_through_frame=40,
            confidence=0.8
        )
        
        assert serve.start_frame == 10
        assert serve.end_frame == 50
        assert serve.ball_toss_frame == 15
        assert serve.contact_frame == 30
        assert serve.follow_through_frame == 40
        assert serve.confidence == 0.8


class TestServeState:
    """Test ServeState dataclass."""
    
    def test_serve_state_creation(self):
        """Test creating a ServeState."""
        state = ServeState(
            phase=ServePhase.WAITING,
            start_frame=10,
            confidence_scores=[0.8, 0.9]
        )
        
        assert state.phase == ServePhase.WAITING
        assert state.start_frame == 10
        assert state.confidence_scores == [0.8, 0.9]
    
    def test_serve_state_default_confidence_scores(self):
        """Test that confidence_scores defaults to empty list."""
        state = ServeState(phase=ServePhase.WAITING)
        assert state.confidence_scores == []


class TestServeDetection:
    """Test serve detection functions."""
    
    def create_mock_pose_frame(self, frame_idx: int, landmarks: dict) -> PoseFrame:
        """Create a mock pose frame for testing."""
        return PoseFrame(
            frame_idx=frame_idx,
            landmarks=landmarks,
            timestamp=frame_idx / 30.0
        )
    
    def create_mock_landmark(self, x: float, y: float, z: float = 0.0, visibility: float = 0.9) -> PoseLandmark:
        """Create a mock landmark for testing."""
        return PoseLandmark(x=x, y=y, z=z, visibility=visibility)
    
    def test_calculate_frame_confidence_with_pose_only(self):
        """Test calculating frame confidence with pose data only."""
        landmarks = {
            'nose': self.create_mock_landmark(0.5, 0.5, visibility=0.8),
            'left_wrist': self.create_mock_landmark(0.3, 0.4, visibility=0.9),
            'right_wrist': self.create_mock_landmark(0.7, 0.4, visibility=0.7),
            'left_shoulder': self.create_mock_landmark(0.4, 0.6, visibility=0.9),
            'right_shoulder': self.create_mock_landmark(0.6, 0.6, visibility=0.9)
        }
        
        pose_frame = self.create_mock_pose_frame(0, landmarks)
        config = DEFAULT_SERVE_CONFIG.copy()
        
        confidence = calculate_frame_confidence(pose_frame, None, config)
        
        # Should be average of visibilities: (0.8 + 0.9 + 0.7 + 0.9 + 0.9) / 5 = 0.84
        assert confidence == pytest.approx(0.84, abs=0.01)
    
    def test_calculate_frame_confidence_with_ball(self):
        """Test calculating frame confidence with pose and ball data."""
        landmarks = {
            'nose': self.create_mock_landmark(0.5, 0.5, visibility=0.8),
            'left_wrist': self.create_mock_landmark(0.3, 0.4, visibility=0.9),
            'right_wrist': self.create_mock_landmark(0.7, 0.4, visibility=0.7),
            'left_shoulder': self.create_mock_landmark(0.4, 0.6, visibility=0.9),
            'right_shoulder': self.create_mock_landmark(0.6, 0.6, visibility=0.9)
        }
        
        pose_frame = self.create_mock_pose_frame(0, landmarks)
        ball_detection = BallDetection(frame_idx=0, x=0.5, y=0.3, confidence=0.6, radius=10)
        config = DEFAULT_SERVE_CONFIG.copy()
        
        confidence = calculate_frame_confidence(pose_frame, ball_detection, config)
        
        # Should be average of pose confidence (0.84) and ball confidence (0.6): (0.84 + 0.6) / 2 = 0.72
        assert confidence == pytest.approx(0.72, abs=0.01)
    

    
    def test_validate_serve_event_valid(self):
        """Test validation of a valid serve event."""
        serve_event = ServeEvent(
            start_frame=10,
            end_frame=50,
            ball_toss_frame=15,
            contact_frame=30,
            follow_through_frame=40,
            confidence=0.8
        )
        
        config = DEFAULT_SERVE_CONFIG.copy()
        assert validate_serve_event(serve_event, config) is True
    
    def test_validate_serve_event_invalid_duration(self):
        """Test validation of serve event with invalid duration."""
        serve_event = ServeEvent(
            start_frame=10,
            end_frame=200,  # Too long
            ball_toss_frame=15,
            contact_frame=30,
            follow_through_frame=40,
            confidence=0.8
        )
        
        config = DEFAULT_SERVE_CONFIG.copy()
        assert validate_serve_event(serve_event, config) is False
    
    def test_validate_serve_event_invalid_sequence(self):
        """Test validation of serve event with invalid sequence."""
        serve_event = ServeEvent(
            start_frame=10,
            end_frame=50,
            ball_toss_frame=40,  # After contact
            contact_frame=30,
            follow_through_frame=15,  # Before contact
            confidence=0.8
        )
        
        config = DEFAULT_SERVE_CONFIG.copy()
        assert validate_serve_event(serve_event, config) is False
    
    def test_validate_serve_event_low_confidence(self):
        """Test validation of serve event with low confidence."""
        serve_event = ServeEvent(
            start_frame=10,
            end_frame=50,
            ball_toss_frame=15,
            contact_frame=30,
            follow_through_frame=40,
            confidence=0.3  # Below threshold
        )
        
        config = DEFAULT_SERVE_CONFIG.copy()
        assert validate_serve_event(serve_event, config) is False
    
    def test_get_serve_stats_empty(self):
        """Test getting stats for empty serve events list."""
        stats = get_serve_stats([])
        assert stats == {}
    
    def test_get_serve_stats_with_events(self):
        """Test getting stats for serve events."""
        serve_events = [
            ServeEvent(start_frame=10, end_frame=50, ball_toss_frame=15, 
                      contact_frame=30, follow_through_frame=40, confidence=0.8),
            ServeEvent(start_frame=60, end_frame=100, ball_toss_frame=65, 
                      contact_frame=80, follow_through_frame=90, confidence=0.9)
        ]
        
        stats = get_serve_stats(serve_events)
        
        assert stats['total_serves'] == 2
        assert stats['avg_duration'] == 40.0  # (40 + 40) / 2
        assert stats['avg_confidence'] == pytest.approx(0.85, abs=0.01)  # (0.8 + 0.9) / 2
        assert stats['min_confidence'] == 0.8
        assert stats['max_confidence'] == 0.9


class TestServeStateMachine:
    """Test serve state machine transitions."""
    
    def create_mock_pose_frame(self, frame_idx: int, landmarks: dict) -> PoseFrame:
        """Create a mock pose frame for testing."""
        return PoseFrame(
            frame_idx=frame_idx,
            landmarks=landmarks,
            timestamp=frame_idx / 30.0
        )
    
    def create_mock_landmark(self, x: float, y: float, z: float = 0.0, visibility: float = 0.9) -> PoseLandmark:
        """Create a mock landmark for testing."""
        return PoseLandmark(x=x, y=y, z=z, visibility=visibility)
    
    def test_waiting_to_ball_toss_transition(self):
        """Test transition from waiting to ball toss phase."""
        landmarks = {
            'nose': self.create_mock_landmark(0.5, 0.5),
            'left_wrist': self.create_mock_landmark(0.3, 0.3),  # Above nose
            'right_wrist': self.create_mock_landmark(0.7, 0.6),
            'left_shoulder': self.create_mock_landmark(0.4, 0.6),
            'right_shoulder': self.create_mock_landmark(0.6, 0.6)
        }
        
        pose_frame = self.create_mock_pose_frame(10, landmarks)
        current_state = ServeState(phase=ServePhase.WAITING)
        config = DEFAULT_SERVE_CONFIG.copy()
        
        new_state, serve_event = update_serve_state(current_state, pose_frame, None, config)
        
        assert new_state.phase == ServePhase.BALL_TOSS
        assert new_state.start_frame == 10
        assert new_state.ball_toss_frame == 10
        assert serve_event is None


if __name__ == "__main__":
    pytest.main([__file__])
