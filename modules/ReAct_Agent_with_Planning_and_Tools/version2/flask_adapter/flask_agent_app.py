# flask_agent_app.py
# IMPORTANT: Run this file directly with Python, NOT through Cursor's debugger
#
# API FORMAT FOR SENDING ERRORS:
# POST /process_errors
# {
#   "errors": [
#     {
#       "context": "Your error log content here with surrounding context lines and timestamps"
#     }
#   ]
# }
#
# POST /process_errors_async  
# {
#   "errors": [
#     {
#       "context": "Your error log content here with surrounding context lines and timestamps"
#     }
#   ]
# }

import os
import sys
import json
import threading
import queue
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS

# Add the parent directory to Python path to find the agent modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent_tool_executor.tool_call_executor import handle_llm_plan_with_tools
from tool_calling.tool_calling_from_errors import generate_planned_actions_from_errors

# Force disable debug mode
os.environ['FLASK_ENV'] = 'production'
os.environ['FLASK_DEBUG'] = '0'

app = Flask(__name__)
CORS(app)

# Global queue for managing background jobs
job_queue = queue.Queue()
jobs = {}

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint to verify the service is running"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'AI DevOps Agent Flask API'
    })

@app.route('/process_errors', methods=['POST'])
def process_errors():
    """Process errors synchronously - returns results immediately"""
    try:
        data = request.get_json()
        
        if not data or 'errors' not in data:
            return jsonify({'error': 'Invalid request format. Expected {"errors": [...]}'}), 400
        
        errors = data['errors']
        if not errors:
            return jsonify({'error': 'No errors provided'}), 400
        
        # Process the first error (for simplicity)
        error_context = errors[0].get('context', '')
        if not error_context:
            return jsonify({'error': 'Error context is required'}), 400
        
        print(f"🔍 Processing error: {error_context}")
        
        # Generate planned actions using the agent
        planned_actions = generate_planned_actions_from_errors([error_context])
        
        # Execute the plan with tools
        results = handle_llm_plan_with_tools(planned_actions)
        
        return jsonify({
            'status': 'completed',
            'error_context': error_context,
            'planned_actions': planned_actions,
            'results': results,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"❌ Error processing request: {str(e)}")
        return jsonify({
            'error': f'Internal server error: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/process_errors_async', methods=['POST'])
def process_errors_async():
    """Process errors asynchronously - returns job ID immediately, results later"""
    try:
        data = request.get_json()
        
        if not data or 'errors' not in data:
            return jsonify({'error': 'Invalid request format. Expected {"errors": [...]}'}), 400
        
        errors = data['errors']
        if not errors:
            return jsonify({'error': 'No errors provided'}), 400
        
        # Generate a unique job ID
        job_id = f"job_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(jobs)}"
        
        # Store job info
        jobs[job_id] = {
            'status': 'running',
            'started_at': datetime.now().isoformat(),
            'error_context': errors[0].get('context', ''),
            'progress': 0
        }
        
        # Start background processing
        def process_job():
            try:
                error_context = errors[0].get('context', '')
                print(f"🔍 Processing error asynchronously: {error_context}")
                
                # Update progress
                jobs[job_id]['progress'] = 25
                
                # Generate planned actions
                planned_actions = generate_planned_actions_from_errors([error_context])
                jobs[job_id]['progress'] = 50
                
                # Execute the plan with tools
                results = handle_llm_plan_with_tools(planned_actions)
                jobs[job_id]['progress'] = 100
                
                # Update job status
                jobs[job_id].update({
                    'status': 'completed',
                    'completed_at': datetime.now().isoformat(),
                    'planned_actions': planned_actions,
                    'results': results
                })
                
                print(f"✅ Job {job_id} completed successfully")
                
            except Exception as e:
                print(f"❌ Error in job {job_id}: {str(e)}")
                jobs[job_id].update({
                    'status': 'failed',
                    'completed_at': datetime.now().isoformat(),
                    'error': str(e)
                })
        
        # Start the background thread
        thread = threading.Thread(target=process_job)
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'status': 'accepted',
            'job_id': job_id,
            'message': 'Job started successfully',
            'timestamp': datetime.now().isoformat()
        }), 202
        
    except Exception as e:
        print(f"❌ Error starting async job: {str(e)}")
        return jsonify({
            'error': f'Internal server error: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/job_status/<job_id>', methods=['GET'])
def job_status(job_id):
    """Check the status of an asynchronous job"""
    if job_id not in jobs:
        return jsonify({'error': 'Job not found'}), 404
    
    job = jobs[job_id]
    return jsonify(job)

@app.route('/example_errors', methods=['GET'])
def example_errors():
    """Get example error scenarios for testing with realistic log context"""
    examples = [
        {
            "context": """2025-08-10 14:23:15 [INFO] Starting Docker container build for service 'webapp'
2025-08-10 14:23:16 [INFO] Building image from Dockerfile...
2025-08-10 14:23:18 [INFO] Step 1/8 : FROM python:3.9-slim
2025-08-10 14:23:19 [INFO] Step 2/8 : COPY requirements.txt .
2025-08-10 14:23:20 [ERROR] failed to compute cache key: "/requirements.txt" not found: not found
2025-08-10 14:23:21 [ERROR] Build failed with exit code 1
2025-08-10 14:23:22 [INFO] Cleaning up build context
2025-08-10 14:23:23 [INFO] Build process terminated""",
            "description": "Docker build failure - missing requirements.txt file"
        },
        {
            "context": """2025-08-10 15:45:12 [INFO] Kubernetes deployment 'nginx-app' starting
2025-08-10 15:45:13 [INFO] Pod 'nginx-app-7d8f9c4b5' created
2025-08-10 15:45:14 [INFO] Pod 'nginx-app-7d8f9c4b5' scheduled on node 'worker-01'
2025-08-10 15:45:15 [WARN] Pod 'nginx-app-7d8f9c4b5' Pending - insufficient memory
2025-08-10 15:45:16 [ERROR] Pod 'nginx-app-7d8f9c4b5' failed to start: 0/1 nodes are available: 1 Insufficient memory
2025-08-10 15:45:17 [INFO] Retrying pod creation...
2025-08-10 15:45:18 [INFO] Pod 'nginx-app-7d8f9c4b6' created""",
            "description": "Kubernetes pod scheduling failure - insufficient memory"
        },
        {
            "context": """2025-08-10 16:12:33 [INFO] Git merge operation started
2025-08-10 16:12:34 [INFO] Merging branch 'feature/user-auth' into 'main'
2025-08-10 16:12:35 [INFO] Auto-merging src/auth/login.py
2025-08-10 16:12:36 [ERROR] CONFLICT (content): Merge conflict in src/auth/login.py
2025-08-10 16:12:37 [ERROR] Automatic merge failed; fix conflicts and then commit the result
2025-08-10 16:12:38 [INFO] Merge process halted - manual resolution required
2025-08-10 16:12:39 [INFO] Current branch: main (unmerged)""",
            "description": "Git merge conflict in authentication module"
        },
        {
            "context": """2025-08-10 17:28:45 [INFO] Database connection pool initialized
2025-08-10 17:28:46 [INFO] Attempting to connect to PostgreSQL database
2025-08-10 17:28:47 [INFO] Connection attempt 1/3...
2025-08-10 17:28:50 [WARN] Connection timeout after 3 seconds
2025-08-10 17:28:51 [INFO] Connection attempt 2/3...
2025-08-10 17:28:54 [WARN] Connection timeout after 3 seconds
2025-08-10 17:28:55 [ERROR] Database connection failed: timeout after 30 seconds
2025-08-10 17:28:56 [ERROR] Failed to establish database connection
2025-08-10 17:28:57 [INFO] Retrying in 60 seconds...""",
            "description": "Database connection timeout - network or configuration issue"
        },
        {
            "context": """2025-08-10 18:55:22 [INFO] CI/CD pipeline started for commit a1b2c3d
2025-08-10 18:55:23 [INFO] Stage 1: Code checkout - SUCCESS
2025-08-10 18:55:24 [INFO] Stage 2: Dependency installation - SUCCESS
2025-08-10 18:55:25 [INFO] Stage 3: Code quality checks - SUCCESS
2025-08-10 18:55:26 [INFO] Stage 4: Unit tests - SUCCESS
2025-08-10 18:55:27 [INFO] Stage 5: Build process - STARTED
2025-08-10 18:55:28 [ERROR] Build failed: npm install failed with exit code 1
2025-08-10 18:55:29 [ERROR] npm ERR! code ENOENT
2025-08-10 18:55:30 [ERROR] npm ERR! syscall open
2025-08-10 18:55:31 [ERROR] npm ERR! path /app/package.json
2025-08-10 18:55:32 [ERROR] npm ERR! errno -2
2025-08-10 18:55:33 [ERROR] npm ERR! enoent ENOENT: no such file or directory, open 'package.json'
2025-08-10 18:55:34 [INFO] Build stage failed - pipeline terminated""",
            "description": "CI/CD build failure - missing package.json file"
        }
    ]
    
    return jsonify({
        'examples': examples,
        'usage': 'Send POST to /process_errors with {"errors": [{"context": "your error log here"}]}',
        'format_explanation': 'Each example includes context lines before and after the error with timestamps for realistic testing'
    })

@app.route('/dashboard')
def dashboard():
    """Dashboard endpoint serving the web interface"""
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AI DevOps Agent Dashboard</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                color: #333;
            }
            
            .container {
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
            }
            
            .header {
                text-align: center;
                color: white;
                margin-bottom: 30px;
            }
            
            .header h1 {
                font-size: 2.5rem;
                margin-bottom: 10px;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            }
            
            .header p {
                font-size: 1.2rem;
                opacity: 0.9;
            }
            
            .dashboard-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }
            
            .card {
                background: white;
                border-radius: 15px;
                padding: 25px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.1);
                transition: transform 0.3s ease;
            }
            
            .card:hover {
                transform: translateY(-5px);
            }
            
            .card h3 {
                color: #667eea;
                margin-bottom: 15px;
                font-size: 1.3rem;
                border-bottom: 2px solid #f0f0f0;
                padding-bottom: 10px;
            }
            
            .status-indicator {
                display: inline-block;
                width: 12px;
                height: 12px;
                border-radius: 50%;
                margin-right: 8px;
            }
            
            .status-online { 
                background: #4CAF50; 
            }
            
            .status-offline { 
                background: #f44336; 
            }
            
            .endpoint-list {
                list-style: none;
            }
            
            .endpoint-list li {
                padding: 8px 0;
                border-bottom: 1px solid #f0f0f0;
                font-family: monospace;
                font-size: 0.9rem;
            }
            
            .endpoint-list li:last-child {
                border-bottom: none;
            }
            
            .form-group {
                margin-bottom: 15px;
            }
            
            .form-group label {
                display: block;
                margin-bottom: 5px;
                font-weight: 600;
                color: #555;
            }
            
            .form-group input, 
            .form-group textarea, 
            .form-group select {
                width: 100%;
                padding: 12px;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                font-size: 14px;
                transition: border-color 0.3s ease;
            }
            
            .form-group input:focus, 
            .form-group textarea:focus, 
            .form-group select:focus {
                outline: none;
                border-color: #667eea;
            }
            
            .btn {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                padding: 12px 25px;
                border-radius: 8px;
                cursor: pointer;
                font-size: 16px;
                font-weight: 600;
                transition: transform 0.2s ease;
            }
            
            .btn:hover {
                transform: translateY(-2px);
            }
            
            .btn:disabled {
                opacity: 0.6;
                cursor: not-allowed;
                transform: none;
            }
            
            .response-area {
                background: #f8f9fa;
                border: 1px solid #e9ecef;
                border-radius: 8px;
                padding: 15px;
                margin-top: 15px;
                font-family: monospace;
                font-size: 0.9rem;
                max-height: 300px;
                overflow-y: auto;
                white-space: pre-wrap;
                min-height: 50px;
            }
            
            .response-area.empty {
                background: #f8f9fa;
                border: 1px dashed #dee2e6;
                color: #6c757d;
                font-style: italic;
                text-align: center;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            
            .response-area.empty::after {
                content: "Output will appear here...";
                color: #999;
                font-style: italic;
            }
            
            .loading {
                text-align: center;
                color: #666;
                font-style: italic;
            }
            
            .error {
                color: #f44336;
                background: #ffebee;
                padding: 10px;
                border-radius: 5px;
                margin-top: 10px;
            }
            
            .success {
                color: #4CAF50;
                background: #e8f5e8;
                padding: 10px;
                border-radius: 5px;
                margin-top: 10px;
            }
            
            .progress-bar {
                width: 100%;
                height: 20px;
                background: #e0e0e0;
                border-radius: 10px;
                overflow: hidden;
                margin-top: 10px;
            }
            
            .progress-fill {
                height: 100%;
                background: linear-gradient(90deg, #4CAF50, #8BC34A);
                transition: width 0.3s ease;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🤖 AI DevOps Agent Dashboard</h1>
                <p>Monitor, manage, and interact with your AI agent</p>
            </div>
            
            <div class="dashboard-grid">
                <!-- Agent Status Card -->
                <div class="card">
                    <h3>📊 Agent Status</h3>
                    <div id="agent-status">
                        <span class="status-indicator status-online"></span>
                        <strong>Online</strong>
                        <p style="margin-top: 10px; color: #666;">
                            Agent is running and ready to process requests
                        </p>
                    </div>
                </div>
                
                <!-- Available Endpoints Card -->
                <div class="card">
                    <h3>🔗 Available Endpoints</h3>
                    <ul class="endpoint-list">
                        <li><strong>GET</strong> /health - Health check</li>
                        <li><strong>POST</strong> /process_errors - Sync processing</li>
                        <li><strong>POST</strong> /process_errors_async - Async processing</li>
                        <li><strong>GET</strong> /job_status/{id} - Job status</li>
                        <li><strong>GET</strong> /example_errors - Sample data</li>
                        <li><strong>GET</strong> /dashboard - This interface</li>
                    </ul>
                </div>
                
                <!-- Quick Test Card -->
                <div class="card">
                    <h3>🧪 Quick Test</h3>
                    <div class="form-group">
                        <label for="test-endpoint">Test Endpoint:</label>
                        <select id="test-endpoint">
                            <option value="/health">/health</option>
                            <option value="/example_errors">/example_errors</option>
                        </select>
                    </div>
                    <button class="btn" onclick="testEndpoint()">Test Endpoint</button>
                    <div id="test-response" class="response-area empty"></div>
                </div>
                
                <!-- Error Processing Card -->
                <div class="card">
                    <h3>⚡ Process Errors</h3>
                    <div class="form-group">
                        <label for="error-context">Error Context:</label>
                        <textarea id="error-context" rows="3" placeholder="Enter error context here...">Docker build failed with out of memory error</textarea>
                    </div>
                    <div class="form-group">
                        <label for="processing-mode">Processing Mode:</label>
                        <select id="processing-mode">
                            <option value="sync">Synchronous</option>
                            <option value="async">Asynchronous</option>
                        </select>
                    </div>
                    <button class="btn" onclick="processErrors()">Process Errors</button>
                    <div id="processing-response" class="response-area empty"></div>
                </div>
                
                <!-- Job Monitoring Card -->
                <div class="card">
                    <h3>📈 Job Monitoring</h3>
                    <div class="form-group">
                        <label for="job-id">Job ID:</label>
                        <input type="text" id="job-id" placeholder="Enter job ID to monitor...">
                    </div>
                    <button class="btn" onclick="checkJobStatus()">Check Status</button>
                    <div id="job-response" class="response-area empty"></div>
                </div>
            </div>
        </div>

        <script>
            // Initialize response areas with empty state
            document.addEventListener('DOMContentLoaded', function() {
                const responseAreas = document.querySelectorAll('.response-area');
                responseAreas.forEach(area => {
                    if (!area.textContent.trim()) {
                        area.classList.add('empty');
                    }
                });
            });
            
            // Test endpoint function
            async function testEndpoint() {
                const endpoint = document.getElementById('test-endpoint').value;
                const responseDiv = document.getElementById('test-response');
                
                responseDiv.classList.remove('empty');
                responseDiv.innerHTML = '<div class="loading">Testing endpoint...</div>';
                
                try {
                    const response = await fetch(endpoint);
                    const data = await response.json();
                    
                    responseDiv.innerHTML = `<div class="success">✅ Success!</div>
<strong>Status:</strong> ${response.status}
<strong>Response:</strong>
${JSON.stringify(data, null, 2)}`;
                } catch (error) {
                    responseDiv.innerHTML = `<div class="error">❌ Error: ${error.message}</div>`;
                }
            }
            
            // Process errors function
            async function processErrors() {
                const context = document.getElementById('error-context').value;
                const mode = document.getElementById('processing-mode').value;
                const responseDiv = document.getElementById('processing-response');
                
                if (!context.trim()) {
                    alert('Please enter error context');
                    return;
                }
                
                responseDiv.classList.remove('empty');
                responseDiv.innerHTML = '<div class="loading">Processing errors...</div>';
                
                const data = {
                    errors: [{ context: context }]
                };
                
                try {
                    const endpoint = mode === 'async' ? '/process_errors_async' : '/process_errors';
                    const response = await fetch(endpoint, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify(data)
                    });
                    
                    const result = await response.json();
                    
                    if (response.status === 202 && mode === 'async') {
                        // Async response
                        responseDiv.innerHTML = `<div class="success">✅ Job started!</div>
<strong>Job ID:</strong> ${result.job_id}
<strong>Status:</strong> ${result.status}
<strong>Message:</strong> ${result.message}`;
                    } else {
                        // Sync response
                        responseDiv.innerHTML = `<div class="success">✅ Processing completed!</div>
<strong>Status:</strong> ${response.status}
<strong>Response:</strong>
${JSON.stringify(result, null, 2)}`;
                    }
                } catch (error) {
                    responseDiv.innerHTML = `<div class="error">❌ Error: ${error.message}</div>`;
                }
            }
            
            // Check job status function
            async function checkJobStatus() {
                const jobId = document.getElementById('job-id').value;
                const responseDiv = document.getElementById('job-response');
                
                if (!jobId.trim()) {
                    alert('Please enter a job ID');
                    return;
                }
                
                responseDiv.classList.remove('empty');
                responseDiv.innerHTML = '<div class="loading">Checking job status...</div>';
                
                try {
                    const response = await fetch(`/job_status/${jobId}`);
                    const data = await response.json();
                    
                    if (response.status === 200) {
                        let statusHtml = `<div class="success">✅ Job found!</div>
<strong>Job ID:</strong> ${jobId}
<strong>Status:</strong> ${data.status}
<strong>Started:</strong> ${data.started_at}`;
                        
                        if (data.progress !== undefined) {
                            statusHtml += `
<strong>Progress:</strong> ${data.progress}%
<div class="progress-bar">
    <div class="progress-fill" style="width: ${data.progress}%"></div>
</div>`;
                        }
                        
                        if (data.completed_at) {
                            statusHtml += `<br><strong>Completed:</strong> ${data.completed_at}`;
                        }
                        
                        if (data.results) {
                            statusHtml += `<br><strong>Results:</strong>
${JSON.stringify(data.results, null, 2)}`;
                        }
                        
                        responseDiv.innerHTML = statusHtml;
                    } else {
                        responseDiv.innerHTML = `<div class="error">❌ ${data.error}</div>`;
                    }
                } catch (error) {
                    responseDiv.innerHTML = `<div class="error">❌ Error: ${error.message}</div>`;
                }
            }
            
            // Auto-refresh agent status every 30 seconds
            setInterval(async () => {
                try {
                    const response = await fetch('/health');
                    const statusIndicator = document.querySelector('.status-indicator');
                    const statusText = document.querySelector('#agent-status strong');
                    
                    if (response.ok) {
                        statusIndicator.className = 'status-indicator status-online';
                        statusText.textContent = 'Online';
                    } else {
                        statusIndicator.className = 'status-indicator status-offline';
                        statusText.textContent = 'Offline';
                    }
                } catch (error) {
                    const statusIndicator = document.querySelector('.status-indicator');
                    const statusText = document.querySelector('#agent-status strong');
                    statusIndicator.className = 'status-indicator status-offline';
                    statusText.textContent = 'Offline';
                }
            }, 30000);
            
            // Make functions globally accessible so HTML can call them
            window.testEndpoint = testEndpoint;
            window.processErrors = processErrors;
            window.checkJobStatus = checkJobStatus;
        </script>
    </body>
    </html>
    '''

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors with a helpful message"""
    return jsonify({
        'error': 'Endpoint not found',
        'available_endpoints': [
            'GET  /health - Health check',
            'POST /process_errors - Process errors synchronously',
            'POST /process_errors_async - Process errors asynchronously',
            'GET  /job_status/<job_id> - Check async job status',
            'GET  /example_errors - Get example error scenarios',
            'GET  /dashboard - Web dashboard interface'
        ]
    }), 404

if __name__ == '__main__':
    print("🚀 Starting AI DevOps Agent Flask API")
    print("📊 Available endpoints:")
    print("   GET  /health - Health check")
    print("   POST /process_errors - Process errors synchronously")
    print("   POST /process_errors_async - Process errors asynchronously")
    print("   GET  /job_status/<job_id> - Check async job status")
    print("   GET  /example_errors - Get example error scenarios")
    print("   GET  /dashboard - Web dashboard interface")
    print("🌐 Server will start on http://localhost:5000")
    print("🎨 Dashboard available at http://localhost:5000/dashboard")
    
    # Force disable debug mode and reloader
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False) 
