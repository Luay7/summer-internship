## Day 3 Task: Code Review & Refactoring

**Overview of the Review Process:**
Following the AI-assisted development phase, a thorough line-by-line code review was conducted on the initial script. The goal was to shift from simply "trusting" the AI output to actively "verifying" it. During this review, several subtle logical bugs, performance bottlenecks, and structural inefficiencies were identified. 

Below are the 7 key improvements implemented to enhance the script's readability, efficiency, and correctness, ordered logically by the script's execution flow:

### 1. Granular Network Error Handling (Readability)
* **The Problem:** The script used a single generic exception to catch all network errors during the initial page fetch. If the internet disconnected or a page was missing (404), the user saw the exact same confusing error message.
* **The Solution:** Split the error handling into specific blocks (e.g., `Timeout`, `HTTPError`, `ConnectionError`). 
* **The Impact:** The tool now tells the user exactly what went wrong and how to fix it, making debugging much easier.

### 2. Simplified Link Extraction (Readability)
* **The Problem:** The code extracted all `<a>` tags and then manually looped through them to check if they actually had an `href` attribute, which looked messy.
* **The Solution:** Used BeautifulSoup's built-in filter to extract only tags with a valid `href` directly.
* **The Impact:** Removed unnecessary lines of code, making the extraction phase cleaner and more "Pythonic".

### 3. Ignoring Anchor Links (Correctness)
* **The Problem:** The script treated page sections (like `https://example.com/#about`) as brand-new links, causing duplicate and useless network requests to the same page.
* **The Solution:** Used a filter to remove URL fragments (the `#` part) before adding them to the check list.
* **The Impact:** Prevents redundant scanning and saves execution time.

### 4. Fast Link Filtering (Efficiency)
* **The Problem:** The script used a standard Python list `[]` to store links and check for duplicates. Searching through a list gets very slow when a page has thousands of links.
* **The Solution:** Changed the data structure to a Python `set()`.
* **The Impact:** Sets prevent duplicates automatically and offer instant search speed, making the extraction process highly efficient.

### 5. Smart Fallback Strategy (Correctness)
* **The Problem:** The fallback logic only triggered if the server returned status codes `403` or `405`. It failed to catch other common blocks like `401` or `429` (Too Many Requests).
* **The Solution:** Updated the logic to dynamically check if the status code is `>= 400` (excluding standard errors like 404 and 503).
* **The Impact:** The tool now automatically adapts to any unknown firewall or anti-bot protection accurately.

### 6. Streaming Fallback Requests (Efficiency)
* **The Problem:** When checking a protected link using a standard `GET` request, the script downloaded the entire file. If the link was a 100MB PDF, it wasted huge amounts of bandwidth and memory.
* **The Solution:** Configured the fallback `GET` request to stream, reading only the HTTP headers.
* **The Impact:** The script now immediately closes the connection after reading the headers, saving bandwidth and making the check instant.

### 7. Code Modularization (Maintainability)
* **The Problem:** The entire script was written as one long, flat file, making it hard to read and test.
* **The Solution:** Grouped the logic into specific functions (e.g., `fetch_page()`, `extract_links()`) and added a `main()` execution block.
* **The Impact:** The code is now organized, modular, and ready for future updates and unit testing.
