import argparse
import sys
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

# 3. Print status
print(f"Starting scan for: {target_url}")
print(f"Delay: {delay} seconds")
print("Initialization successful. Ready to fetch...")
