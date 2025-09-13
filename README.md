# Network Ladder

Minimal build and run instructions.

## Build
```powershell
g++ -std=c++17 -O2 -o app.exe main.cpp Polynomial.cpp ContinuedFraction.cpp CSVMaker.cpp NetworkUtils.cpp
```

## Run (example: (s+1)/s)
Input format is degrees followed by coefficients (ascending powers):
- First line: n a0 ... an
- Second line: m b0 ... bm

Example:
```powershell
echo 1 1 1 1 0 1 | .\app.exe
```

This writes `Z.csv` and `Y.csv` and invokes `network.py`.

## Python image generation
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install pandas schemdraw matplotlib
python network.py
```

Outputs:
- `Z.csv`, `Y.csv` from the C++ app
- `ladder_network.png` from `network.py`
