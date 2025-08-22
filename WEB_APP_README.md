# Tennis Serve Analysis Web Application

A modern web application for analyzing tennis serves using AI-powered computer vision. Built with React, FastAPI, and MediaPipe for accurate pose estimation and serve detection.

## 🚀 Features

- **Drag & Drop Video Upload**: Easy video upload with support for MP4, AVI, MOV, and MKV formats
- **Real-time Processing**: Live progress tracking with detailed status updates
- **Configurable Analysis**: Adjustable parameters for confidence thresholds, duration limits, and processing options
- **Player Handedness Support**: Automatic detection for both right and left-handed players
- **Serve Segmentation**: Extract individual serve clips with confidence scoring
- **Results Gallery**: View and download detected serves with detailed metrics
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile devices

## 🏗️ Architecture

### Backend (FastAPI)
- **Framework**: FastAPI with async/await support
- **AI/ML**: MediaPipe for pose estimation, OpenCV for video processing
- **File Handling**: Local file storage with static file serving
- **Background Processing**: ThreadPoolExecutor for non-blocking analysis
- **API Documentation**: Automatic OpenAPI/Swagger documentation

### Frontend (React)
- **Framework**: React 18 with TypeScript
- **State Management**: Zustand for local state, React Query for server state
- **Styling**: Tailwind CSS with custom components
- **UI Components**: Lucide React icons, React Dropzone for file uploads
- **Video Player**: Native HTML5 video with custom controls

## 📋 Prerequisites

- Python 3.11+
- Node.js 18+
- npm or yarn

## 🛠️ Installation

### 1. Install Python Dependencies

```bash
# Install the package with all dependencies
pip install -e .

# Or install manually
pip install fastapi uvicorn python-multipart opencv-python mediapipe numpy pandas
```

### 2. Install Frontend Dependencies

```bash
cd frontend
npm install
```

## 🚀 Running the Application

### Option 1: Separate Backend and Frontend

1. **Start the Backend**:
   ```bash
   python start_web_app.py
   ```
   The API will be available at http://localhost:8000

2. **Start the Frontend**:
   ```bash
   cd frontend
   npm run dev
   ```
   The web app will be available at http://localhost:3000

### Option 2: Using the Startup Script

```bash
# Start backend
python start_web_app.py

# In another terminal, start frontend
cd frontend && npm run dev
```

## 📖 API Documentation

Once the backend is running, you can access:
- **Interactive API Docs**: http://localhost:8000/docs
- **ReDoc Documentation**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 🎯 Usage

### 1. Upload Video
- Drag and drop a tennis serve video or click to browse
- Supported formats: MP4, AVI, MOV, MKV (max 100MB)
- Recommended: Side view of serve motion with good lighting

### 2. Configure Analysis
- **Player Handedness**: Select right or left-handed
- **Confidence Threshold**: Adjust detection sensitivity (0.1-1.0)
- **Duration Limits**: Set min/max serve duration
- **Processing Options**: Enable/disable video optimization and landmarks

### 3. Monitor Processing
- Real-time progress tracking
- Step-by-step status updates
- Estimated completion time

### 4. View Results
- Grid view of detected serves
- Confidence scores and duration metrics
- Download individual serve clips
- Detailed serve analysis

## 🔧 Configuration

### Backend Configuration

The backend can be configured through environment variables:

```bash
# Server settings
HOST=0.0.0.0
PORT=8000

# File storage
UPLOAD_DIR=uploads
OUTPUT_DIR=outputs

# Processing
MAX_WORKERS=2
MAX_FILE_SIZE=104857600  # 100MB
```

### Frontend Configuration

Frontend configuration is in `frontend/vite.config.ts`:

```typescript
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      }
    }
  }
})
```

## 📁 Project Structure

```
serve-ai-analysis/
├── src/serve_ai_analysis/
│   ├── web/
│   │   ├── __init__.py
│   │   └── api.py              # FastAPI backend
│   ├── video/                  # Video processing modules
│   ├── pose/                   # Pose estimation modules
│   └── cli.py                  # Command-line interface
├── frontend/
│   ├── src/
│   │   ├── components/         # React components
│   │   ├── api.ts             # API client
│   │   ├── store.ts           # Zustand store
│   │   ├── types.ts           # TypeScript types
│   │   └── App.tsx            # Main app component
│   ├── package.json
│   └── vite.config.ts
├── start_web_app.py           # Backend startup script
└── WEB_APP_README.md          # This file
```

## 🧪 Testing

### Backend Testing
```bash
# Run backend tests
pytest tests/

# Test specific modules
pytest tests/test_serve_detection.py
```

### Frontend Testing
```bash
cd frontend
npm test
```

## 🚀 Deployment

### Development
- Backend: `python start_web_app.py`
- Frontend: `cd frontend && npm run dev`

### Production
- Backend: Use Gunicorn with uvicorn workers
- Frontend: Build with `npm run build` and serve static files
- Consider using Docker for containerized deployment

## 🔍 Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```bash
   # Check what's using the port
   lsof -i :8000
   # Kill the process or change the port
   ```

2. **Video Upload Fails**
   - Check file size (max 100MB)
   - Verify file format (MP4, AVI, MOV, MKV)
   - Ensure sufficient disk space

3. **Processing Takes Too Long**
   - Reduce video resolution
   - Enable video optimization
   - Check system resources

4. **No Serves Detected**
   - Lower confidence threshold
   - Adjust duration limits
   - Ensure good video quality and lighting

### Logs

Backend logs are displayed in the terminal. For more detailed logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **MediaPipe**: Google's pose estimation library
- **OpenCV**: Computer vision library
- **FastAPI**: Modern Python web framework
- **React**: JavaScript UI library
- **Tailwind CSS**: Utility-first CSS framework

---

**Version**: 2.0.0  
**Last Updated**: January 2025
