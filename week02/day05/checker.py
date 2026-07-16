# Improvement 7: Code Modularization
# The final version reorganizes the code into reusable functions (methods) instead of one long execution flow.

import argparse
import sys
import time
from datetime import datetime
from urllib.parse import urljoin, urldefrag, urlparse

import requests
from bs4 import BeautifulSoup


def parse_arguments():
    """Read command-line arguments."""
    parser = argparse.ArgumentParser(description="CLI Broken Link Checker")
    parser.add_argument("url", help="Target URL to scan")
    parser.add_argument("--delay", type=float, default=1.0, help="Delay between requests in seconds")
    return parser.parse_args()


def validate_url(target_url):
    """Return True when the target URL is a valid HTTP or HTTPS URL."""
    parsed = urlparse(target_url)

    if parsed.scheme not in ["http", "https"] or not parsed.netloc:
        print("[ERROR] Invalid URL format.")
        print("Please use a valid URL starting with http:// or https://")
        return False

    return True


def fetch_page(target_url):
    """Fetch the target page and return its HTML content."""
    print("-" * 50)
    print(f"Fetching main page: {target_url}")

    try:
        response = requests.get(target_url, timeout=10)
        response.raise_for_status()
        print("[SUCCESS] Successfully connected to the target URL.\n")
        return response.text

    # Improvement 1: Granular Network Error Handling
    # Different network errors now display specific and clear messages.
    except requests.exceptions.Timeout as error:
        print("\n[FATAL ERROR] The request timed out.")
        print(f"Technical Details: {error}")
        print("The target website took too long to respond.")

    except requests.exceptions.HTTPError as error:
        print("\n[FATAL ERROR] The target website returned an HTTP error.")
        print(f"HTTP Status: {error.response.status_code}")
        print(f"Technical Details: {error}")

    except requests.exceptions.ConnectionError as error:
        print("\n[FATAL ERROR] Failed to connect to the target website.")
        print(f"Technical Details: {error}")
        print("Please check your internet connection or verify that the domain is online.")

    except requests.exceptions.RequestException as error:
        print("\n[FATAL ERROR] An unexpected network error occurred.")
        print(f"Technical Details: {error}")

    return None


def extract_links(html_content, target_url):
    """Extract unique HTTP and HTTPS links from the target page."""
    print("-" * 50)
    print("Extracting links...")

    soup = BeautifulSoup(html_content, "html.parser")

    # Improvement 2: Simplified Link Extraction
    # BeautifulSoup now extracts only anchor tags that contain a non-empty href.
    raw_links = soup.find_all("a", href=lambda href: href and href.strip())

    # Improvement 3: Faster Duplicate Filtering
    # A set automatically prevents duplicate URLs and provides faster lookup.
    links_to_check = set()

    for tag in raw_links:
        href = tag.get("href")

        # Convert relative links into absolute links.
        absolute_url = urljoin(target_url, href)

        # Improvement 4: Remove URL Fragments
        # Links such as /page#top and /page#content are treated as the same URL.
        clean_url, _ = urldefrag(absolute_url)

        # Keep only HTTP and HTTPS links.
        parsed_href = urlparse(clean_url)
        if parsed_href.scheme in ["http", "https"]:
            links_to_check.add(clean_url)

    print(f"Found {len(links_to_check)} unique valid links to check.\n")
    return links_to_check


def log_result(classification, link, request_history):
    """Print one structured result with a timestamp."""
    # Specification Completion: Timestamped Structured Logging
    # Every result now includes the exact time, classification, URL, and request history.
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{classification}] {link} | {request_history}")


def verify_with_get(link, head_history):
    """Use a streaming GET fallback after an unsuccessful HEAD response."""
    try:
        # Improvement 6: Streaming Fallback Requests
        # stream=True reads the response status without downloading the full response body.
        with requests.get(link, timeout=5, allow_redirects=True, stream=True) as get_resp:
            get_status = get_resp.status_code

        if get_status < 400:
            log_result("PROTECTED", link, f"{head_history} -> GET {get_status}")
        elif get_status == 404:
            log_result("DEAD", link, f"{head_history} -> GET {get_status}")
        elif get_status == 503:
            log_result("UNAVAILABLE", link, f"{head_history} -> GET {get_status}")
        else:
            log_result("BLOCKED", link, f"{head_history} -> GET {get_status}")

    except requests.exceptions.Timeout:
        # Retry GET once when the first streaming request times out.
        try:
            with requests.get(link, timeout=2, allow_redirects=True, stream=True) as retry_get:
                retry_get_status = retry_get.status_code

            if retry_get_status < 400:
                log_result("PROTECTED", link, f"{head_history} -> GET TIMEOUT -> GET {retry_get_status}")
            elif retry_get_status == 404:
                log_result("DEAD", link, f"{head_history} -> GET TIMEOUT -> GET {retry_get_status}")
            elif retry_get_status == 503:
                log_result("UNAVAILABLE", link, f"{head_history} -> GET TIMEOUT -> GET {retry_get_status}")
            else:
                log_result("BLOCKED", link, f"{head_history} -> GET TIMEOUT -> GET {retry_get_status}")

        except requests.exceptions.Timeout:
            log_result("TIMEOUT", link, f"{head_history} -> GET TIMEOUT -> GET TIMEOUT")

        except requests.exceptions.RequestException:
            log_result("BLOCKED", link, f"{head_history} -> GET TIMEOUT -> GET ERROR")

    except requests.exceptions.RequestException:
        log_result("BLOCKED", link, f"{head_history} -> GET ERROR")


def handle_head_status(link, head_status, head_history):
    """Classify a HEAD response or start the GET fallback strategy."""
    # Improvement 5: Improved Fallback Strategy
    # Any HEAD error or protection status uses GET fallback, except clear 404 and 503 results.
    if head_status < 400:
        log_result("OK", link, head_history)
    elif head_status == 404:
        log_result("DEAD", link, head_history)
    elif head_status == 503:
        log_result("UNAVAILABLE", link, head_history)
    else:
        verify_with_get(link, head_history)


def check_link(link):
    """Check one link using HEAD, retry, and GET fallback when required."""
    try:
        link_resp = requests.head(link, timeout=5, allow_redirects=True)
        head_status = link_resp.status_code
        handle_head_status(link, head_status, f"HEAD {head_status}")

    except requests.exceptions.Timeout:
        # Retry HEAD once after a timeout.
        try:
            retry_resp = requests.head(link, timeout=2, allow_redirects=True)
            retry_status = retry_resp.status_code

            # The retried HEAD response now uses the same fallback strategy as the first attempt.
            handle_head_status(link, retry_status, f"HEAD TIMEOUT -> HEAD {retry_status}")

        except requests.exceptions.Timeout:
            log_result("TIMEOUT", link, "HEAD TIMEOUT -> HEAD TIMEOUT")

        except requests.exceptions.RequestException:
            log_result("ERROR", link, "HEAD TIMEOUT -> HEAD ERROR")

    except requests.exceptions.RequestException:
        log_result("ERROR", link, "HEAD ERROR")


def verify_links(links_to_check, delay):
    """Check every extracted link sequentially."""
    print("-" * 50)
    print("Starting Link Verification...")

    for link in links_to_check:
        time.sleep(delay)
        check_link(link)


def main():
    """Run the CLI Broken Link Checker."""
    args = parse_arguments()
    target_url = args.url
    delay = args.delay

    if not validate_url(target_url):
        sys.exit(1)

    print(f"Starting scan for: {target_url}")
    print(f"Delay: {delay} seconds")
    print("Initialization successful. Ready to fetch...\n")

    html_content = fetch_page(target_url)
    if html_content is None:
        sys.exit(1)

    links_to_check = extract_links(html_content, target_url)
    verify_links(links_to_check, delay)


if __name__ == "__main__":
    main()


