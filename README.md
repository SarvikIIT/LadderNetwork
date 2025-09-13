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