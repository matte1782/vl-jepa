# Quick Start

Get Lecture Mind running in under 5 minutes.

## Option 1: Cloud Demo (Instant)

No installation required:

1. Go to [lecture-mind.onrender.com](https://lecture-mind.onrender.com)
2. Click "Upload Video"
3. Select a video file (MP4, WebM, AVI, MOV, or MKV)
4. Wait for processing
5. Explore the results!

!!! warning "Demo Limitations"
    The cloud demo uses placeholder processing due to free tier memory limits.
    For full AI functionality, use the local installation.

---

## Option 2: Local Installation (Full Features)

### Prerequisites

- Python 3.10+
- FFmpeg
- Git

### Install

```bash
# Clone the repository
git clone https://github.com/matte1782/lecture-mind.git
cd lecture-mind

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install with all dependencies
pip install -e ".[all]"
```

### Run

```bash
uvicorn vl_jepa.api.main:app --port 8000
```

Open [http://localhost:8000](http://localhost:8000) in your browser.

---

## What's Next?

- [Local Setup Guide](local-setup.md) - Detailed installation instructions
- [Web Interface Guide](guide/web-ui.md) - How to use the web UI
- [API Reference](guide/api.md) - REST API documentation
- [Architecture](ARCHITECTURE.md) - Technical details
