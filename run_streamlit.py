#!/usr/bin/env python3
"""
Python launcher for Vietnamese Traffic Law QA Streamlit UI.
Alternative to the bash script for cross-platform compatibility.
"""

import subprocess
import sys
from pathlib import Path

def main():
    """Launch Streamlit app."""
    
    # Get project root
    project_root = Path(__file__).parent
    app_path = project_root / "src" / "traffic_law_qa" / "ui" / "streamlit_app.py"
    
    # Check if app file exists
    if not app_path.exists():
        print(f"❌ Error: Streamlit app not found at {app_path}")
        sys.exit(1)
    
    print("🚦 Starting Vietnamese Traffic Law QA System...")
    print("=" * 60)
    print()
    print("System: Neo4j-based Hybrid Search (Vector + BM25)")
    print("UI: Streamlit Web Interface")
    print()
    print("Once started, the app will be available at:")
    print("  🌐 http://localhost:9001")
    print()
    print("=" * 60)
    print()
    
    try:
        # Launch Streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run",
            str(app_path),
            "--server.port=9001",
            "--server.address=localhost"
        ], check=True)
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down gracefully...")
        sys.exit(0)
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error launching Streamlit: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print("\n❌ Error: Streamlit is not installed.")
        print("Please install it with: pip install streamlit")
        sys.exit(1)

if __name__ == "__main__":
    main()
