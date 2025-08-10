# Flask Integration for AI DevOps Agent

This document explains how the AI DevOps Agent has been integrated with Flask to provide a REST API interface.

## Overview

The Flask integration wraps the existing AI DevOps Agent pipeline in a web API, allowing you to:
- Process DevOps errors via HTTP requests
- Handle both synchronous and asynchronous processing
- Monitor job progress and retrieve results
- Integrate the agent with other systems and applications

## Key Changes Made

### 1. **New Dependencies Added**
- `flask` - Web framework for creating the API
- `flask-cors` - Cross-origin resource sharing support
- `requests` - HTTP client for testing

### 2. **Flask Application Structure**
- **`flask_agent_app.py`** - Main Flask application with all endpoints
- **`test_flask_agent.py`** - Test client to verify API functionality
- **Updated `requirements.txt`** - Added Flask dependencies

### 3. **API Endpoints Created**
- `GET /health` - Health check and service status
- `POST /process_errors` - Synchronous error processing
- `POST /process_errors_async` - Asynchronous error processing
- `GET /job_status/<job_id>` - Check background job status
- `GET /example_errors` - Get sample error scenarios for testing

### 4. **Integration Points**
- **Existing Agent Logic**: All original agent functionality is preserved
- **Tool Calling**: Maintains the existing tool calling approach
- **Error Handling**: Added comprehensive error handling and validation
- **Background Processing**: Supports long-running operations via threading

## Installation and Setup

### 1. **Install Dependencies**
```bash
cd version2
pip install -r requirements.txt
```

### 2. **Environment Configuration**
Ensure your `.env` file contains:
```env
OPEN_AI_API_KEY=your_openai_api_key_here
```

### 3. **Start the Flask Server**
```bash
python flask_agent_app.py
```
The server will start on `http://localhost:5000`

## API Usage Examples

### Health Check
```bash
curl http://localhost:5000/health
```

### Get Example Errors
```bash
curl http://localhost:5000/example_errors
```

### Process Errors Synchronously
```bash
curl -X POST http://localhost:5000/process_errors \
  -H "Content-Type: application/json" \
  -d '{
    "errors": [
      {
        "context": "[12:05:00] Error: Port 443 already in use"
      }
    ],
    "max_scenarios": 1
  }'
```

### Process Errors Asynchronously
```bash
curl -X POST http://localhost:5000/process_errors_async \
  -H "Content-Type: application/json" \
  -d '{
    "errors": [
      {
        "context": "[12:05:00] Error: Port 443 already in use"
      }
    ]
  }'
```

### Check Job Status
```bash
curl http://localhost:5000/job_status/job_20250810_120000_12345
```

## Testing the Integration

### 1. **Start the Flask Server**
```bash
python flask_agent_app.py
```

### 2. **Run the Test Client**
```bash
python test_flask_agent.py
```

The test client will:
- Verify the server is running
- Test all API endpoints
- Demonstrate synchronous and asynchronous processing
- Show detailed results and statistics

## Architecture Changes

### Before (Command Line Only)
```
User Input → Agent Pipeline → Console Output
```

### After (Flask API)
```
HTTP Request → Flask App → Agent Pipeline → JSON Response
                ↓
         Background Jobs → Status Monitoring
```

## Key Benefits of Flask Integration

### 1. **Web Accessibility**
- Access the agent from any HTTP client
- Integrate with web applications and dashboards
- Support for mobile and remote access

### 2. **Scalability**
- Asynchronous processing for long-running operations
- Background job management
- Progress monitoring and status tracking

### 3. **Integration Capabilities**
- REST API standard for easy integration
- JSON request/response format
- CORS support for cross-origin requests

### 4. **Error Handling**
- Comprehensive input validation
- Graceful error responses
- Detailed error logging and debugging

## Code Structure Explanation

### Flask App (`flask_agent_app.py`)
```python
# Key integration points:
from tool_calling.tool_calling_from_errors import generate_planned_actions_from_errors
from agent_tool_executor.tool_call_executor import handle_llm_plan_with_tools

# Maintains existing agent configuration
openai.api_key = os.getenv("OPEN_AI_API_KEY")
MODEL = "gpt-4o"
```

### Request Processing Flow
1. **Input Validation**: JSON payload validation and error handling
2. **Agent Integration**: Calls existing agent functions with minimal changes
3. **Response Formatting**: Converts agent output to structured JSON responses
4. **Error Handling**: Graceful handling of individual scenario failures

### Background Processing
- Uses Python threading for non-blocking operations
- Maintains job state in memory (can be extended to use databases)
- Provides progress tracking and status monitoring

## Extending the Integration

### 1. **Add New Endpoints**
```python
@app.route('/new_endpoint', methods=['POST'])
def new_functionality():
    # Your new logic here
    pass
```

### 2. **Database Integration**
- Replace in-memory storage with database persistence
- Add user authentication and authorization
- Implement request logging and analytics

### 3. **Advanced Features**
- Rate limiting and API key management
- WebSocket support for real-time updates
- Load balancing and clustering support

## Troubleshooting

### Common Issues

1. **Connection Refused**
   - Ensure Flask server is running on port 5000
   - Check firewall settings

2. **Import Errors**
   - Verify all dependencies are installed
   - Check Python path and module structure

3. **API Key Issues**
   - Verify `.env` file configuration
   - Check OpenAI API key validity

### Debug Mode
The Flask app runs in debug mode by default, providing detailed error information and automatic reloading.

## Performance Considerations

### 1. **Synchronous vs Asynchronous**
- Use synchronous processing for quick operations (< 30 seconds)
- Use asynchronous processing for long-running tasks

### 2. **Resource Management**
- Background jobs are cleaned up after 1 hour
- Monitor memory usage for large error batches
- Consider implementing job queuing for high-volume scenarios

### 3. **Scaling**
- For production use, consider using Gunicorn or uWSGI
- Implement proper logging and monitoring
- Add health checks and metrics collection

## Security Considerations

### 1. **Input Validation**
- All inputs are validated before processing
- JSON payload structure is enforced
- Error messages don't expose internal system details

### 2. **CORS Configuration**
- CORS is enabled for development
- Restrict origins for production deployment
- Consider implementing API key authentication

### 3. **Error Handling**
- Internal errors are logged but not exposed to clients
- Graceful degradation for failed scenarios
- No sensitive information in error responses

## Conclusion

The Flask integration successfully transforms the AI DevOps Agent from a command-line tool to a web service while preserving all existing functionality. The integration provides:

- **Minimal Code Changes**: Existing agent logic remains largely unchanged
- **Web Accessibility**: REST API interface for easy integration
- **Scalability**: Support for both sync and async processing
- **Robustness**: Comprehensive error handling and validation
- **Extensibility**: Easy to add new features and endpoints

This approach allows you to leverage the power of the AI DevOps Agent in web applications, CI/CD pipelines, monitoring systems, and other automated workflows. 
