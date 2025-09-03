import os
import time
import requests
from dotenv import load_dotenv
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
from tabulate import tabulate

# Load environment variables
load_dotenv()

# Configurable values from .env
TIMEOUT = int(os.getenv("TIMEOUT", 30))  # Default 30s
URL_FILE = os.getenv("URL_FILE", "endpoints.txt")  # Default file name
MAX_WORKERS = int(os.getenv("MAX_WORKERS", 10))  # Default 10 workers

def check_endpoint(url: str, timeout: int):
    """Check endpoint response time and availability."""
    try:
        start = time.time()
        response = requests.get(url, timeout=timeout)
        elapsed = round(time.time() - start, 2)
        return {
            "url": url,
            "status": response.status_code,
            "time": elapsed,
            "result": "UP" if elapsed <= timeout else "TIMEOUT"
        }
    except requests.exceptions.Timeout:
        return {"url": url, "status": None, "time": None, "result": "TIMEOUT"}
    except requests.exceptions.RequestException as e:
        return {"url": url, "status": None, "time": None, "result": f"DOWN ({e.__class__.__name__})"}

def main():
    if not os.path.exists(URL_FILE):
        print(f"❌ URL file '{URL_FILE}' not found!")
        return

    with open(URL_FILE, "r") as f:
        urls = [
            line.strip()
            for line in f
            if line.strip() and not line.strip().startswith("#")
        ]

    print(f"🔍 Checking {len(urls)} endpoints concurrently (max_workers={MAX_WORKERS}, timeout={TIMEOUT}s)...\n")

    results = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_url = {executor.submit(check_endpoint, url, TIMEOUT): url for url in urls}
        for future in tqdm(as_completed(future_to_url), total=len(urls), desc="Progress", ncols=100):
            results.append(future.result())

    # Prepare data for tabulate
    table_data = []
    for res in results:
        table_data.append([
            res['url'],
            res['result'],
            res['status'] if res['status'] else "-",
            f"{res['time']}s" if res['time'] else "-"
        ])

    print("\n📊 Results:")
    print(tabulate(table_data, headers=["Endpoint", "Result", "HTTP Status", "Response Time"], tablefmt="fancy_grid"))

if __name__ == "__main__":
    main()
