#!/bin/bash
# Build script for template projects with CMake and Clang

set -e

PROJECT_NAME=${1:-pid_controller}
BUILD_DIR="${PROJECT_NAME}_build"

echo "Building $PROJECT_NAME with CMake and Clang..."

# Create build directory
mkdir -p "$BUILD_DIR"

# Configure with CMake using Clang
echo "Configuring CMake..."
cmake -S . -B "$BUILD_DIR" \
    -DCMAKE_C_COMPILER=clang \
    -DCMAKE_CXX_COMPILER=clang++ \
    -DCMAKE_BUILD_TYPE=Debug

# Build
echo "Building..."
cmake --build "$BUILD_DIR" --verbose

# Run tests
echo "Running tests..."
ctest --test-dir "$BUILD_DIR" --verbose

# MULL mutation testing (if available)
if command -v mull-runner &> /dev/null; then
    echo ""
    echo "Running MULL mutation testing..."
    mull-runner -config mull.yml --log-level=info
else
    echo ""
    echo "MULL not installed. To install: sudo apt-get install mull-runner"
    echo "Or see: https://mull.readthedocs.io/"
fi

echo ""
echo "Build and test complete!"
