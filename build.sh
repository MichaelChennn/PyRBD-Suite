#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

echo "Building pyrbd_core..."
chmod +x packages/pyrbd_core/build.sh
(cd packages/pyrbd_core && ./build.sh)

echo "Installing pyrbd_suite..."
(cd packages/pyrbd_suite && pip install -e .)

echo "All builds completed successfully."