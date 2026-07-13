CLI Broken Link Checker

**Current Version:** v0.2.0 (Network Resilience & Graceful Exit)

## Overview
This project is an automated command-line tool designed to detect broken hyperlinks on a given web page. 
Currently, the project is in its `v0.2.0` phase. This version establishes the foundational CLI structure, strict input validation, and robust network error handling using `requests`.

## Features in v0.2.0
* **CLI Argument Parsing:** Utilizes `argparse` to handle mandatory and optional arguments safely.
* **Strict URL Validation:** Ensures the target URL contains a valid scheme (`http://` or `https://`) and a valid domain before proceeding.
* **Graceful Prevention:** Prevents execution and returns standardized error messages for malformed inputs.
* **Network Resilience:** Implements `try/except` blocks to gracefully catch DNS failures, timeouts, and connection errors without crashing the script.

## Usage
To test the current network logic, activate the virtual environment and run the script:

**Standard execution:**
```bash
python checker.py https://www.python.org
```
**Advanced execution:**
```bash
python checker.py https://www.python.org --delay 0.1
```
