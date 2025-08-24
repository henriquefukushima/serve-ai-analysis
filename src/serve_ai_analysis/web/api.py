"""FastAPI backend for tennis serve analysis web application."""

import os
import uuid
from pathlib import Path
from typing import List, Optional
from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks, Form
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
    DEFAULT_SERVE_CONFIG,
    extract_serve_segments
)

from ..pose import (
    estimate_pose_video,
    filter_pose_frames_by_visibility,
    get_pose_stats,
    PoseFrame
)

from ..reports.generator import create_serve_archive

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
    # New parameters
    video_quality: str = Field(default="medium", pattern="^(low|medium|high|original)$")
    landmark_style: str = Field(default="skeleton", pattern="^(points|skeleton|both)$")
    output_format: str = Field(default="mp4", pattern="^(mp4|avi|mov)$")
    include_metadata: bool = Field(default=True)
    serve_numbering: str = Field(default="sequential", pattern="^(sequential|timestamp)$")
    compression_level: int = Field(default=5, ge=1, le=10)

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

def validate_video_file(file: UploadFile) -> bool:
    """Validate uploaded video file."""
    if not file.filename:
        return False
    
    # Check file extension
    allowed_extensions = {".mp4", ".avi", ".mov", ".mkv", ".webm"}
    file_ext = Path(file.filename).suffix.lower()
    
    if file_ext not in allowed_extensions:
        return False
    
    # Additional MIME type validation (optional)
    allowed_mime_types = {
        "video/mp4", "video/mp4v-es", "video/x-m4v",
        "video/avi", "video/x-msvideo",
        "video/quicktime", "video/x-ms-wmv",
        "video/x-matroska", "video/webm"
    }
    
    if file.content_type and file.content_type not in allowed_mime_types:
        # Log warning but don't reject
        print(f"Warning: Unexpected MIME type for {file.filename}: {file.content_type}")
    
    return True

@app.post("/upload", response_model=dict)
async def upload_video(
    file: UploadFile = File(...),
    config: str = Form(None),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """Upload video and start analysis."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    # Use enhanced validation
    if not validate_video_file(file):
        raise HTTPException(
            status_code=400, 
            detail="Unsupported file type. Allowed: MP4, AVI, MOV, MKV, WebM"
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
    
    # Parse config if provided
    analysis_config = AnalysisRequest()
    if config:
        try:
            config_dict = json.loads(config)
            analysis_config = AnalysisRequest(**config_dict)
        except (json.JSONDecodeError, ValueError) as e:
            print(f"Warning: Invalid config JSON: {e}")
    
    # Start background analysis
    background_tasks.add_task(run_analysis, task_id, file_path, analysis_config)
    
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

@app.get("/download/{task_id}/archive")
async def download_analysis_archive(task_id: str):
    """Download the complete analysis archive as a ZIP file."""
    if task_id not in analysis_tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = analysis_tasks[task_id]
    if task.status != "completed":
        raise HTTPException(status_code=400, detail="Analysis not completed")
    
    # Get the ZIP file path from results
    if not task.results or "zip_path" not in task.results:
        raise HTTPException(status_code=404, detail="Archive not found")
    
    zip_path = Path(task.results["zip_path"])
    if not zip_path.exists():
        raise HTTPException(status_code=404, detail="Archive file not found")
    
    return FileResponse(
        zip_path,
        media_type="application/zip",
        filename=f"serve_analysis_{task_id}.zip"
    )

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
    """Enhanced video processing pipeline with user configurable parameters."""
    print(f"🔍 Starting analysis for task {task_id}")
    try:
        task = analysis_tasks[task_id]
        task.status = "processing"
        task.progress = 0.1
        task.message = "Loading video and initializing analysis..."
        print(f"✅ Task {task_id} initialized with status: {task.status}")
        
        # Step 1: Video Loading and Quality Assessment
        task.progress = 0.2
        task.message = "Assessing video quality..."
        print(f"📊 Assessing video quality for {video_path}")
        video_quality = await asyncio.get_event_loop().run_in_executor(
            executor, assess_video_quality, str(video_path)
        )
        print(f"✅ Video quality assessment complete: {video_quality}")
        
        # Step 2: Video Optimization (if enabled)
        if config.optimize_video:
            task.progress = 0.3
            task.message = "Optimizing video for processing..."
            print(f"🔄 Optimizing video...")
            optimized_path = await asyncio.get_event_loop().run_in_executor(
                executor, optimize_video_for_processing, str(video_path)
            )
            processing_video_path = Path(optimized_path)
        else:
            processing_video_path = video_path
            print(f"⏭️ Skipping video optimization")
        
        # Step 3: Serve Detection
        task.progress = 0.4
        task.message = "Detecting serves in video..."
        print(f"🎾 Starting serve detection...")
        
        # Load video and get pose frames
        print(f"👤 Estimating pose for video...")
        pose_frames = await asyncio.get_event_loop().run_in_executor(
            executor, estimate_pose_video, str(processing_video_path), config.confidence_threshold
        )
        print(f"✅ Pose estimation complete: {len(pose_frames)} frames")
        
        # Detect ball trajectory
        print(f"🏐 Detecting ball trajectory...")
        ball_detections = await asyncio.get_event_loop().run_in_executor(
            executor, detect_ball_trajectory, str(processing_video_path)
        )
        print(f"✅ Ball detection complete: {len(ball_detections)} detections")
        
        # Detect serves with user config
        serve_config = DEFAULT_SERVE_CONFIG.copy()
        serve_config.update({
            "min_serve_duration": config.min_serve_duration,
            "max_serve_duration": config.max_serve_duration,
            "confidence_threshold": config.confidence_threshold
        })
        
        print(f"🎯 Detecting serves with config: {serve_config}")
        serves = await asyncio.get_event_loop().run_in_executor(
            executor, detect_serves, pose_frames, ball_detections, serve_config
        )
        print(f"✅ Serve detection complete: {len(serves)} serves found")
        
        # Step 4: Pose Estimation (if enabled)
        pose_data = None
        if config.include_landmarks:
            task.progress = 0.6
            task.message = "Estimating player pose and landmarks..."
            pose_data = pose_frames  # Already calculated above
            print(f"✅ Landmarks enabled, using existing pose data")
        
        # Step 5: Serve Segmentation
        task.progress = 0.8
        task.message = "Extracting serve segments..."
        print(f"✂️ Extracting serve segments...")
        serve_segments = await asyncio.get_event_loop().run_in_executor(
            executor, extract_serve_segments,
            str(processing_video_path), 
            serves, 
            pose_data,
            config.include_landmarks
        )
        print(f"✅ Serve segmentation complete: {len(serve_segments)} segments")
        
        # Step 6: Generate ZIP Archive
        task.progress = 0.9
        task.message = "Creating output archive..."
        print(f"📦 Creating ZIP archive...")
        zip_path = await asyncio.get_event_loop().run_in_executor(
            executor, create_serve_archive, task_id, serve_segments, config.dict()
        )
        print(f"✅ ZIP archive created: {zip_path}")
        
        # Step 7: Update Results
        task.progress = 1.0
        task.status = "completed"
        task.message = "Analysis completed successfully"
        task.results = {
            "task_id": task_id,
            "total_serves": len(serves),
            "serve_segments": serve_segments,
            "video_quality": video_quality,
            "download_url": f"/api/download/{task_id}/archive",
            "config_used": config.dict(),
            "zip_path": str(zip_path)
        }
        print(f"🎉 Analysis completed successfully for task {task_id}")
        
    except Exception as e:
        print(f"❌ Analysis failed for task {task_id}: {e}")
        import traceback
        traceback.print_exc()
        task.status = "failed"
        task.error = str(e)
        task.message = f"Analysis failed: {str(e)}"

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
