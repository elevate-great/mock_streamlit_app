#!/usr/bin/env python3
"""
Simple command-line stress tester for Wagtail pages
Usage: python stress_test_simple.py <url> <num_requests> <concurrent_workers>
"""
import sys
import time
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List
import statistics

def load_page(page_url: str, request_id: int = 0) -> Dict:
    """Load a full page and return results"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    start_time = time.time()
    error = None
    status_code = 0
    success = False
    content_length = 0
    
    try:
        response = requests.get(page_url, headers=headers, timeout=60, allow_redirects=True)
        status_code = response.status_code
        content_length = len(response.content)
        success = status_code < 400
        
    except requests.exceptions.Timeout:
        error = "Page load timeout (60s)"
    except requests.exceptions.ConnectionError:
        error = "Connection error"
    except requests.exceptions.RequestException as e:
        error = str(e)
    except Exception as e:
        error = f"Unexpected error: {str(e)}"
    
    response_time = time.time() - start_time
    
    return {
        'request_id': request_id,
        'status_code': status_code,
        'response_time': response_time,
        'success': success,
        'error': error,
        'content_length': content_length
    }


def run_stress_test(page_url: str, num_requests: int, concurrent_workers: int) -> List[Dict]:
    """Run concurrent page load stress test"""
    results = []
    
    print(f"Starting stress test...")
    print(f"URL: {page_url}")
    print(f"Requests: {num_requests}")
    print(f"Concurrent workers: {concurrent_workers}")
    print("-" * 60)
    
    with ThreadPoolExecutor(max_workers=concurrent_workers) as executor:
        futures = []
        
        for i in range(num_requests):
            future = executor.submit(load_page, page_url=page_url, request_id=i + 1)
            futures.append(future)
        
        completed = 0
        for future in as_completed(futures):
            result = future.result()
            results.append(result)
            completed += 1
            if completed % 10 == 0 or completed == num_requests:
                print(f"Progress: {completed}/{num_requests} requests completed", end='\r')
    
    print()  # New line after progress
    return results


def print_results(results: List[Dict]):
    """Print test results summary"""
    total = len(results)
    successful = sum(1 for r in results if r['success'])
    failed = total - successful
    success_rate = (successful / total * 100) if total > 0 else 0
    
    response_times = [r['response_time'] for r in results]
    avg_time = statistics.mean(response_times) if response_times else 0
    min_time = min(response_times) if response_times else 0
    max_time = max(response_times) if response_times else 0
    median_time = statistics.median(response_times) if response_times else 0
    
    # Status code distribution
    status_codes = {}
    for r in results:
        code = r['status_code']
        status_codes[code] = status_codes.get(code, 0) + 1
    
    print("\n" + "=" * 60)
    print("STRESS TEST RESULTS")
    print("=" * 60)
    print(f"Total Requests:     {total}")
    print(f"Successful:         {successful} ({success_rate:.1f}%)")
    print(f"Failed:             {failed}")
    print(f"\nResponse Times:")
    print(f"  Average:          {avg_time:.3f}s")
    print(f"  Median:           {median_time:.3f}s")
    print(f"  Min:              {min_time:.3f}s")
    print(f"  Max:              {max_time:.3f}s")
    
    if status_codes:
        print(f"\nStatus Codes:")
        for code, count in sorted(status_codes.items()):
            print(f"  {code}: {count} requests")
    
    # Show errors if any
    errors = [r for r in results if r['error']]
    if errors:
        print(f"\nErrors ({len(errors)}):")
        error_types = {}
        for r in errors:
            error = r['error']
            error_types[error] = error_types.get(error, 0) + 1
        for error, count in error_types.items():
            print(f"  {error}: {count}")
    
    print("=" * 60)


def main():
    if len(sys.argv) != 4:
        print("Usage: python stress_test_simple.py <url> <num_requests> <concurrent_workers>")
        print("\nExample:")
        print("  python stress_test_simple.py https://your-wagtail-site.com/dashboard-page 10 20")
        sys.exit(1)
    
    page_url = sys.argv[1]
    try:
        num_requests = int(sys.argv[2])
        concurrent_workers = int(sys.argv[3])
    except ValueError:
        print("Error: num_requests and concurrent_workers must be integers")
        sys.exit(1)
    
    if num_requests < 1:
        print("Error: num_requests must be at least 1")
        sys.exit(1)
    
    if concurrent_workers < 1:
        print("Error: concurrent_workers must be at least 1")
        sys.exit(1)
    
    # Run the stress test
    results = run_stress_test(page_url, num_requests, concurrent_workers)
    
    # Print results
    print_results(results)


if __name__ == "__main__":
    main()

