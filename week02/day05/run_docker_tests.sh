#!/usr/bin/env bash

set -euo pipefail

IMAGE_NAME="cli-broken-link-checker:final-test"
OUTPUT_FILE="$(pwd)/docker_output.txt"

# The container uses the host network, so port 8000 must be free.
if fuser 8000/tcp > /dev/null 2>&1; then
    echo "Port 8000 is already in use."
    echo "Stop the existing test server, then run this script again."
    exit 1
fi

: > "$OUTPUT_FILE"

echo "Building Docker test image using the host network..."

docker build \
    --network host \
    -f Dockerfile.test \
    -t "$IMAGE_NAME" \
    .

echo "Running the final test suite inside Docker using the host network..."

docker run --rm \
    --network host \
    --mount type=bind,src="$OUTPUT_FILE",dst=/app/output.txt \
    "$IMAGE_NAME"

# Keep the generated file owned by the normal user when the script uses sudo.
if [ -n "${SUDO_USER:-}" ]; then
    chown "$SUDO_USER":"$(id -gn "$SUDO_USER")" "$OUTPUT_FILE"
fi

echo "Docker test results saved to docker_output.txt"
