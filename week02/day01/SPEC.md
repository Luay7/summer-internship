# Software Specification

**Project Name:** CLI Broken Link Checker

---

## 1. The Problem
Over time, websites suffer from "link rot" where page paths change or external sites go offline, resulting in broken links (e.g., 404 Not Found). These dead links harm User Experience (UX) and negatively impact Search Engine Optimization (SEO). Manually checking each link is tedious, time-consuming, and impractical. This project aims to automate this process to save developers' time and ensure website quality, while efficiently handling server firewalls and security restrictions.

## 2. Key Features (In Scope)
* **Strict Input Validation:** The tool accepts only a single, properly formatted absolute URL (must include `http://` or `https://`) per execution. If the input format is malformed, the tool gracefully exits with a clear error message.
* **Graceful Error Handling (Network Resilience):** If the primary target website is completely unreachable (e.g., the domain does not exist, the server is down, or there is no active internet connection), the tool will catch the network exception and exit gracefully with a human-readable error, preventing abrupt script crashes or raw Python stack traces.
* **HTML Parsing:** The tool fetches the target page's raw HTML and intelligently extracts all hyperlinks (`<a>` tags), automatically skipping non-navigable links (e.g., `mailto:` or `javascript:`).
* **Smart Verification & Fallback Strategy:** The tool primarily sends a fast HTTP `HEAD` request to verify a link's status. If the server rejects the `HEAD` request (status codes 403, 405, etc.), the tool automatically sends a confirming `GET` request. In the event of a connection timeout, it will retry by sending a confirming `HEAD` request once more; if there is still no response, it stops trying for that link.
* **Customizable Request Delay:** To prevent IP bans and avoid overloading servers (Rate Limiting), the tool implements a default time delay (e.g., 1 second) between requests. Users can customize this delay via a CLI argument.
* **Structured Log Reporting:** The tool outputs a clean, unified log-style report in the terminal. Each entry includes the exact timestamp, the final classification of the link, the URL itself, and the sequence of requests made (e.g., `[YYYY-MM-DD HH:MM:SS] 🛡️ [Protected] https://example.com | HEAD: 403 -> GET: 200`).

## 3. Constraints & Out of Scope
* **Sequential Processing (No Concurrency):** The tool checks links synchronously, one by one. Multi-threading or asynchronous concurrent requests are completely out of scope to maintain project simplicity and respect the rate limit delay.
* **No Recursive Crawling:** The tool will only scan the specific page provided by the user. It will not follow links to scan the entire website (no deep crawling) to prevent infinite loops and ensure the project fits within a one-week timeline.
* **No Authentication Bypass:** The tool only scans publicly accessible pages. It will not handle URLs that require login credentials or attempt to bypass authentication walls.
* **No JavaScript Rendering:** The tool parses direct links from the raw HTML source code. It will not execute or render JavaScript to find dynamically generated links.
* **CLI & Text Output Only:** There is no Graphical User Interface (GUI). All inputs and outputs are handled via the terminal, and results will not be exported to external files (e.g., Excel, PDF) or saved to a database.
