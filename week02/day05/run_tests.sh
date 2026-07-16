#!/usr/bin/env bash

OUTPUT="output.txt"
: > "$OUTPUT"

# Make sure port 8000 is not already in use
if fuser 8000/tcp > /dev/null 2>&1; then
    echo "Port 8000 is already in use."
    echo "Stop the old test server, then run this script again."
    exit 1
fi

# Start the local test server in the background
python -u test_server.py > test_server_output.txt 2>&1 &
SERVER_PID=$!

# Give the server a moment to start
sleep 1

# Check that the server started successfully
if ! kill -0 "$SERVER_PID" 2>/dev/null; then
    echo "Test server could not start."
    cat test_server_output.txt
    exit 1
fi

# Stop the server when the script finishes
cleanup() {
    kill "$SERVER_PID" 2>/dev/null
    wait "$SERVER_PID" 2>/dev/null
}

trap cleanup EXIT

echo "Version: v0.5.0" | tee -a "$OUTPUT"
echo "URL: http://127.0.0.1:8000" | tee -a "$OUTPUT"
echo "Expected: 3 unique links with no URL fragments" | tee -a "$OUTPUT"
echo "----------------------------------------" | tee -a "$OUTPUT"

python -u checker.py http://127.0.0.1:8000 --delay 0.1 2>&1 | tee -a "$OUTPUT"

echo "----------------------------------------" | tee -a "$OUTPUT"
echo "Results saved to $OUTPUT"
