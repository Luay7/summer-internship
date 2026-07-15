import argparse
import sys
import time
import requests
from urllib.parse import urlparse, urljoin
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
except requests.exceptions.RequestException as e:
    print("\n[FATAL ERROR] Failed to establish a connection to the target website.")
    print(f"Technical Details: {e}")
    print("Please check your internet connection or verify that the domain is online.")
    sys.exit(1)

# 5. Extract and Filter Links
print("-" * 50)
print("Extracting links...")
soup = BeautifulSoup(html_content, 'html.parser')
raw_links = soup.find_all('a')

links_to_check = []
for tag in raw_links:
    href = tag.get('href')
    if not href:
        continue
        
    # Convert relative links (like /about) to absolute links (https://site.com/about)
    absolute_url = urljoin(target_url, href)
    
    # Filter out mailto, javascript, etc. Keep only http/https
    parsed_href = urlparse(absolute_url)
    if parsed_href.scheme in ['http', 'https']:
        if absolute_url not in links_to_check: # Prevent checking duplicates
            links_to_check.append(absolute_url)

print(f"Found {len(links_to_check)} valid links to check.\n")

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
            get_resp = requests.get(link, allow_redirects=True)
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
