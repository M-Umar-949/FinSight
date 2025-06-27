#!/usr/bin/env python3
"""
FinSight Application Startup Script
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    """Main startup function"""
    print("🚀 FinSight - Fintech Intelligence Agent")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("main.py").exists():
        print("❌ Error: Please run this script from the FinSight project root directory")
        sys.exit(1)
    
    # Check if requirements are installed
    try:
        import streamlit
        import requests
        import aiohttp
        print("✅ Dependencies check passed")
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please run: pip install -r requirements.txt")
        sys.exit(1)
    
    # Check Ollama connection
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            print("✅ Ollama connection successful")
        else:
            print("⚠️  Ollama may not be running. Please start Ollama first.")
    except:
        print("⚠️  Cannot connect to Ollama. Please ensure Ollama is running on localhost:11434")
    
    print("\n🎯 Choose your interface:")
    print("1. Web Interface (Streamlit)")
    print("2. CLI Interface")
    print("3. Test Intent Detection")
    print("4. Exit")
    
    choice = input("\nEnter your choice (1-4): ").strip()
    
    if choice == "1":
        print("\n🌐 Starting web interface...")
        print("📱 Open your browser to: http://localhost:8501")
        print("⏹️  Press Ctrl+C to stop the server")
        subprocess.run([sys.executable, "-m", "streamlit", "run", "frontend/app.py", "--server.port", "8501"])
    
    elif choice == "2":
        print("\n💻 Starting CLI interface...")
        subprocess.run([sys.executable, "main.py"])
    
    elif choice == "3":
        print("\n🧪 Running intent detection test...")
        subprocess.run([sys.executable, "test_intent.py"])
    
    elif choice == "4":
        print("👋 Goodbye!")
        sys.exit(0)
    
    else:
        print("❌ Invalid choice. Please select 1-4.")
        sys.exit(1)

if __name__ == "__main__":
    main() 