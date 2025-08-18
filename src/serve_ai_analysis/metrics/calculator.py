"""Biomechanical metrics calculator for tennis serve analysis."""

import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import json
from rich.console import Console

from ..pose.mediapipe_pose import PoseFrame, PoseLandmark

console = Console()

@dataclass
class JointAngle:
    """Represents a joint angle measurement."""
    joint_name: str
    angle: float
    timestamp: float
    frame_number: int
    unit: str = "degrees"

@dataclass
class Velocity:
    """Represents a velocity measurement."""
    landmark_name: str
    velocity_x: float
    velocity_y: float
    velocity_z: float
    speed: float
    timestamp: float
    frame_number: int
    unit: str = "m/s"

@dataclass
class ServeMetrics:
    """Complete biomechanical metrics for a tennis serve."""
    serve_id: str
    duration: float
    ball_toss_height: float
    contact_point_height: float
    racket_speed_at_contact: float
    joint_angles: List[JointAngle]
    velocities: List[Velocity]
    timing_metrics: Dict[str, float]
    performance_score: float

class BiomechanicalCalculator:
    """Calculate biomechanical metrics from pose data."""
    
    def __init__(self):
        self.gravity = 9.81  # m/s²
        
    def calculate_serve_metrics(
        self, 
        pose_frames: List[PoseFrame],
        serve_segment: Optional[Dict[str, Any]] = None
    ) -> ServeMetrics:
        """
        Calculate comprehensive biomechanical metrics for a tennis serve.
        
        Args:
            pose_frames: List of pose frames for the serve
            serve_segment: Optional serve segment metadata
            
        Returns:
            ServeMetrics object with all calculated metrics
        """
        console.print("[blue]Calculating biomechanical metrics...[/blue]")
        
        if not pose_frames:
            raise ValueError("No pose frames provided")
        
        # Calculate joint angles
        joint_angles = self._calculate_joint_angles(pose_frames)
        
        # Calculate velocities
        velocities = self._calculate_velocities(pose_frames)
        
        # Calculate timing metrics
        timing_metrics = self._calculate_timing_metrics(pose_frames)
        
        # Calculate serve-specific metrics
        ball_toss_height = self._estimate_ball_toss_height(pose_frames)
        contact_point_height = self._estimate_contact_point_height(pose_frames)
        racket_speed = self._calculate_racket_speed(pose_frames)
        
        # Calculate performance score
        performance_score = self._calculate_performance_score(
            joint_angles, velocities, timing_metrics
        )
        
        # Create serve metrics
        serve_id = serve_segment.get("serve_id", "serve_1") if serve_segment else "serve_1"
        duration = pose_frames[-1].timestamp - pose_frames[0].timestamp
        
        metrics = ServeMetrics(
            serve_id=serve_id,
            duration=duration,
            ball_toss_height=ball_toss_height,
            contact_point_height=contact_point_height,
            racket_speed_at_contact=racket_speed,
            joint_angles=joint_angles,
            velocities=velocities,
            timing_metrics=timing_metrics,
            performance_score=performance_score
        )
        
        console.print(f"✅ Calculated metrics for {serve_id}")
        return metrics
    
    def _calculate_joint_angles(self, pose_frames: List[PoseFrame]) -> List[JointAngle]:
        """Calculate joint angles throughout the serve."""
        joint_angles = []
        
        for frame in pose_frames:
            # Shoulder abduction (right arm)
            if all(name in frame.landmarks for name in ["right_shoulder", "right_elbow", "right_wrist"]):
                angle = self._calculate_angle_3d(
                    frame.landmarks["right_shoulder"],
                    frame.landmarks["right_elbow"],
                    frame.landmarks["right_wrist"]
                )
                joint_angles.append(JointAngle(
                    joint_name="right_shoulder_abduction",
                    angle=angle,
                    timestamp=frame.timestamp,
                    frame_number=frame.frame_number
                ))
            
            # Elbow flexion (right arm)
            if all(name in frame.landmarks for name in ["right_shoulder", "right_elbow", "right_wrist"]):
                angle = self._calculate_angle_3d(
                    frame.landmarks["right_shoulder"],
                    frame.landmarks["right_elbow"],
                    frame.landmarks["right_wrist"]
                )
                joint_angles.append(JointAngle(
                    joint_name="right_elbow_flexion",
                    angle=angle,
                    timestamp=frame.timestamp,
                    frame_number=frame.frame_number
                ))
            
            # Hip flexion
            if all(name in frame.landmarks for name in ["left_hip", "right_hip", "left_knee", "right_knee"]):
                # Use average of left and right hip angles
                left_angle = self._calculate_angle_3d(
                    frame.landmarks["left_hip"],
                    frame.landmarks["left_knee"],
                    frame.landmarks["left_ankle"]
                ) if "left_ankle" in frame.landmarks else 0
                
                right_angle = self._calculate_angle_3d(
                    frame.landmarks["right_hip"],
                    frame.landmarks["right_knee"],
                    frame.landmarks["right_ankle"]
                ) if "right_ankle" in frame.landmarks else 0
                
                avg_angle = (left_angle + right_angle) / 2
                joint_angles.append(JointAngle(
                    joint_name="hip_flexion",
                    angle=avg_angle,
                    timestamp=frame.timestamp,
                    frame_number=frame.frame_number
                ))
        
        return joint_angles
    
    def _calculate_velocities(self, pose_frames: List[PoseFrame]) -> List[Velocity]:
        """Calculate velocities of key landmarks."""
        velocities = []
        
        for i, frame in enumerate(pose_frames):
            if i == 0:
                continue  # Skip first frame (no previous frame to calculate velocity)
            
            prev_frame = pose_frames[i - 1]
            dt = frame.timestamp - prev_frame.timestamp
            
            if dt <= 0:
                continue
            
            # Calculate racket head velocity (approximated by right wrist)
            if "right_wrist" in frame.landmarks and "right_wrist" in prev_frame.landmarks:
                curr_pos = frame.landmarks["right_wrist"]
                prev_pos = prev_frame.landmarks["right_wrist"]
                
                # Convert normalized coordinates to meters (approximate)
                # Assuming 2m height and 1.5m width for the person
                scale_x = 1.5  # meters
                scale_y = 2.0  # meters
                
                dx = (curr_pos.x - prev_pos.x) * scale_x
                dy = (curr_pos.y - prev_pos.y) * scale_y
                dz = (curr_pos.z - prev_pos.z) * scale_x  # Approximate depth
                
                velocity_x = dx / dt
                velocity_y = dy / dt
                velocity_z = dz / dt
                speed = np.sqrt(velocity_x**2 + velocity_y**2 + velocity_z**2)
                
                velocities.append(Velocity(
                    landmark_name="right_wrist",
                    velocity_x=velocity_x,
                    velocity_y=velocity_y,
                    velocity_z=velocity_z,
                    speed=speed,
                    timestamp=frame.timestamp,
                    frame_number=frame.frame_number
                ))
        
        return velocities
    
    def _calculate_timing_metrics(self, pose_frames: List[PoseFrame]) -> Dict[str, float]:
        """Calculate timing-related metrics."""
        if len(pose_frames) < 2:
            return {}
        
        # Find key events
        ball_toss_frame = self._find_ball_toss_frame(pose_frames)
        contact_frame = self._find_contact_frame(pose_frames)
        
        timing_metrics = {
            "total_duration": pose_frames[-1].timestamp - pose_frames[0].timestamp,
            "ball_toss_time": pose_frames[ball_toss_frame].timestamp - pose_frames[0].timestamp if ball_toss_frame is not None else 0,
            "contact_time": pose_frames[contact_frame].timestamp - pose_frames[0].timestamp if contact_frame is not None else 0,
        }
        
        return timing_metrics
    
    def _estimate_ball_toss_height(self, pose_frames: List[PoseFrame]) -> float:
        """Estimate ball toss height based on arm position."""
        # Find frame with highest arm position
        max_arm_height = 0
        for frame in pose_frames:
            if "right_wrist" in frame.landmarks:
                # Convert normalized Y to height in meters
                height = (1 - frame.landmarks["right_wrist"].y) * 2.0  # Assuming 2m person height
                max_arm_height = max(max_arm_height, height)
        
        return max_arm_height
    
    def _estimate_contact_point_height(self, pose_frames: List[PoseFrame]) -> float:
        """Estimate contact point height."""
        # Use the highest point of the serve motion
        return self._estimate_ball_toss_height(pose_frames)
    
    def _calculate_racket_speed(self, pose_frames: List[PoseFrame]) -> float:
        """Calculate racket speed at contact point."""
        velocities = self._calculate_velocities(pose_frames)
        if not velocities:
            return 0.0
        
        # Find maximum speed (likely at contact)
        max_speed = max(v.speed for v in velocities)
        return max_speed
    
    def _calculate_performance_score(
        self, 
        joint_angles: List[JointAngle], 
        velocities: List[Velocity], 
        timing_metrics: Dict[str, float]
    ) -> float:
        """Calculate overall performance score (0-100)."""
        score = 50.0  # Base score
        
        # Score based on timing consistency
        if timing_metrics.get("total_duration", 0) > 0:
            # Ideal serve duration is around 2.5-3.5 seconds
            duration = timing_metrics["total_duration"]
            if 2.5 <= duration <= 3.5:
                score += 20
            elif 2.0 <= duration <= 4.0:
                score += 10
        
        # Score based on racket speed
        if velocities:
            max_speed = max(v.speed for v in velocities)
            if max_speed > 30:  # m/s
                score += 20
            elif max_speed > 20:
                score += 10
        
        # Score based on joint angle ranges
        if joint_angles:
            shoulder_angles = [ja.angle for ja in joint_angles if "shoulder" in ja.joint_name]
            if shoulder_angles:
                max_shoulder_angle = max(shoulder_angles)
                if max_shoulder_angle > 150:  # Good shoulder extension
                    score += 10
        
        return min(score, 100.0)
    
    def _calculate_angle_3d(self, p1: PoseLandmark, p2: PoseLandmark, p3: PoseLandmark) -> float:
        """Calculate 3D angle between three points."""
        # Convert to numpy arrays
        v1 = np.array([p1.x - p2.x, p1.y - p2.y, p1.z - p2.z])
        v2 = np.array([p3.x - p2.x, p3.y - p2.y, p3.z - p2.z])
        
        # Calculate angle
        cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
        cos_angle = np.clip(cos_angle, -1.0, 1.0)  # Clamp to valid range
        angle = np.arccos(cos_angle)
        
        return np.degrees(angle)
    
    def _find_ball_toss_frame(self, pose_frames: List[PoseFrame]) -> Optional[int]:
        """Find the frame where ball toss occurs."""
        # Simple heuristic: find frame with highest arm position
        max_height = 0
        toss_frame = None
        
        for i, frame in enumerate(pose_frames):
            if "right_wrist" in frame.landmarks:
                height = frame.landmarks["right_wrist"].y
                if height > max_height:
                    max_height = height
                    toss_frame = i
        
        return toss_frame
    
    def _find_contact_frame(self, pose_frames: List[PoseFrame]) -> Optional[int]:
        """Find the frame where ball contact occurs."""
        # Simple heuristic: find frame with highest racket speed
        max_speed = 0
        contact_frame = None
        
        velocities = self._calculate_velocities(pose_frames)
        for v in velocities:
            if v.speed > max_speed:
                max_speed = v.speed
                contact_frame = v.frame_number
        
        return contact_frame
    
    def save_metrics(self, metrics: ServeMetrics, output_path: Path):
        """Save metrics to JSON file."""
        data = {
            "serve_id": metrics.serve_id,
            "duration": metrics.duration,
            "ball_toss_height": metrics.ball_toss_height,
            "contact_point_height": metrics.contact_point_height,
            "racket_speed_at_contact": metrics.racket_speed_at_contact,
            "performance_score": metrics.performance_score,
            "timing_metrics": metrics.timing_metrics,
            "joint_angles": [
                {
                    "joint_name": ja.joint_name,
                    "angle": ja.angle,
                    "timestamp": ja.timestamp,
                    "frame_number": ja.frame_number,
                    "unit": ja.unit
                }
                for ja in metrics.joint_angles
            ],
            "velocities": [
                {
                    "landmark_name": v.landmark_name,
                    "velocity_x": v.velocity_x,
                    "velocity_y": v.velocity_y,
                    "velocity_z": v.velocity_z,
                    "speed": v.speed,
                    "timestamp": v.timestamp,
                    "frame_number": v.frame_number,
                    "unit": v.unit
                }
                for v in metrics.velocities
            ]
        }
        
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        console.print(f"Saved metrics to {output_path}")
