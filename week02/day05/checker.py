import argparse
import sys
import time
import requests
from urllib.parse import urlparse, urljoin, urldefrag
from bs4 import BeautifulSoup

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
    response = requests.get(target_url, timeout=10)
    response.raise_for_status()
    print("[SUCCESS] Successfully connected to the target URL.\n")
    html_content = response.text

# Improvement 1: Granular Network Error Handling
# Different network errors now display specific and clear messages.
except requests.exceptions.Timeout as e:
    print("\n[FATAL ERROR] The request timed out.")
    print(f"Technical Details: {e}")
    print("The target website took too long to respond.")
    sys.exit(1)

except requests.exceptions.HTTPError as e:
    print("\n[FATAL ERROR] The target website returned an HTTP error.")
    print(f"HTTP Status: {e.response.status_code}")
    print(f"Technical Details: {e}")
    sys.exit(1)

except requests.exceptions.ConnectionError as e:
    print("\n[FATAL ERROR] Failed to connect to the target website.")
    print(f"Technical Details: {e}")
    print("Please check your internet connection or verify that the domain is online.")
    sys.exit(1)

except requests.exceptions.RequestException as e:
    print("\n[FATAL ERROR] An unexpected network error occurred.")
    print(f"Technical Details: {e}")
    sys.exit(1)

# 5. Extract and Filter Links
print("-" * 50)
print("Extracting links...")
soup = BeautifulSoup(html_content, 'html.parser')

# Improvement 2: Simplified Link Extraction
# BeautifulSoup now extracts only anchor tags that contain a non-empty href.
raw_links = soup.find_all('a', href=lambda href: href and href.strip())

# Improvement 3: Faster Duplicate Filtering
# A set automatically prevents duplicate URLs and provides faster lookup.
links_to_check = set()

for tag in raw_links:
    href = tag.get('href')
        
    # Convert relative links (like /about) to absolute links (https://site.com/about)
    absolute_url = urljoin(target_url, href)

    # Improvement 4: Remove URL Fragments
    # Links such as /page#top and /page#content are treated as the same URL.
    clean_url, fragment = urldefrag(absolute_url)
    
    # Filter out mailto, javascript, etc. Keep only http/https
    parsed_href = urlparse(clean_url)
    if parsed_href.scheme in ['http', 'https']:
        links_to_check.add(clean_url)

print(f"Found {len(links_to_check)} unique valid links to check.\n")

# 6. Smart Verification & Fallback Strategy
print("-" * 50)
print("Starting Link Verification...")

for link in links_to_check:
    # Apply user-defined delay before each request
    time.sleep(delay)
    
    try:
        # First attempt: Fast HEAD request
        link_resp = requests.head(link, timeout=5, allow_redirects=True)
        h_status = link_resp.status_code
        
        # Fallback 1: If server rejects HEAD, try GET
        if h_status in [403, 405]:
            get_resp = requests.get(link, timeout=5, allow_redirects=True)
            g_status = get_resp.status_code
            
            # Print actual status codes returned by the server
            if g_status < 400:
                print(f"[PROTECTED] {link} HEAD {h_status} GET {g_status}")
            elif g_status == 503:
                print(f"[UNAVAILABLE] {link} HEAD {h_status} GET {g_status}")
            elif g_status == 404:
                print(f"[DEAD] {link} HEAD {h_status} GET {g_status}")
            else:
                print(f"[BLOCKED] {link} HEAD {h_status} GET {g_status}")
        else:
            # Print actual HEAD status code
            if h_status < 400:
                print(f"[OK] {link} HEAD {h_status}")
            elif h_status == 503:
                print(f"[UNAVAILABLE] {link} HEAD {h_status}")
            elif h_status == 404:
                print(f"[DEAD] {link} HEAD {h_status}")
            else:
                print(f"[BROKEN] {link} HEAD {h_status}")
                
    except requests.exceptions.Timeout:
        # Fallback 2: Retry HEAD once on timeout
        try:
            retry_resp = requests.head(link, timeout=5, allow_redirects=True)
            r_status = retry_resp.status_code
            
            # If the retry succeeds, log the actual recovered status code
            if r_status < 400:
                print(f"[OK] {link} HEAD TIMEOUT HEAD {r_status}")
            elif r_status == 503:
                print(f"[UNAVAILABLE] {link} HEAD TIMEOUT HEAD {r_status}")
            elif r_status == 404:
                print(f"[DEAD] {link} HEAD TIMEOUT HEAD {r_status}")
            else:
                print(f"[BROKEN] {link} HEAD TIMEOUT HEAD {r_status}")
                
        except requests.exceptions.Timeout:
            # If it times out again, there is no status code to print
            print(f"[DEAD] {link} HEAD TIMEOUT HEAD TIMEOUT")
        except requests.exceptions.RequestException:
            # If the retry results in a connection error
            print(f"[DEAD] {link} HEAD TIMEOUT HEAD ERROR")
            
    except requests.exceptions.RequestException:
        # Catch other connection errors where no status code is returned
        print(f"[DEAD] {link} HEAD ERROR")
