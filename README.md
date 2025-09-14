# 🔌 Network Ladder

A C++ and Python tool for synthesizing electrical ladder networks from rational transfer functions using continued fraction expansion.

[![C++](https://img.shields.io/badge/C%2B%2B-17-blue.svg)](https://en.cppreference.com/w/cpp/17)
[![Python](https://img.shields.io/badge/Python-3.7+-green.svg)](https://www.python.org/downloads/)
[![CMake](https://img.shields.io/badge/CMake-3.15+-red.svg)](https://cmake.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 📋 Overview

This project converts rational transfer functions into equivalent electrical ladder networks through continued fraction expansion. It's particularly useful for:

- **Filter Design**: Synthesizing passive LC ladder filters
- **Network Analysis**: Understanding the relationship between transfer functions and physical circuits
- **Educational Purposes**: Visualizing how mathematical functions map to electrical components

### What it does

1. **Input**: A rational transfer function H(s) = N(s)/D(s) where N(s) and D(s) are polynomials
2. **Process**: Converts the transfer function to a continued fraction expansion
3. **Output**: Generates a ladder network with series impedances (Z) and shunt admittances (Y)
4. **Visualization**: Creates a schematic diagram of the resulting electrical network

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Polynomial    │    │  Continued       │    │   Network       │
│   Arithmetic    │───▶│  Fraction        │───▶│   Synthesis     │
│                 │    │  Expansion       │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                         │
                                                         ▼
                                                ┌─────────────────┐
                                                │   Schematic     │
                                                │   Generation    │
                                                │   (Python)      │
                                                └─────────────────┘
```

## 🎓 Professor’s Guide: How the System Works

This is a brief, high-signal overview designed for fast review.

- **Goal**: Given a rational driving-point impedance \( Z(s) = \dfrac{N(s)}{D(s)} \), synthesize an equivalent passive ladder network (Cauer form) and render its schematic.
- **Why two languages?** C++ does the heavy algebra (fast polynomial Euclidean algorithm and tokenization). Python/Flask provides the web API and draws the circuit (Schemdraw/Matplotlib).
- **UI**: A single-page app (`templates/index.html`) with MathJax previews, expression or coefficient inputs, and a dark-mode toggle.

### End-to-End Flow
1. User enters \(N(s), D(s)\) as either expressions (e.g., `s^2 + 3s + 2`) or coefficient tables.
2. Frontend posts JSON to `POST /api/process` with two arrays: `numerator`, `denominator` (ascending powers).
3. Backend (`web/app.py`):
   - Trims trailing zeros for numeric stability, handles trivial cases (constant, `s`, `1/s`).
   - Launches the C++ core (`app`/`app.exe`) via `subprocess` and streams coefficients.
4. C++ core (`src/*.cpp`):
   - Computes the polynomial continued fraction via Euclidean division.
   - Alternates quotient polynomials into series impedances (Z) and shunt admittances (Y).
   - Emits validated Z/Y token lists.
5. Python renderer: maps tokens to Schemdraw primitives and generates a PNG schematic.
6. API Response: `{ Z: [...], Y: [...], image: <base64-png> }` is returned to the UI.

### File Map (key responsibilities)
- `web/app.py`: Flask routes (`/`, `/api/process`, `/api/health`), C++ invocation, image encoding, edge-case handling.
- `templates/index.html`: UI, MathJax rendering, inputs, live previews, microinteractions, dark-mode toggle.
- `src/Polynomial.*`: basic polynomial arithmetic and division.
- `src/ContinuedFraction.*`: polynomial Euclidean algorithm → continued fraction parts.
- `src/NetworkUtils.*`: maps quotient polynomials to Z/Y tokens; sanity checks.
- `wsgi.py`: exposes `app` for Gunicorn (production).
- `Dockerfile`, `docker-compose.yml`: multi-stage build (C++ → Python 3.11 slim) and service runtime (Gunicorn).

### Mathematical Summary (Cauer form)
- Compute the continued fraction of \( Z(s)=\dfrac{N(s)}{D(s)} \) by repeated polynomial division: \( N = Q_0 D + R_1;\; D = Q_1 R_1 + R_2;\; \ldots \)
- Even-indexed \(Q_{0}, Q_{2}, ...\) map to series impedances (Z); odd-indexed \(Q_{1}, Q_{3}, ...\) map to shunt admittances (Y).
- Special cases handled explicitly: constants (resistor), `s` (inductor), `1/s` (capacitor).

### One‑Minute Demo
1) Local run: `python web/app.py` → open `http://localhost:5000`.
2) Example: choose “RC: (s+1)/s” → press “Generate Network”.
3) Observe MathJax preview, Z/Y token arrays, and the rendered ladder schematic.


## 🚀 Quick Start

### Prerequisites

- **C++ Compiler** with C++17 support (GCC, Clang, or MSVC)
- **Python 3.7+** with pip
- **CMake 3.15+** (optional, for build system)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd network-ladder
   ```

2. **Build the C++ application**
   ```powershell
   # Windows (PowerShell)
   g++ -std=c++17 -O2 -o app.exe main.cpp Polynomial.cpp ContinuedFraction.cpp CSVMaker.cpp NetworkUtils.cpp
   
   # Or using CMake
   mkdir build && cd build
   cmake ..
   cmake --build . --config Release
   ```

3. **Install Python dependencies**
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   python -m pip install --upgrade pip
   python -m pip install pandas schemdraw matplotlib
   ```

### Usage

**Example: Synthesizing (s+1)/s**

```powershell
echo 1 1 1 1 0 1 | .\app.exe
```

**Input Format:**
- First line: `n a₀ a₁ ... aₙ` (numerator degree and coefficients in ascending powers)
- Second line: `m b₀ b₁ ... bₘ` (denominator degree and coefficients in ascending powers)

**Example Input:**
```
1 1 1    # s + 1 (numerator)
1 0 1    # s (denominator)
```

**Output:**
- `Z.csv` - Series impedances
- `Y.csv` - Shunt admittances  
- `ladder_network.png` - Visual schematic

## 🌐 Web Application

### Quick Web App Setup

1. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the web application**
   ```bash
   python web/app.py
   ```

3. **Open your browser**
   Navigate to: `http://localhost:5000`

### Docker Deployment

#### Option 1: Docker Compose (Recommended)

```bash
# Build and run with Docker Compose
docker-compose up --build

# Run in background
docker-compose up -d
```

#### Option 2: Manual Docker Build

```bash
# Build the image
docker build -t network-ladder .

# Run the container
docker run -p 5000:5000 network-ladder
```

### Web App Features

- **🌐 Modern Web Interface**: Clean, responsive design with Bootstrap 5
- **📊 Real-time Processing**: Instant network synthesis with live preview
- **🖼️ Interactive Visualization**: Auto-generated circuit schematics
- **📱 Mobile Friendly**: Works on desktop, tablet, and mobile devices
- **⚡ Fast Performance**: Optimized C++ backend with Python frontend
- **🎯 Example Templates**: Quick-start examples for common circuits

### API Endpoints

#### POST `/api/process`
Process a transfer function and return network data.

**Request:**
```json
{
  "numerator": [1, 1],
  "denominator": [0, 1]
}
```

**Response:**
```json
{
  "success": true,
  "Z": ["s"],
  "Y": ["1"],
  "image": "base64_encoded_png_data"
}
```

#### GET `/api/health`
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "message": "Network Ladder API is running"
}
```

### Production Deployment

#### Using Docker (Recommended)

```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  network-ladder:
    build: .
    ports:
      - "80:5000"
    environment:
      - FLASK_ENV=production
    restart: unless-stopped
    volumes:
      - ./logs:/app/logs
```

#### Using Reverse Proxy (Nginx)

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Quick Deploy Recipes

- Render: connect repo, choose Docker runtime, expose port 5000, health check `/api/health`.
- VPS + Docker Compose: `docker compose up -d --build` and reverse proxy with Nginx to `127.0.0.1:5000`.
- Heroku: use the included `Procfile` to run `gunicorn` (`wsgi:app`).

## 📚 Examples

### Example 1: Simple RC Network
**Transfer Function:** H(s) = (s+1)/s

**Input:**
```
1 1 1
1 0 1
```

**Result:** Series inductor (1H) with shunt resistor (1Ω)

### Example 2: LC Filter
**Transfer Function:** H(s) = (s²+4s+3)/(s²+2s)

**Input:**
```
2 3 4 1
2 0 2 1
```

**Result:** Series inductor (1H) with shunt parallel LC (2H + 3Ω)

## 🔧 API Reference

### Core Classes

#### `Polynomial`
- **Purpose**: Handles polynomial arithmetic operations
- **Key Methods**:
  - `operator+`, `operator-`, `operator*`: Basic arithmetic
  - `divmod()`: Division with remainder
  - `toString()`: String representation

#### `ContinuedFraction`
- **Purpose**: Converts rational functions to continued fraction form
- **Key Methods**:
  - `ContinuedFraction(N, D)`: Constructor with numerator and denominator
  - `get()`: Returns the continued fraction parts

#### `NetworkUtils`
- **Purpose**: Maps polynomial parts to network tokens
- **Key Functions**:
  - `mapAndValidateTokens()`: Converts Z/Y parts to string tokens
  - `polynomialToToken()`: Formats polynomials as network elements

### Python Visualization

The `network.py` script generates electrical schematics using:
- **schemdraw**: Circuit diagram generation
- **matplotlib**: Image rendering
- **pandas**: CSV data processing

## 🧪 Testing

Run the test suite using CMake:

```powershell
mkdir build && cd build
cmake -DBUILD_TESTING=ON ..
cmake --build .
ctest --verbose
```

**Test Coverage:**
- Polynomial arithmetic operations
- Continued fraction expansion
- Network synthesis edge cases
- Input validation

## 📁 Project Structure

```
network-ladder/
├── 📄 main.cpp                 # Main application entry point
├── 📄 CMakeLists.txt          # CMake build configuration
├── 📁 src/                    # Core C++ source files
│   ├── 📄 Polynomial.hpp/.cpp      # Polynomial arithmetic
│   ├── 📄 ContinuedFraction.hpp/.cpp # Continued fraction expansion
│   ├── 📄 NetworkUtils.hpp/.cpp    # Network synthesis utilities
│   └── 📄 CSVMaker.hpp/.cpp       # CSV output generation
├── 📁 tests/                  # Unit tests
│   └── 📄 test_network.cpp        # GoogleTest test cases
├── 📄 network.py              # Python visualization script
├── 📄 README.md               # This file
└── 📁 out/                    # Build output directory
```

## 🔬 Mathematical Background

### Continued Fraction Expansion

The algorithm converts a rational transfer function H(s) = N(s)/D(s) into a continued fraction:

```
H(s) = q₀(s) + 1/(q₁(s) + 1/(q₂(s) + 1/(...)))
```

Where:
- **q₀, q₂, q₄, ...** become **series impedances** (Z)
- **q₁, q₃, q₅, ...** become **shunt admittances** (Y)

### Network Synthesis

The resulting ladder network follows the Cauer form:
- **Series elements**: Inductors (s terms) and resistors (constant terms)
- **Shunt elements**: Capacitors (1/s terms) and resistors (constant terms)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **schemdraw** library for beautiful circuit diagrams
- **GoogleTest** for comprehensive testing framework
- **CMake** for cross-platform build system

---

<div align="center">

**Made with ❤️ for electrical engineers and circuit designers**

[Report Bug](https://github.com/your-repo/issues) • [Request Feature](https://github.com/your-repo/issues) • [Documentation](https://github.com/your-repo/wiki)

</div>