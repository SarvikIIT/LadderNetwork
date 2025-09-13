#!/usr/bin/env python3
"""
Network Ladder Web Application Startup Script
This script handles the complete setup and startup process
"""

import os
import sys
import subprocess
import platform
import webbrowser
import time
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 7):
        print("❌ Error: Python 3.7 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def check_dependencies():
    """Check if required Python packages are installed"""
    required_packages = ['flask', 'flask_cors', 'pandas', 'schemdraw', 'matplotlib']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} is installed")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} is missing")
    
    if missing_packages:
        print(f"\n📦 Installing missing packages: {', '.join(missing_packages)}")
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install'] + missing_packages, check=True)
            print("✅ All packages installed successfully")
        except subprocess.CalledProcessError:
            print("❌ Failed to install packages. Please run: pip install -r requirements.txt")
            return False
    
    return True

def compile_cpp_app():
    """Compile the C++ application"""
    if os.path.exists("app.exe") or os.path.exists("app"):
        print("✅ C++ application already compiled")
        return True
    
    print("🔨 Compiling C++ application...")
    
    # Determine the executable name based on platform
    exe_name = "app.exe" if platform.system() == "Windows" else "app"
    
    # Source files
    source_files = [
        "main.cpp", "Polynomial.cpp", "ContinuedFraction.cpp", 
        "CSVMaker.cpp", "NetworkUtils.cpp"
    ]
    
    # Check if all source files exist
    missing_files = [f for f in source_files if not os.path.exists(f)]
    if missing_files:
        print(f"❌ Missing source files: {missing_files}")
        return False
    
    # Compile command
    if platform.system() == "Windows":
        cmd = ["g++", "-std=c++17", "-O2", "-o", exe_name] + source_files
    else:
        cmd = ["g++", "-std=c++17", "-O2", "-o", exe_name] + source_files
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"✅ C++ application compiled successfully: {exe_name}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Compilation failed: {e.stderr}")
        print("💡 Make sure you have g++ installed and in your PATH")
        return False
    except FileNotFoundError:
        print("❌ g++ compiler not found")
        print("💡 Please install g++ (GCC) compiler")
        return False

def start_webapp():
    """Start the Flask web application"""
    print("\n🚀 Starting Network Ladder Web Application...")
    print("📱 The application will open in your default browser")
    print("🔗 URL: http://localhost:5000")
    print("⏹️  Press Ctrl+C to stop the server")
    print("-" * 50)
    
    # Open browser after a short delay
    def open_browser():
        time.sleep(2)
        webbrowser.open("http://localhost:5000")
    
    import threading
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    # Start the Flask app
    try:
        from app import app
        app.run(debug=False, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n👋 Shutting down Network Ladder Web Application...")
    except Exception as e:
        print(f"❌ Error starting web application: {e}")

def main():
    """Main startup function"""
    print("🔌 Network Ladder Web Application Startup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Check and install dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Compile C++ application
    if not compile_cpp_app():
        print("⚠️  Warning: C++ compilation failed. Some features may not work.")
        print("💡 You can still use the web interface, but network synthesis may fail.")
        response = input("Continue anyway? (y/N): ").lower().strip()
        if response != 'y':
            sys.exit(1)
    
    # Start the web application
    start_webapp()

if __name__ == "__main__":
    main()
