"""FastAPI backend for tennis serve analysis web application."""

import os
import uuid
from pathlib import Path
from typing import List, Optional
from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
import asyncio
from concurrent.futures import ThreadPoolExecutor
import json

# Import the serve analysis modules
from ..video import (
    detect_serves,
    detect_ball_trajectory,
    filter_ball_detections,
    load_video,
    save_video_segment,
    extract_serve_clip,
    extract_serve_clip_direct,
    assess_video_quality,
    optimize_video_for_processing,
    ServeEvent,
    DEFAULT_SERVE_CONFIG
)

from ..pose import (
    estimate_pose_video,
    filter_pose_frames_by_visibility,
    get_pose_stats,
    PoseFrame
)

# Create FastAPI app
app = FastAPI(
    title="Tennis Serve Analysis API",
    description="API for analyzing tennis serves from video recordings",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create directories for file storage
UPLOAD_DIR = Path("uploads")
OUTPUT_DIR = Path("outputs")
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

# Mount static files for serving processed videos
app.mount("/static", StaticFiles(directory="outputs"), name="static")

# Thread pool for running analysis tasks
executor = ThreadPoolExecutor(max_workers=2)

# Store for tracking analysis tasks
analysis_tasks = {}

class AnalysisRequest(BaseModel):
    """Request model for analysis configuration."""
    confidence_threshold: float = Field(default=0.7, ge=0.0, le=1.0)
    min_serve_duration: float = Field(default=1.5, ge=0.5, le=10.0)
    max_serve_duration: float = Field(default=8.0, ge=1.0, le=20.0)
    optimize_video: bool = Field(default=True)
    include_landmarks: bool = Field(default=True)
    extract_segments: bool = Field(default=True)
    player_handedness: str = Field(default="right", pattern="^(right|left)$")

class AnalysisStatus(BaseModel):
    """Status model for analysis progress."""
    task_id: str
    status: str  # "pending", "processing", "completed", "failed"
    progress: float = 0.0
    message: str = ""
    results: Optional[dict] = None
    error: Optional[str] = None

class ServeResult(BaseModel):
    """Model for serve analysis results."""
    serve_id: int
    start_frame: int
    end_frame: int
    duration: float
    confidence: float
    video_url: str
    thumbnail_url: Optional[str] = None

@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Tennis Serve Analysis API", "version": "2.0.0"}

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": "2.0.0"}

@app.post("/upload", response_model=dict)
async def upload_video(
    file: UploadFile = File(...),
    config: AnalysisRequest = None
):
    """Upload video and start analysis."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    # Validate file type
    allowed_extensions = {".mp4", ".avi", ".mov", ".mkv"}
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
        )
    
    # Generate unique task ID
    task_id = str(uuid.uuid4())
    
    # Save uploaded file
    file_path = UPLOAD_DIR / f"{task_id}_{file.filename}"
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    # Initialize task status
    analysis_tasks[task_id] = AnalysisStatus(
        task_id=task_id,
        status="pending",
        progress=0.0,
        message="Video uploaded successfully"
    )
    
    # Start background analysis
    background_tasks = BackgroundTasks()
    background_tasks.add_task(run_analysis, task_id, file_path, config or AnalysisRequest())
    
    return {
        "task_id": task_id,
        "message": "Video uploaded and analysis started",
        "file_size": len(content)
    }

@app.get("/status/{task_id}", response_model=AnalysisStatus)
async def get_analysis_status(task_id: str):
    """Get the status of an analysis task."""
    if task_id not in analysis_tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return analysis_tasks[task_id]

@app.get("/results/{task_id}")
async def get_analysis_results(task_id: str):
    """Get the results of a completed analysis."""
    if task_id not in analysis_tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = analysis_tasks[task_id]
    if task.status != "completed":
        raise HTTPException(status_code=400, detail="Analysis not completed")
    
    return task.results

@app.get("/download/{task_id}/{serve_id}")
async def download_serve_video(task_id: str, serve_id: int):
    """Download a specific serve video."""
    if task_id not in analysis_tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = analysis_tasks[task_id]
    if task.status != "completed":
        raise HTTPException(status_code=400, detail="Analysis not completed")
    
    # Find the serve video file
    serve_file = OUTPUT_DIR / f"{task_id}_serve_{serve_id}.mp4"
    if not serve_file.exists():
        raise HTTPException(status_code=404, detail="Serve video not found")
    
    return FileResponse(
        serve_file,
        media_type="video/mp4",
        filename=f"serve_{serve_id}.mp4"
    )

async def run_analysis(task_id: str, video_path: Path, config: AnalysisRequest):
    """Run the serve analysis in a background task."""
    try:
        task = analysis_tasks[task_id]
        task.status = "processing"
        task.progress = 0.1
        task.message = "Assessing video quality..."
        
        # Step 1: Video quality assessment
        quality_result = await asyncio.get_event_loop().run_in_executor(
            executor, assess_video_quality, video_path
        )
        
        task.progress = 0.2
        task.message = "Optimizing video for processing..."
        
        # Step 2: Video optimization (if enabled)
        if config.optimize_video:
            optimized_path = await asyncio.get_event_loop().run_in_executor(
                executor, optimize_video_for_processing, video_path
            )
            video_path = optimized_path
        
        task.progress = 0.3
        task.message = "Detecting player pose..."
        
        # Step 3: Pose estimation
        pose_frames = await asyncio.get_event_loop().run_in_executor(
            executor, estimate_pose_video, video_path, config.confidence_threshold
        )
        
        task.progress = 0.5
        task.message = "Detecting ball trajectory..."
        
        # Step 4: Ball detection
        ball_detections = await asyncio.get_event_loop().run_in_executor(
            executor, detect_ball_trajectory, video_path
        )
        
        task.progress = 0.7
        task.message = "Identifying serve segments..."
        
        # Step 5: Serve detection
        serve_config = DEFAULT_SERVE_CONFIG.copy()
        serve_config.update({
            "min_serve_duration": config.min_serve_duration,
            "max_serve_duration": config.max_serve_duration,
            "confidence_threshold": config.confidence_threshold
        })
        
        serve_events = await asyncio.get_event_loop().run_in_executor(
            executor, detect_serves, video_path, pose_frames, ball_detections, serve_config
        )
        
        task.progress = 0.9
        task.message = "Extracting serve clips..."
        
        # Step 6: Extract serve clips
        serve_results = []
        for i, serve_event in enumerate(serve_events):
            output_path = OUTPUT_DIR / f"{task_id}_serve_{i}.mp4"
            
            await asyncio.get_event_loop().run_in_executor(
                executor, extract_serve_clip_direct, video_path, serve_event, output_path
            )
            
            serve_results.append(ServeResult(
                serve_id=i,
                start_frame=serve_event.start_frame,
                end_frame=serve_event.end_frame,
                duration=serve_event.end_frame - serve_event.start_frame,
                confidence=serve_event.confidence,
                video_url=f"/static/{output_path.name}",
                thumbnail_url=None  # Could add thumbnail generation later
            ))
        
        task.progress = 1.0
        task.status = "completed"
        task.message = f"Analysis completed. Found {len(serve_events)} serves."
        task.results = {
            "total_serves": len(serve_events),
            "video_quality": quality_result,
            "pose_stats": get_pose_stats(pose_frames),
            "serves": [serve.dict() for serve in serve_results],
            "config": config.dict()
        }
        
    except Exception as e:
        task.status = "failed"
        task.error = str(e)
        task.message = f"Analysis failed: {str(e)}"

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
