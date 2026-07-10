#!/bin/bash
set -e

echo "Building pyrbd_core..."

# Create build directory
mkdir -p build
cd build

# Configure and build
cmake .. -DCMAKE_BUILD_TYPE=Release
make -j$(nproc)

cd ..

# Install the Python package in development mode
pip install -e . --no-build-isolation 2>/dev/null || echo "Note: pip install skipped (run manually if needed)"

echo "pyrbd_core build completed."
