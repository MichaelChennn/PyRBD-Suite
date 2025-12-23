#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

echo "Building pyrbd_plusplus..."
chmod +x packages/pyrbd_plusplus/build.sh
./packages/pyrbd_plusplus/build.sh

echo "Building pyrbd3..."
chmod +x packages/pyrbd3/build.sh
./packages/pyrbd3/build.sh

echo "All builds completed successfully."