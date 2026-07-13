# CLI Broken Link Checker

**Current Version:** v0.1.0 (Initial Skeleton & Validation)

## Overview
This project is an automated command-line tool designed to detect broken hyperlinks on a given web page. 
Currently, the project is in its initial development phase (`v0.1.0`). This version establishes the foundational CLI structure, argument parsing, and strict input validation rules based on the project specifications (`SPEC.md`).

## Features in v0.1.0
* **CLI Argument Parsing:** Utilizes `argparse` to handle mandatory and optional arguments safely.
* **Strict URL Validation:** Ensures the target URL contains a valid scheme (`http://` or `https://`) and a valid domain before proceeding.
* **Graceful Prevention:** Prevents execution and returns standardized error messages for malformed inputs.

## Usage
To test the current skeleton logic, activate the virtual environment and run the script:

**Standard execution:**
```bash
python checker.py https://www.python.org
```
**Advanced execution:**
```bash
python checker.py https://www.python.org --delay 0.1
```
