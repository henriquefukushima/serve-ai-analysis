#!/usr/bin/env python3
"""
Startup script for the Tennis Serve Analysis Web Application.

This script starts the FastAPI backend server for the web application.
"""

import uvicorn
import sys
from pathlib import Path

# Add the src directory to the Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

if __name__ == "__main__":
    print("🎾 Starting Tennis Serve Analysis Web Application...")
    print("📡 Backend API will be available at: http://localhost:8000")
    print("📖 API Documentation: http://localhost:8000/docs")
    print("🔧 Frontend should be started separately with: cd frontend && npm run dev")
    print("🌐 Full application will be available at: http://localhost:3000")
    print()
    
    uvicorn.run(
        "serve_ai_analysis.web.api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
