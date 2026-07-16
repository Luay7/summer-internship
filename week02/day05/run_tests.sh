#!/usr/bin/env bash

set -o pipefail

OUTPUT="output.txt"
INTEGRATION_RESULT="integration_result.txt"
BRANCH_RESULT="branch_result.txt"

: > "$OUTPUT"
: > "$INTEGRATION_RESULT"
: > "$BRANCH_RESULT"

python -u test_server.py > test_server_output.txt 2>&1 &
SERVER_PID=$!

cleanup() {
    kill "$SERVER_PID" 2>/dev/null || true
    wait "$SERVER_PID" 2>/dev/null || true
    rm -f "$INTEGRATION_RESULT" "$BRANCH_RESULT"
}

trap cleanup EXIT

sleep 1

if ! kill -0 "$SERVER_PID" 2>/dev/null; then
    echo "Test server could not start."
    cat test_server_output.txt
    exit 1
fi

echo "Version: v1.0.0 Final Comprehensive Test" | tee -a "$OUTPUT"
echo "URL: http://127.0.0.1:8000/final" | tee -a "$OUTPUT"
echo "Expected: Multiple paths for OK, PROTECTED, DEAD, UNAVAILABLE, and BLOCKED" | tee -a "$OUTPUT"
echo "----------------------------------------" | tee -a "$OUTPUT"

python -u checker.py http://127.0.0.1:8000/final --delay 0.01 \
    2>&1 | tee "$INTEGRATION_RESULT" | tee -a "$OUTPUT"

INTEGRATION_PASSED=true

required_results=(
    "Found 12 unique valid links to check."
    "/ok-200 | HEAD 200"
    "/ok-204 | HEAD 204"
    "/redirect-ok | HEAD 200"
    "/head-401-get-200 | HEAD 401 -> GET 200"
    "/head-403-get-204 | HEAD 403 -> GET 204"
    "/large-file | HEAD 403 -> GET 200"
    "/dead-404 | HEAD 404"
    "/head-405-get-404 | HEAD 405 -> GET 404"
    "/unavailable-503 | HEAD 503"
    "/head-429-get-503 | HEAD 429 -> GET 503"
    "/head-500-get-429 | HEAD 500 -> GET 429"
    "/head-403-get-500 | HEAD 403 -> GET 500"
)

for expected in "${required_results[@]}"; do
    if ! grep -Fq "$expected" "$INTEGRATION_RESULT"; then
        INTEGRATION_PASSED=false
    fi
done

if [ "$INTEGRATION_PASSED" = true ]; then
    echo "Integration Test Result: Passed" | tee -a "$OUTPUT"
else
    echo "Integration Test Result: Failed" | tee -a "$OUTPUT"
fi

echo "----------------------------------------" | tee -a "$OUTPUT"
echo "Deterministic Timeout and Error Branch Tests" | tee -a "$OUTPUT"
echo "----------------------------------------" | tee -a "$OUTPUT"

python -u test_branches.py \
    2>&1 | tee "$BRANCH_RESULT" | tee -a "$OUTPUT"

if grep -Fq "BRANCH TEST SUMMARY: 18/18 Passed" "$BRANCH_RESULT"; then
    BRANCH_PASSED=true
else
    BRANCH_PASSED=false
fi

if [ "$INTEGRATION_PASSED" = true ] && [ "$BRANCH_PASSED" = true ]; then
    echo "FINAL TEST RESULT: PASSED" | tee -a "$OUTPUT"
    exit 0
else
    echo "FINAL TEST RESULT: FAILED" | tee -a "$OUTPUT"
    exit 1
fi
