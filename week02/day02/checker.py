import argparse
import sys
import requests
from urllib.parse import urlparse

# 1. Setup CLI arguments
parser = argparse.ArgumentParser(description="CLI Broken Link Checker")
parser.add_argument("url", help="Target URL to scan")
parser.add_argument("--delay", type=float, default=1.0, help="Delay between requests in seconds")

args = parser.parse_args()
target_url = args.url
delay = args.delay

# 2. Validate URL format
parsed = urlparse(target_url)
if parsed.scheme not in ['http', 'https'] or not parsed.netloc:
    print("[ERROR] Invalid URL format.")
    print("Please use a valid URL starting with http:// or https://")
    sys.exit(1)

# 3. Print initialization status
print(f"Starting scan for: {target_url}")
print(f"Delay: {delay} seconds")
print("Initialization successful. Ready to fetch...\n")

# 4. Network Fetch & Graceful Error Handling
print("-" * 50)
print(f"Fetching main page: {target_url}")

try:
    # Adding a 10-second timeout to prevent the script from hanging indefinitely
    response = requests.get(target_url, timeout=10)
    
    # Raise an exception if the server responds with an error code (4xx, 5xx)
    response.raise_for_status()
    
    print("[SUCCESS] Successfully connected to the target URL.")
    # html_content = response.text (Prepared for Phase 3)

except requests.exceptions.RequestException as e:
    # Catch all network-related exceptions (DNS failure, timeout, connection reset, etc.)
    print("\n[FATAL ERROR] Failed to establish a connection to the target website.")
    print(f"Technical Details: {e}")
    print("Please check your internet connection or verify that the domain is online.")
    sys.exit(1) # Graceful exit without crashing
