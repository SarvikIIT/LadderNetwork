# Multi-stage build for Network Ladder Web App
FROM ubuntu:22.04 as builder

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    g++ \
    cmake \
    && rm -rf /var/lib/apt/lists/*

# Copy source files
WORKDIR /app
COPY src/*.cpp src/*.hpp ./src/
COPY CMakeLists.txt ./

# Build the C++ application
RUN g++ -std=c++17 -O2 -o app \
    src/main.cpp src/Polynomial.cpp src/ContinuedFraction.cpp src/CSVMaker.cpp src/NetworkUtils.cpp

# Python runtime stage
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy Python requirements and install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the built C++ application and Python files
COPY --from=builder /app/app ./
COPY web ./web
COPY templates ./templates
COPY static ./static
COPY wsgi.py ./
COPY requirements.txt ./

# Create a non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/api/health || exit 1

# Run via shell so $PORT expands on platforms that don't inject a shell
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT:-5000} --timeout 600 wsgi:app"]
