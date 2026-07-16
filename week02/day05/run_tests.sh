#!/usr/bin/env bash

OUTPUT="output.txt"
: > "$OUTPUT"

run_test() {
    url="$1"
    expected="$2"
    shift 2

    echo "URL: $url" | tee -a "$OUTPUT"
    echo "Expected: $expected" | tee -a "$OUTPUT"

    python -u checker.py "$url" "$@" 2>&1 | tee -a "$OUTPUT"

    echo "----------------------------------------" | tee -a "$OUTPUT"
}

run_test "http://127.0.0.1:8000" "Successful scan (200 OK)" --delay 0.1
run_test "example.com" "Invalid URL format"
run_test "https://connection-test.invalid" "Connection error"
run_test "http://127.0.0.1:8000/404" "HTTP error 404"
run_test "http://127.0.0.1:8000/503" "HTTP error 503"

echo "Results saved to $OUTPUT"
