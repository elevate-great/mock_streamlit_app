# streamlit_app.py - Wagtail Integration Stress Tester
import time
import pandas as pd
import numpy as np
import streamlit as st
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import json
from typing import List, Dict, Optional

st.set_page_config(page_title="Wagtail Stress Tester", page_icon="⚡", layout="wide")
st.title("⚡ Wagtail Integration Stress Tester")
st.caption("Stress test your Wagtail dashboard page integration with concurrent requests")

# Initialize session state
if 'test_results' not in st.session_state:
    st.session_state.test_results = []
if 'test_history' not in st.session_state:
    st.session_state.test_history = []

# --- Sidebar Configuration
st.sidebar.header("⚙️ Test Configuration")

# Test Mode Selection
test_mode = st.sidebar.radio(
    "Test Mode",
    options=["API Endpoint", "Page Load (Embedded)"],
    help="Test API endpoints or full page loads (for embedded Streamlit apps)"
)

# Initialize variables
page_url = ""
base_url = ""
api_endpoint = ""

if test_mode == "API Endpoint":
    # Wagtail API Configuration
    st.sidebar.subheader("Wagtail API Settings")
    base_url = st.sidebar.text_input(
        "Base URL", 
        value="http://localhost:8000",
        help="Base URL of your Wagtail instance"
    )

    api_endpoint = st.sidebar.text_input(
        "API Endpoint", 
        value="/api/v2/pages/",
        help="API endpoint path (e.g., /api/v2/pages/ or /wagtail/api/v2/pages/)"
    )
    target_url = f"{base_url.rstrip('/')}/{api_endpoint.lstrip('/')}"
else:
    # Page Load Configuration
    st.sidebar.subheader("Page Load Settings")
    st.sidebar.info("Test the Wagtail page where your Streamlit app is embedded")
    
    page_url = st.sidebar.text_input(
        "Page URL", 
        value="http://localhost:8000/dashboard/test-dashboard/",
        help="Full URL of the Wagtail page with embedded Streamlit app"
    )
    target_url = page_url
    base_url = page_url.split('/')[0] + '//' + page_url.split('/')[2] if len(page_url.split('/')) > 2 else page_url
    api_endpoint = ""

# Authentication (optional)
use_auth = st.sidebar.checkbox("Use Authentication", value=False)
auth_token = None
if use_auth:
    auth_token = st.sidebar.text_input("API Token", type="password", help="Bearer token or API key")

# Test Parameters
st.sidebar.subheader("Test Parameters")
num_requests = st.sidebar.slider(
    "Number of Requests", 
    min_value=1, 
    max_value=1000, 
    value=50,
    help="Total number of requests to send"
)

concurrent_workers = st.sidebar.slider(
    "Concurrent Workers", 
    min_value=1, 
    max_value=100, 
    value=10,
    help="Number of concurrent requests"
)

request_method = None
if test_mode == "API Endpoint":
    request_method = st.sidebar.selectbox(
        "HTTP Method",
        options=["GET", "POST", "PUT", "DELETE"],
        index=0,
        help="HTTP method to use for requests"
    )

# Request delay
delay_between_requests = st.sidebar.slider(
    "Delay Between Requests (ms)",
    min_value=0,
    max_value=1000,
    value=0,
    help="Delay in milliseconds between requests (0 = no delay)"
)

# Request payload for POST/PUT
request_payload = None
if test_mode == "API Endpoint" and request_method and request_method in ["POST", "PUT"]:
    st.sidebar.subheader("Request Payload")
    payload_text = st.sidebar.text_area(
        "JSON Payload",
        value='{"title": "Test Dashboard", "type": "dashboard.DashboardPage"}',
        help="JSON payload for POST/PUT requests"
    )
    try:
        request_payload = json.loads(payload_text)
    except json.JSONDecodeError:
        st.sidebar.error("Invalid JSON payload")
        request_payload = None

# --- Main Content
tab1, tab2, tab3 = st.tabs(["🚀 Run Test", "📊 Results", "📈 History"])

# Tab 1: Run Test
with tab1:
    st.subheader("Stress Test Configuration")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Requests", num_requests)
    with col2:
        st.metric("Concurrent Workers", concurrent_workers)
    with col3:
        if test_mode == "API Endpoint":
            st.metric("HTTP Method", request_method)
        else:
            st.metric("Test Mode", "Page Load")
    
    st.info(f"**Target URL:** `{target_url}`")
    
    if st.button("🚀 Start Stress Test", type="primary", use_container_width=True):
        if test_mode == "API Endpoint" and (not base_url or not api_endpoint):
            st.error("Please configure the base URL and API endpoint")
        elif test_mode == "Page Load" and not page_url:
            st.error("Please configure the page URL")
        else:
            with st.spinner("Running stress test..."):
                if test_mode == "API Endpoint":
                    results = run_stress_test(
                        base_url=base_url,
                        endpoint=api_endpoint,
                        num_requests=num_requests,
                        concurrent_workers=concurrent_workers,
                        method=request_method,
                        payload=request_payload,
                        auth_token=auth_token,
                        delay_ms=delay_between_requests
                    )
                else:
                    results = run_page_load_test(
                        page_url=page_url,
                        num_requests=num_requests,
                        concurrent_workers=concurrent_workers,
                        auth_token=auth_token,
                        delay_ms=delay_between_requests
                    )
                
                # Store results
                test_timestamp = datetime.now().isoformat()
                test_summary = {
                    "timestamp": test_timestamp,
                    "config": {
                        "test_mode": test_mode,
                        "base_url": base_url if test_mode == "API Endpoint" else (page_url if page_url else ""),
                        "endpoint": api_endpoint if test_mode == "API Endpoint" else "",
                        "target_url": target_url,
                        "num_requests": num_requests,
                        "concurrent_workers": concurrent_workers,
                        "method": request_method if test_mode == "API Endpoint" else "GET"
                    },
                    "results": results
                }
                st.session_state.test_results = results
                st.session_state.test_history.append(test_summary)
                
                st.success(f"✅ Stress test completed! Processed {len(results)} requests.")
                st.rerun()

# Tab 2: Results
with tab2:
    if st.session_state.test_results:
        results = st.session_state.test_results
        
        # Calculate metrics
        total_requests = len(results)
        successful = sum(1 for r in results if r['status_code'] < 400)
        failed = total_requests - successful
        success_rate = (successful / total_requests * 100) if total_requests > 0 else 0
        
        response_times = [r['response_time'] for r in results]
        avg_response_time = np.mean(response_times) if response_times else 0
        min_response_time = np.min(response_times) if response_times else 0
        max_response_time = np.max(response_times) if response_times else 0
        median_response_time = np.median(response_times) if response_times else 0
        
        # Status code distribution
        status_codes = {}
        for r in results:
            code = r['status_code']
            status_codes[code] = status_codes.get(code, 0) + 1
        
        # Display metrics
        st.subheader("📊 Test Results Summary")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Requests", total_requests)
        with col2:
            st.metric("Success Rate", f"{success_rate:.1f}%", f"{successful} successful")
        with col3:
            st.metric("Failed Requests", failed, delta=f"{(failed/total_requests*100):.1f}%" if total_requests > 0 else "0%")
        with col4:
            st.metric("Avg Response Time", f"{avg_response_time:.2f}s")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Min Response Time", f"{min_response_time:.3f}s")
        with col2:
            st.metric("Max Response Time", f"{max_response_time:.3f}s")
        with col3:
            st.metric("Median Response Time", f"{median_response_time:.3f}s")
        
        # Response time distribution
        st.subheader("⏱️ Response Time Distribution")
        response_time_df = pd.DataFrame({
            'Request #': range(1, len(response_times) + 1),
            'Response Time (s)': response_times
        })
        st.line_chart(response_time_df.set_index('Request #'))
        
        # Status code distribution
        st.subheader("📈 Status Code Distribution")
        if status_codes:
            status_df = pd.DataFrame({
                'Status Code': list(status_codes.keys()),
                'Count': list(status_codes.values())
            })
            st.bar_chart(status_df.set_index('Status Code'))
        
        # Detailed results table
        st.subheader("📋 Detailed Results")
        results_df = pd.DataFrame(results)
        display_cols = ['request_id', 'status_code', 'response_time', 'success', 'error']
        if 'content_length' in results_df.columns:
            display_cols.insert(3, 'content_length')
        st.dataframe(
            results_df[display_cols],
            use_container_width=True
        )
        
        # Error analysis
        errors = [r for r in results if r['error']]
        if errors:
            st.subheader("❌ Errors")
            for error in errors[:10]:  # Show first 10 errors
                with st.expander(f"Request #{error['request_id']} - {error['error']}"):
                    st.code(error.get('response_text', 'No response'), language='text')
    else:
        st.info("No test results yet. Run a stress test from the 'Run Test' tab.")

# Tab 3: History
with tab3:
    if st.session_state.test_history:
        st.subheader("📈 Test History")
        
        for i, test in enumerate(reversed(st.session_state.test_history[-10:])):  # Show last 10 tests
            with st.expander(f"Test {len(st.session_state.test_history) - i} - {test['timestamp']}"):
                st.json(test['config'])
                
                results = test['results']
                if results:
                    total = len(results)
                    successful = sum(1 for r in results if r['status_code'] < 400)
                    avg_time = np.mean([r['response_time'] for r in results])
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total Requests", total)
                    with col2:
                        st.metric("Success Rate", f"{(successful/total*100):.1f}%")
                    with col3:
                        st.metric("Avg Response Time", f"{avg_time:.2f}s")
    else:
        st.info("No test history yet. Run some stress tests to see history here.")


# --- Helper Functions
def make_request(
    base_url: str,
    endpoint: str,
    method: str = "GET",
    payload: Optional[Dict] = None,
    auth_token: Optional[str] = None,
    request_id: int = 0
) -> Dict:
    """Make a single HTTP request and return results"""
    url = f"{base_url.rstrip('/')}/{endpoint.lstrip('/')}"
    headers = {}
    
    if auth_token:
        headers['Authorization'] = f'Bearer {auth_token}'
    
    if payload:
        headers['Content-Type'] = 'application/json'
    
    start_time = time.time()
    error = None
    status_code = 0
    response_text = ""
    success = False
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, timeout=30)
        elif method == "POST":
            response = requests.post(url, json=payload, headers=headers, timeout=30)
        elif method == "PUT":
            response = requests.put(url, json=payload, headers=headers, timeout=30)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers, timeout=30)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        status_code = response.status_code
        response_text = response.text[:500]  # Limit response text
        success = status_code < 400
        
    except requests.exceptions.Timeout:
        error = "Request timeout"
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
        'response_text': response_text
    }


def run_stress_test(
    base_url: str,
    endpoint: str,
    num_requests: int,
    concurrent_workers: int,
    method: str = "GET",
    payload: Optional[Dict] = None,
    auth_token: Optional[str] = None,
    delay_ms: int = 0
) -> List[Dict]:
    """Run concurrent stress test"""
    results = []
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    with ThreadPoolExecutor(max_workers=concurrent_workers) as executor:
        futures = []
        
        for i in range(num_requests):
            if delay_ms > 0 and i > 0:
                time.sleep(delay_ms / 1000.0)
            
            future = executor.submit(
                make_request,
                base_url=base_url,
                endpoint=endpoint,
                method=method,
                payload=payload,
                auth_token=auth_token,
                request_id=i + 1
            )
            futures.append(future)
        
        completed = 0
        for future in as_completed(futures):
            result = future.result()
            results.append(result)
            completed += 1
            progress_bar.progress(completed / num_requests)
            status_text.text(f"Completed {completed}/{num_requests} requests...")
    
    progress_bar.empty()
    status_text.empty()
    
    return results


def load_page(
    page_url: str,
    auth_token: Optional[str] = None,
    request_id: int = 0
) -> Dict:
    """Load a full page and return results"""
    headers = {}
    
    if auth_token:
        headers['Authorization'] = f'Bearer {auth_token}'
    
    # Set user agent to simulate browser
    headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    
    start_time = time.time()
    error = None
    status_code = 0
    response_text = ""
    success = False
    content_length = 0
    
    try:
        response = requests.get(page_url, headers=headers, timeout=60, allow_redirects=True)
        status_code = response.status_code
        content_length = len(response.content)
        response_text = response.text[:1000]  # Limit response text
        success = status_code < 400
        
        # Check if Streamlit iframe is present (basic check)
        has_streamlit_iframe = 'streamlit' in response.text.lower() or 'iframe' in response.text.lower()
        
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
        'response_text': response_text,
        'content_length': content_length
    }


def run_page_load_test(
    page_url: str,
    num_requests: int,
    concurrent_workers: int,
    auth_token: Optional[str] = None,
    delay_ms: int = 0
) -> List[Dict]:
    """Run concurrent page load stress test"""
    results = []
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    with ThreadPoolExecutor(max_workers=concurrent_workers) as executor:
        futures = []
        
        for i in range(num_requests):
            if delay_ms > 0 and i > 0:
                time.sleep(delay_ms / 1000.0)
            
            future = executor.submit(
                load_page,
                page_url=page_url,
                auth_token=auth_token,
                request_id=i + 1
            )
            futures.append(future)
        
        completed = 0
        for future in as_completed(futures):
            result = future.result()
            results.append(result)
            completed += 1
            progress_bar.progress(completed / num_requests)
            status_text.text(f"Completed {completed}/{num_requests} page loads...")
    
    progress_bar.empty()
    status_text.empty()
    
    return results
