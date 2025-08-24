# Quick Start Guide - Video Processing Pipeline

## 🚀 Getting Started

This guide will help you test the new video processing pipeline that processes uploaded videos and returns ZIP folders containing segmented serves.

## 📋 Prerequisites

1. **Python Environment**: Ensure you have the virtual environment activated
2. **Dependencies**: All dependencies should be installed via `uv`
3. **Test Video**: Have a tennis serve video file ready (MP4, AVI, MOV, MKV, or WebM)

## 🏃‍♂️ Quick Test

### 1. Test the Backend Pipeline

```bash
# Navigate to the project directory
cd serve-ai-analysis

# Run the test script to verify the pipeline works
uv run python test_video_processing.py
```

Expected output:
```
🚀 Starting video processing pipeline tests...

🧪 Testing AnalysisRequest model...
✅ Default config created: 0.7
✅ Custom config created: 0.8
✅ Invalid config properly rejected: 1 validation error for AnalysisRequest

🧪 Testing serve segmentation...
✅ Mock serve data created: 2 serves

🧪 Testing report generation...
✅ HTML report generated: 3493 characters
✅ README generated: 1397 characters

🧪 Testing archive creation...
✅ Created serve analysis archive: outputs/test_task_123/serve_analysis_test_task_123.zip
✅ Archive created successfully: outputs/test_task_123/serve_analysis_test_task_123.zip
✅ Archive exists: True

🎉 All tests passed! Video processing pipeline is working correctly.
```

### 2. Start the Backend Server

```bash
# Start the FastAPI backend server
uv run python start_web_app.py
```

The server will start on `http://localhost:8000`

### 3. Start the Frontend

```bash
# In a new terminal, navigate to the frontend directory
cd frontend

# Install dependencies (if not already done)
npm install

# Start the development server
npm run dev
```

The frontend will start on `http://localhost:3000`

## 🎯 Testing the Full Pipeline

### Step 1: Upload a Video

1. Open `http://localhost:3000` in your browser
2. Click on the upload area or drag a tennis serve video file
3. The file should be accepted (MP4, AVI, MOV, MKV, WebM formats supported)

### Step 2: Configure Analysis Settings

1. Click the "Settings" button to expand the configuration panel
2. Try the preset configurations:
   - **Quick Analysis**: Fast processing with basic output
   - **Detailed Analysis**: Comprehensive analysis with landmarks
   - **Professional Analysis**: High-quality output for coaching
3. Or customize individual parameters:
   - Confidence threshold (0.1-1.0)
   - Serve duration limits
   - Video quality settings
   - Landmark visualization options

### Step 3: Monitor Processing

1. After uploading, you'll see the enhanced processing status
2. Watch the step-by-step progress:
   - Video quality assessment
   - Video optimization
   - Serve detection
   - Pose estimation
   - Serve segmentation
   - Creating output archive
3. Each step shows detailed status messages

### Step 4: Download Results

1. When processing completes, you'll see the "Analysis Complete!" screen
2. The interface shows:
   - Total serves detected
   - Average confidence score
   - Download readiness status
3. Click "Download Serve Analysis" to get the ZIP file

## 📦 ZIP Archive Contents

The downloaded ZIP file contains:

```
serve_analysis_{task_id}.zip
├── serves/
│   ├── serve_001.mp4    # Individual serve video clips
│   ├── serve_002.mp4
│   └── ...
├── analysis_report.html # Detailed HTML report with statistics
├── config_summary.json  # Analysis configuration and metadata
└── README.md           # Usage instructions
```

## 🔧 Configuration Options

### Video Quality
- **Low**: Fast processing, reduced quality
- **Medium**: Balanced speed and quality
- **High**: Better quality, slower processing
- **Original**: No quality changes

### Landmark Style
- **Points only**: Just pose keypoints
- **Skeleton lines**: Connected pose skeleton
- **Both**: Points and skeleton lines

### Output Format
- **MP4**: Recommended, widely compatible
- **AVI**: Alternative format
- **MOV**: Apple QuickTime format

### Compression Level
- **1-3**: High quality, larger files
- **4-7**: Balanced quality and size
- **8-10**: Smaller files, lower quality

## 🐛 Troubleshooting

### Common Issues

1. **Upload Fails**
   - Check file format (MP4, AVI, MOV, MKV, WebM)
   - Ensure file size is under 500MB
   - Try a different browser

2. **Processing Stuck**
   - Check browser console for errors
   - Verify backend server is running
   - Try refreshing the page

3. **Download Fails**
   - Check if processing completed successfully
   - Verify ZIP file was created in `outputs/` directory
   - Try downloading again

### Debug Information

```bash
# Check backend logs
uv run python start_web_app.py

# Check frontend build
cd frontend && npm run build

# Run backend tests
uv run python test_video_processing.py
```

## 📊 Expected Results

### Processing Time
- **Quick Analysis**: 2-5 minutes for 10-minute video
- **Detailed Analysis**: 5-10 minutes for 10-minute video
- **Professional Analysis**: 10-15 minutes for 10-minute video

### Output Quality
- **Serve Detection**: 90%+ accuracy with proper configuration
- **Video Quality**: Maintains original quality or optimized based on settings
- **Archive Size**: 50-200MB depending on video length and settings

## 🎉 Success Indicators

✅ Video uploads successfully  
✅ Processing shows step-by-step progress  
✅ Analysis completes without errors  
✅ ZIP file downloads successfully  
✅ Archive contains all expected files  
✅ HTML report opens and displays correctly  

## 📞 Support

If you encounter issues:

1. Check the browser console for error messages
2. Verify all services are running (backend + frontend)
3. Test with a different video file
4. Review the implementation summary in `IMPLEMENTATION_SUMMARY.md`

---

**Next Steps**: Once testing is complete, the system is ready for production deployment and can be extended with advanced features like landmark visualization and AI coaching.
