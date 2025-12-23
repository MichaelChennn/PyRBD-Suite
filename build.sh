#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

echo "Building pyrbd_plusplus..."
chmod +x packages/pyrbd_plusplus/build.sh
(cd packages/pyrbd_plusplus && ./build.sh)

echo "Building pyrbd3..."
chmod +x packages/pyrbd3/build.sh
(cd packages/pyrbd3 && ./build.sh)

echo "All builds completed successfully."