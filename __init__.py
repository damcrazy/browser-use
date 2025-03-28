import os
import sys
from pathlib import Path

def setup_environment():
    """Setup environment variables and dependencies"""
    # Add the current directory to Python path
    current_dir = Path(__file__).parent
    sys.path.append(str(current_dir))
    
    # Create static directory if it doesn't exist
    static_dir = current_dir / "static"
    static_dir.mkdir(exist_ok=True)
    
    # Create logs directory if it doesn't exist
    logs_dir = current_dir / "logs"
    logs_dir.mkdir(exist_ok=True)

def check_dependencies():
    """Check if all required dependencies are installed"""
    try:
        import fastapi
        import uvicorn
        import websockets
        import browser_use
        import langchain_openai
        import PIL
        return True
    except ImportError as e:
        print(f"Missing dependency: {e}")
        print("Please install dependencies using: pip install -r requirements.txt")
        return False

# Run setup when module is imported
setup_environment() 