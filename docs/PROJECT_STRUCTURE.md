# 📁 Network Ladder - Project Structure

## Recommended Folder Organization

```
network-ladder/
├── 📁 api/                    # Serverless API (Vercel)
│   └── 📄 index.py           # Main API endpoint
├── 📁 src/                    # C++ source code
│   ├── 📄 main.cpp           # Main C++ application
│   ├── 📄 Polynomial.cpp     # Polynomial arithmetic
│   ├── 📄 Polynomial.hpp     # Polynomial header
│   ├── 📄 ContinuedFraction.cpp
│   ├── 📄 ContinuedFraction.hpp
│   ├── 📄 NetworkUtils.cpp
│   ├── 📄 NetworkUtils.hpp
│   ├── 📄 CSVMaker.cpp
│   └── 📄 CSVMaker.hpp
├── 📁 web/                    # Web application files
│   ├── 📄 app.py             # Flask web server
│   ├── 📄 index.html         # Frontend interface
│   └── 📄 start_webapp.py    # Startup script
├── 📁 static/                 # Static web assets
│   ├── 📁 css/
│   ├── 📁 js/
│   └── 📁 images/
├── 📁 templates/              # HTML templates (if using Flask templates)
├── 📁 tests/                  # Test files
│   └── 📄 test_network.cpp
├── 📁 docs/                   # Documentation
│   ├── 📄 deploy_vercel.md
│   ├── 📄 deploy_heroku.md
│   └── 📄 PROJECT_STRUCTURE.md
├── 📁 build/                  # Build artifacts
├── 📄 .gitignore
├── 📄 .dockerignore
├── 📄 CMakeLists.txt
├── 📄 Dockerfile
├── 📄 docker-compose.yml
├── 📄 vercel.json            # Vercel configuration
├── 📄 Procfile               # Heroku configuration
├── 📄 runtime.txt            # Python runtime version
├── 📄 requirements.txt       # Python dependencies
└── 📄 README.md
```

## File Organization by Purpose

### 🌐 Web Deployment Files
- `api/index.py` - Vercel serverless function
- `web/app.py` - Flask web server
- `web/index.html` - Frontend interface
- `vercel.json` - Vercel configuration
- `Procfile` - Heroku configuration

### 🔧 C++ Core Files
- `src/main.cpp` - Main application
- `src/*.cpp` - Implementation files
- `src/*.hpp` - Header files
- `CMakeLists.txt` - CMake build configuration

### 🐳 Containerization
- `Dockerfile` - Docker image definition
- `docker-compose.yml` - Multi-container setup
- `.dockerignore` - Docker ignore patterns

### 📚 Documentation
- `README.md` - Main documentation
- `docs/deploy_*.md` - Deployment guides
- `PROJECT_STRUCTURE.md` - This file

### 🧪 Testing
- `tests/` - All test files
- `test_network.cpp` - C++ unit tests

## Deployment Options

### Option 1: Vercel (Recommended for Web)
- **Best for**: Web applications, serverless
- **Files needed**: `api/index.py`, `vercel.json`, `requirements.txt`
- **Pros**: Free, fast, auto-deploy from Git
- **Cons**: Serverless limitations

### Option 2: Heroku
- **Best for**: Full-stack applications
- **Files needed**: `web/app.py`, `Procfile`, `requirements.txt`
- **Pros**: Easy deployment, add-ons
- **Cons**: Paid after free tier

### Option 3: Docker
- **Best for**: Self-hosting, VPS
- **Files needed**: `Dockerfile`, `docker-compose.yml`
- **Pros**: Consistent environment, portable
- **Cons**: Requires Docker knowledge

### Option 4: Traditional VPS
- **Best for**: Full control, custom setup
- **Files needed**: All source files
- **Pros**: Complete control, custom configuration
- **Cons**: Manual setup, maintenance

## Quick Start Commands

### Local Development
```bash
# Run web app locally
python web/app.py

# Or use startup script
python web/start_webapp.py

# Run C++ app directly
g++ -std=c++17 -O2 -o app src/*.cpp
./app
```

### Deploy to Vercel
```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
vercel

# Or connect GitHub repo in Vercel dashboard
```

### Deploy to Heroku
```bash
# Install Heroku CLI
# Login and create app
heroku create your-app-name

# Deploy
git push heroku main
```

### Docker Deployment
```bash
# Build image
docker build -t network-ladder .

# Run container
docker run -p 5000:5000 network-ladder

# Or use docker-compose
docker-compose up
```

## Environment Variables

### Vercel
- `PYTHONPATH`: `.`
- `FLASK_ENV`: `production`

### Heroku
- `FLASK_ENV`: `production`
- `PYTHONPATH`: `.`

### Docker
- `FLASK_ENV`: `production`
- `PORT`: `5000`

## Build Commands

### C++ Compilation
```bash
# Basic compilation
g++ -std=c++17 -O2 -o app src/*.cpp

# With CMake
mkdir build && cd build
cmake ..
make
```

### Python Dependencies
```bash
# Install requirements
pip install -r requirements.txt

# Or create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

## Git Workflow

### Main Branches
- `main` - Production-ready code
- `develop` - Development branch
- `feature/*` - Feature branches

### Deployment
- `main` branch auto-deploys to production
- `develop` branch deploys to staging
- Feature branches create preview deployments

## Maintenance

### Regular Tasks
- Update dependencies
- Monitor performance
- Check logs
- Backup data (if applicable)

### Security
- Keep dependencies updated
- Use environment variables for secrets
- Enable HTTPS
- Regular security audits
