import sys
import os
from pathlib import Path

# Get the current directory (backend/dev)
curr_dir = Path(os.getcwd())
# Go up to backend directory
backend_dir = curr_dir.parent
# Add the src directory to Python path
src_dir = backend_dir / "src"
sys.path.insert(0, str(src_dir))

print(f"Added to sys.path: {src_dir}")
print(f"Current sys.path: {sys.path}")

# Now try to import
try:
    from ems_copilot.domain.services.gps_agent import GPSAgent
    print("✅ Successfully imported GPSAgent")
except ImportError as e:
    print(f"❌ Import failed: {e}") 