#!/bin/bash

# Tennis Serve Analysis Web Application Setup Script

echo "🎾 Setting up Tennis Serve Analysis Web Application..."
echo "=================================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.11+ first."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18+ first."
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed. Please install npm first."
    exit 1
fi

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ uv is not installed. Please install uv first."
    exit 1
fi

echo "✅ Prerequisites check passed"

# Install Python dependencies
echo "📦 Installing Python dependencies..."
uv pip install -e . || {
    echo "❌ Failed to install Python dependencies"
    exit 1
}

# Install frontend dependencies
echo "📦 Installing frontend dependencies..."
cd frontend
npm install || {
    echo "❌ Failed to install frontend dependencies"
    exit 1
}
cd ..

echo "✅ All dependencies installed successfully!"
echo ""
echo "🚀 To start the application:"
echo ""
echo "1. Start the backend:"
echo "   python start_web_app.py"
echo ""
echo "2. In another terminal, start the frontend:"
echo "   cd frontend && npm run dev"
echo ""
echo "3. Open your browser to: http://localhost:3000"
echo ""
echo "📖 API documentation will be available at: http://localhost:8000/docs"
echo ""
echo "�� Happy analyzing!"
