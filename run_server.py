#!/usr/bin/env python3
"""
Script to run the EMS Copilot FastAPI server with proper Python path setup.
"""
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
project_dir = Path(__file__).parent
load_dotenv(dotenv_path=project_dir / ".env", override=True)

# Add the backend/src directory to Python path
backend_src_dir = project_dir / "backend" / "src"
sys.path.insert(0, str(backend_src_dir))

# Now we can import the app
from ems_copilot.infrastructure.api.main import app

if __name__ == "__main__":
    import uvicorn
    print(f"🚀 Starting EMS Copilot server...")
    print(f"📁 Project directory: {project_dir}")
    print(f"📁 Backend src directory: {backend_src_dir}")
    print(f"🐍 Python path: {sys.path[:3]}...")
    
    uvicorn.run(
        "run_server:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        reload_dirs=[str(project_dir / "backend")],
        log_level="info"
    ) 