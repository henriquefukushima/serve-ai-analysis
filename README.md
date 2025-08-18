# Tennis Serve AI Analysis

Advanced tennis serve biomechanics analysis using computer vision and AI. This tool analyzes tennis serves from video input to provide detailed biomechanical insights, generate interactive dashboards, and create comprehensive PDF reports for athletes and coaches.

## Features

- **Video Processing**: Automatic serve segmentation from tennis videos
- **Pose Estimation**: 2D and 3D pose estimation using state-of-the-art AI models
- **Biomechanical Analysis**: Calculate joint angles, velocities, timing, and other key metrics
- **Benchmark Comparison**: Compare athlete performance against professional benchmarks
- **Interactive Dashboard**: Web-based visualization of analysis results
- **PDF Reports**: Comprehensive reports for athletes and coaches

## Installation

### Prerequisites

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) (recommended) or pip

### Quick Start

```bash
# Clone the repository
git clone <your-repo-url>
cd serve-ai-analysis

# Install dependencies using uv
uv sync

# Initialize the project
serve-ai init
```

### Alternative Installation with pip

```bash
pip install -e .
```

## Usage

### Command Line Interface

The tool provides a comprehensive CLI with multiple commands for different stages of analysis:

#### 1. Initialize Project

```bash
serve-ai init --output-dir ./my-analysis
```

Creates the necessary directory structure for your analysis.

#### 2. Complete Analysis Pipeline

```bash
serve-ai analyze video.mp4 \
    --output-dir ./results \
    --confidence 0.7 \
    --min-duration 1.5 \
    --max-duration 4.0 \
    --3d \
    --benchmark ./benchmarks/pro-level.json \
    --dashboard \
    --pdf
```

This runs the complete analysis pipeline:
- Segments serves from the video
- Estimates poses (2D or 3D)
- Calculates biomechanical metrics
- Compares with benchmarks
- Generates dashboard and PDF report

#### 3. Individual Pipeline Steps

You can also run individual steps:

**Serve Segmentation:**
```bash
serve-ai segment video.mp4 --min-duration 1.5 --max-duration 4.0
```

**Pose Estimation:**
```bash
serve-ai pose video.mp4 --confidence 0.7 --3d --calibration camera_calib.json
```

**Biomechanical Analysis:**
```bash
serve-ai metrics poses.json --benchmark benchmarks.json
```

**Dashboard Generation:**
```bash
serve-ai dashboard metrics.json --port 8050
```

**PDF Report Generation:**
```bash
serve-ai report metrics.json --athlete "John Doe"
```

### Configuration Options

#### Analysis Parameters

- `--confidence`: Pose detection confidence threshold (0.0-1.0, default: 0.5)
- `--min-duration`: Minimum serve duration in seconds (default: 1.0)
- `--max-duration`: Maximum serve duration in seconds (default: 5.0)
- `--3d`: Enable 3D pose estimation (requires camera calibration)
- `--calibration`: Path to camera calibration file
- `--benchmark`: Path to benchmark data file

#### Output Options

- `--output-dir`: Output directory (default: "runs")
- `--dashboard/--no-dashboard`: Generate interactive dashboard (default: enabled)
- `--pdf/--no-pdf`: Generate PDF report (default: enabled)
- `--port`: Dashboard port (default: 8050)

## Output Structure

After running the analysis, you'll find the following structure in your output directory:

```
runs/
├── videos/          # Processed video segments
├── segments/        # Serve segment metadata
├── poses/          # Pose estimation data
├── metrics/        # Biomechanical metrics
├── dashboards/     # Interactive dashboard files
└── reports/        # PDF reports
```

## Biomechanical Metrics

The analysis calculates various biomechanical metrics including:

### Joint Angles
- Shoulder abduction/adduction
- Elbow flexion/extension
- Wrist pronation/supination
- Hip flexion/extension
- Knee flexion/extension

### Timing Metrics
- Ball toss height and timing
- Contact point timing
- Follow-through duration
- Overall serve duration

### Velocity Metrics
- Racket head speed
- Joint angular velocities
- Center of mass velocity

### Performance Metrics
- Serve consistency
- Power generation efficiency
- Technique quality score

## Benchmark Data

The tool can compare athlete performance against professional benchmarks. Benchmark data should be provided in JSON format with the following structure:

```json
{
  "serve_metrics": {
    "ball_toss_height": {"mean": 2.5, "std": 0.3, "unit": "m"},
    "contact_point_height": {"mean": 2.8, "std": 0.2, "unit": "m"},
    "serve_duration": {"mean": 2.8, "std": 0.4, "unit": "s"},
    "racket_speed": {"mean": 45.0, "std": 5.0, "unit": "m/s"}
  },
  "joint_angles": {
    "shoulder_abduction": {"mean": 90, "std": 10, "unit": "degrees"},
    "elbow_flexion": {"mean": 120, "std": 15, "unit": "degrees"}
  }
}
```

## Dashboard Features

The interactive dashboard provides:

- **Video playback** with synchronized pose overlay
- **Metric visualizations** with interactive charts
- **Benchmark comparisons** with percentile rankings
- **Serve-by-serve analysis** with detailed breakdowns
- **Export capabilities** for further analysis

## PDF Report Features

The PDF report includes:

- **Executive summary** with key findings
- **Detailed metrics** with visualizations
- **Benchmark comparisons** and recommendations
- **Technical analysis** with biomechanical insights
- **Actionable recommendations** for improvement

## Development

### Setup Development Environment

```bash
# Install with development dependencies
uv sync --extra dev

# Run tests
pytest

# Format code
black src/
isort src/

# Type checking
mypy src/
```

### Project Structure

```
serve-ai-analysis/
├── src/
│   └── serve_ai_analysis/
│       ├── __init__.py
│       ├── cli.py              # Command line interface
│       ├── video/              # Video processing modules
│       ├── pose/               # Pose estimation modules
│       ├── metrics/            # Biomechanical analysis
│       ├── dashboard/          # Dashboard generation
│       └── reports/            # PDF report generation
├── tests/                      # Test files
├── benchmarks/                 # Benchmark data
├── examples/                   # Example videos and data
└── docs/                       # Documentation
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

MIT License

Copyright (c) 2025 Henrique A. Fukushima

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

## Citation

If you use this tool in your research, please cite:

```bibtex
@software{serve_ai_analysis,
  title={Tennis Serve AI Analysis},
  author={Henrique A. Fukushima},
  year={2025},
  url={https://github.com/henriquefukushima/serve-ai-analysis}
}
```

## Support

For questions, issues, or feature requests, please open an issue on GitHub or contact [henrique_fukushima@usp.br].
