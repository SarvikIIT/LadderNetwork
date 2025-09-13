#!/usr/bin/env python3
"""
Network Ladder Project Reorganization Script
This script helps organize the project files into the recommended structure
"""

import os
import shutil
from pathlib import Path

def create_directories():
    """Create the recommended directory structure"""
    directories = [
        'api',
        'src', 
        'web',
        'static/css',
        'static/js', 
        'static/images',
        'templates',
        'docs',
        'build'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {directory}")

def move_files():
    """Move files to their appropriate locations"""
    file_moves = {
        # C++ source files to src/
        'main.cpp': 'src/main.cpp',
        'Polynomial.cpp': 'src/Polynomial.cpp',
        'Polynomial.hpp': 'src/Polynomial.hpp',
        'ContinuedFraction.cpp': 'src/ContinuedFraction.cpp',
        'ContinuedFraction.hpp': 'src/ContinuedFraction.hpp',
        'NetworkUtils.cpp': 'src/NetworkUtils.cpp',
        'NetworkUtils.hpp': 'src/NetworkUtils.hpp',
        'CSVMaker.cpp': 'src/CSVMaker.cpp',
        'CSVMaker.hpp': 'src/CSVMaker.hpp',
        
        # Web files to web/
        'app.py': 'web/app.py',
        'index.html': 'web/index.html',
        'start_webapp.py': 'web/start_webapp.py',
        'network.py': 'web/network.py',
        
        # Documentation to docs/
        'deploy_vercel.md': 'docs/deploy_vercel.md',
        'deploy_heroku.md': 'docs/deploy_heroku.md',
        'PROJECT_STRUCTURE.md': 'docs/PROJECT_STRUCTURE.md',
        
        # Keep these in root
        'CMakeLists.txt': 'CMakeLists.txt',
        'Dockerfile': 'Dockerfile',
        'docker-compose.yml': 'docker-compose.yml',
        'vercel.json': 'vercel.json',
        'Procfile': 'Procfile',
        'runtime.txt': 'runtime.txt',
        'requirements.txt': 'requirements.txt',
        'README.md': 'README.md',
        '.gitignore': '.gitignore',
        '.dockerignore': '.dockerignore'
    }
    
    for source, destination in file_moves.items():
        if os.path.exists(source):
            # Create destination directory if it doesn't exist
            dest_dir = os.path.dirname(destination)
            if dest_dir:  # Only create directory if there is one
                os.makedirs(dest_dir, exist_ok=True)
            
            # Move the file
            shutil.move(source, destination)
            print(f"✅ Moved {source} → {destination}")
        else:
            print(f"⚠️  File not found: {source}")

def create_gitignore():
    """Create a comprehensive .gitignore file"""
    gitignore_content = """# Build artifacts
build/
out/
*.exe
*.obj
*.o
*.so
*.dylib
*.dll

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.venv/
ENV/
env.bak/
venv.bak/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Logs
*.log
logs/

# Temporary files
*.tmp
*.temp
*.csv
*.png

# Environment variables
.env
.env.local
.env.development.local
.env.test.local
.env.production.local

# Node modules (if using any JS tools)
node_modules/

# Vercel
.vercel

# Heroku
.heroku/
"""
    
    with open('.gitignore', 'w') as f:
        f.write(gitignore_content)
    print("✅ Created .gitignore file")

def update_cmake_paths():
    """Update CMakeLists.txt to use new src/ directory"""
    cmake_content = """cmake_minimum_required(VERSION 3.15)
project(NetworkLadder CXX)
set(CMAKE_CXX_STANDARD 17)

# Set source directory
set(SOURCES_DIR src)

add_library(network_core
  ${SOURCES_DIR}/Polynomial.cpp
  ${SOURCES_DIR}/ContinuedFraction.cpp
  ${SOURCES_DIR}/NetworkUtils.cpp
  ${SOURCES_DIR}/CSVMaker.cpp
)

target_include_directories(network_core PUBLIC ${SOURCES_DIR})

add_executable(app ${SOURCES_DIR}/main.cpp)
target_link_libraries(app PRIVATE network_core)

# Tests (GoogleTest)
option(BUILD_TESTING "Build tests" ON)
if(BUILD_TESTING)
  enable_testing()
  find_package(GTest REQUIRED)
  add_executable(network_tests tests/test_network.cpp)
  target_link_libraries(network_tests PRIVATE network_core GTest::gtest GTest::gtest_main)
  add_test(NAME network_tests COMMAND network_tests)
endif()
"""
    
    with open('CMakeLists.txt', 'w') as f:
        f.write(cmake_content)
    print("✅ Updated CMakeLists.txt for new structure")

def main():
    """Main reorganization function"""
    print("🔧 Network Ladder Project Reorganization")
    print("=" * 50)
    
    print("\n📁 Creating directory structure...")
    create_directories()
    
    print("\n📦 Moving files to appropriate locations...")
    move_files()
    
    print("\n📝 Creating .gitignore...")
    create_gitignore()
    
    print("\n🔧 Updating build configuration...")
    update_cmake_paths()
    
    print("\n✅ Reorganization complete!")
    print("\n📋 Next steps:")
    print("1. Review the moved files")
    print("2. Test the build: mkdir build && cd build && cmake .. && make")
    print("3. Test the web app: python web/app.py")
    print("4. Deploy to Vercel: vercel")
    print("\n📚 See docs/PROJECT_STRUCTURE.md for full documentation")

if __name__ == "__main__":
    main()
