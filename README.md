# Wagtail Integration Stress Tester

A Streamlit application designed to stress test Wagtail dashboard page integrations by simulating concurrent HTTP requests and measuring performance metrics.

## Features

- **Dual Testing Modes**: 
  - **API Endpoint Testing**: Test Wagtail API endpoints with configurable concurrent workers
  - **Page Load Testing**: Test full page loads (perfect for testing embedded Streamlit apps)
- **Multiple HTTP Methods**: Support for GET, POST, PUT, and DELETE requests
- **Performance Metrics**: Track response times, success rates, and error rates
- **Real-time Visualization**: Charts and graphs showing response time distribution and status codes
- **Test History**: Keep track of previous test runs for comparison
- **Error Tracking**: Detailed error reporting with response text
- **Deployment Ready**: Includes configuration for Streamlit Community Cloud deployment
- **Embedding Support**: Designed to test Wagtail pages with embedded Streamlit apps

## Installation

1. Create a virtual environment (if not already created):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Start the Streamlit app:
```bash
streamlit run streamlit_app.py
```

2. Configure your test parameters in the sidebar:
   - **Test Mode**: Choose between "API Endpoint" or "Page Load (Embedded)"
   - **For API Testing**:
     - **Base URL**: Your Wagtail instance URL (e.g., `http://localhost:8000` or `https://your-wagtail-site.com`)
     - **API Endpoint**: The API endpoint path (e.g., `/api/v2/pages/` or `/wagtail/api/v2/pages/`)
     - **HTTP Method**: GET, POST, PUT, or DELETE
     - **Request Payload**: JSON payload for POST/PUT requests
   - **For Page Load Testing**:
     - **Page URL**: Full URL of the Wagtail page with embedded Streamlit app (e.g., `https://your-site.com/dashboard/test/`)
   - **Common Settings**:
     - **Authentication**: Optional API token if your Wagtail API requires authentication
     - **Number of Requests**: Total requests to send (1-1000)
     - **Concurrent Workers**: Number of simultaneous requests (1-100)
     - **Delay Between Requests**: Optional delay in milliseconds

3. Click "Start Stress Test" to run the test

4. View results in the "Results" tab:
   - Summary metrics (success rate, response times)
   - Response time distribution chart
   - Status code distribution
   - Detailed results table
   - Error analysis

5. Review test history in the "History" tab

## Example Test Scenarios

### Scenario 1: Basic Load Test
- **Method**: GET
- **Requests**: 100
- **Concurrent Workers**: 10
- **Purpose**: Test how your Wagtail API handles moderate concurrent read requests

### Scenario 2: Heavy Load Test
- **Method**: GET
- **Requests**: 500
- **Concurrent Workers**: 50
- **Purpose**: Stress test with high concurrency

### Scenario 3: Dashboard Creation Test
- **Method**: POST
- **Requests**: 50
- **Concurrent Workers**: 5
- **Payload**: `{"title": "Test Dashboard", "type": "dashboard.DashboardPage"}`
- **Purpose**: Test concurrent dashboard page creation

### Scenario 4: Embedded Page Load Test
- **Mode**: Page Load (Embedded)
- **Page URL**: `https://your-wagtail-site.com/dashboard/test-dashboard/`
- **Requests**: 100
- **Concurrent Workers**: 10
- **Purpose**: Test how the Wagtail page with embedded Streamlit app handles concurrent users

### Scenario 5: Mixed Operations
Run multiple tests with different methods to simulate real-world usage patterns.

## Interpreting Results

- **Success Rate**: Percentage of requests that returned HTTP status codes < 400
- **Response Time**: Time taken for each request (min, max, average, median)
- **Status Code Distribution**: Breakdown of HTTP status codes returned
- **Error Analysis**: Detailed error messages for failed requests

## Tips for Effective Stress Testing

1. **Start Small**: Begin with fewer requests and lower concurrency to establish a baseline
2. **Gradually Increase**: Incrementally increase load to find breaking points
3. **Monitor Your Server**: Watch your Wagtail server logs and resource usage during tests
4. **Test Different Endpoints**: Test various API endpoints to find bottlenecks
5. **Use Realistic Payloads**: Use actual payload structures that match your production data
6. **Test During Off-Peak Hours**: Avoid impacting production users

## Troubleshooting

- **Connection Errors**: Verify your base URL and that the Wagtail server is running
- **Authentication Errors**: Check that your API token is correct and has proper permissions
- **Timeout Errors**: Your server may be overloaded; reduce concurrent workers or add delays
- **404 Errors**: Verify the API endpoint path is correct for your Wagtail version

## Deployment & Embedding

### Deploy to Streamlit Community Cloud

This app is ready to deploy to Streamlit Community Cloud! See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions.

Quick steps:
1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repository and deploy
4. Your app will be available at `https://your-app-name.streamlit.app`

### Embed in Wagtail

Once deployed, you can embed this stress tester (or any Streamlit app) in your Wagtail pages. See [WAGTAIL_EMBEDDING.md](WAGTAIL_EMBEDDING.md) for complete instructions.

**Workflow:**
1. Deploy the stress tester to Streamlit Community Cloud
2. Embed it in a Wagtail page using an iframe
3. Use the stress tester to test the embedded page itself (meta-testing!)
4. Test your actual dashboard pages that have embedded Streamlit apps

## Requirements

- Python 3.8+
- Streamlit 1.47.0+
- pandas 2.3.2+
- requests 2.31.0+
- numpy 1.24.0+

## Project Structure

```
mock_sl_app/
├── streamlit_app.py          # Main Streamlit application
├── requirements.txt           # Python dependencies
├── README.md                 # This file
├── DEPLOYMENT.md             # Streamlit Cloud deployment guide
├── WAGTAIL_EMBEDDING.md      # Wagtail embedding guide
└── .streamlit/
    └── config.toml          # Streamlit configuration
```
