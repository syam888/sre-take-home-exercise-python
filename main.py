import yaml
import requests
import time
import sys
from urllib.parse import urlparse
from collections import defaultdict

# Track cumulative availability per domain
domain_stats = defaultdict(lambda: {"up": 0, "total": 0})

# Parse domain and strip port
def get_domain(url):
    parsed = urlparse(url)
    return parsed.hostname

# Load config file
def load_config(path):
    with open(path, "r") as f:
        return yaml.safe_load(f)

# Perform a health check
def check(endpoint):
    url = endpoint["url"]
    method = endpoint.get("method", "GET").upper()
    headers = endpoint.get("headers", {})
    body = endpoint.get("body", None)
    domain = get_domain(url)

    domain_stats[domain]["total"] += 1

    try:
        start = time.time()
        response = requests.request(method, url, headers=headers, data=body, timeout=0.5)
        elapsed = (time.time() - start) * 1000  # ms
        
        print(f"[DEBUG] {url} - {response.status_code} - {elapsed:.2f}ms")
        if 200 <= response.status_code < 300 and elapsed <= 500:
            domain_stats[domain]["up"] += 1

    except requests.RequestException:
        pass  # Consider DOWN

# Log availability
def print_report():
    print("\n--- Availability Report ---")
    for domain, stats in domain_stats.items():
        total = stats["total"]
        up = stats["up"]
        availability = (up / total) * 100 if total else 0
        print(f"{domain}: {availability:.2f}%")
    print("---------------------------")

# Main monitoring loop
def monitor(path):
    config = load_config(path)
    while True:
        for endpoint in config:
            check(endpoint)
        print_report()
        time.sleep(15)

# CLI entry
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python main.py <config.yaml>")
        sys.exit(1)

    config_path = sys.argv[1]
    try:
        monitor(config_path)
    except KeyboardInterrupt:
        print("\nMonitoring stopped.")