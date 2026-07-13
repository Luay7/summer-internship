# CLI Broken Link Checker

**Current Version:** v0.3.0 (Smart Engine & Log Formatting)

## Overview
This project is an automated command-line tool designed to detect broken hyperlinks on a given web page. 
Currently, the project is in its `v0.3.0` phase. This version introduces the core engine using `BeautifulSoup` for link extraction and implements a smart fallback verification strategy with structured logging.

## Features in v0.3.0
* **CLI Argument Parsing:** Utilizes `argparse` to handle mandatory and optional arguments safely.
* **Strict URL Validation:** Ensures the target URL contains a valid scheme (`http://` or `https://`) and a valid domain before proceeding.
* **Graceful Prevention:** Prevents execution and returns standardized error messages for malformed inputs.
* **Network Resilience:** Implements `try/except` blocks to gracefully catch DNS failures, timeouts, and connection errors without crashing the script.
* **Smart Link Extraction:** Uses `BeautifulSoup` to parse HTML, extract valid anchor tags, and resolve relative URLs into absolute ones.
* **Fallback Verification Strategy:** Intelligently switches from fast `HEAD` requests to `GET` requests if blocked (403/405), and automatically retries upon timeouts to ensure accurate status reporting.
* **Structured Logging:** Outputs real-time, easily parsable logs containing the exact HTTP status codes returned by the server (e.g., `[OK] https://example.com HEAD 200`).

## Usage
To test the current verification engine, activate the virtual environment and run the script:

**Standard execution:**
```bash
python checker.py [https://www.python.org](https://www.python.org)
```
**Advanced execution:**
```bash
python checker.py https://www.python.org --delay 0.1
```
