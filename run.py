"""
MedBotX - Development Server Launcher
Developed by Bhaskar Shivaji Kumbhar

Usage:
    python run.py           # Start API server
    python run.py frontend  # Start Streamlit frontend
    python run.py both      # Start both (requires two terminals or background processes)
"""
import sys
import subprocess


def start_api():
    print("🏥 Starting MedBotX API Server...")
    print("   Developed by Bhaskar Shivaji Kumbhar")
    print("   Docs: http://localhost:8000/docs\n")
    subprocess.run(
        ["uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"],
        check=True,
    )


def start_frontend():
    print("🖥️  Starting MedBotX Streamlit Frontend...")
    print("   Developed by Bhaskar Shivaji Kumbhar")
    print("   URL: http://localhost:8501\n")
    subprocess.run(
        ["streamlit", "run", "frontend/app.py", "--server.port=8501"],
        check=True,
    )


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "api"
    if mode == "frontend":
        start_frontend()
    elif mode == "both":
        print("Run 'python run.py' in one terminal and 'python run.py frontend' in another.")
    else:
        start_api()
