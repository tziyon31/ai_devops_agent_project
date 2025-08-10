#!/usr/bin/env python3
"""
Simple Demo  - Shows Synchronous vs Asynchronous POST requests
"""

import requests
import json
import time

# Flask server URL
BASE_URL = "http://localhost:5000"

def demo_sync_post():
    """Demo synchronous POST request"""
    print("🔄 DEMO 1: Synchronous POST Request")
    print("=" * 50)
    
    # Test data
    data = {
        "errors": [
            {
                "context": "[2023-10-25 14:32:15] INFO: Starting Docker build for image my-app:latest\n[2023-10-25 14:33:45] ERROR: Docker build failed with out of memory error\n[2023-10-25 14:33:46] INFO: Cleaning up failed build artifacts"
            },
            {
                "context": "[2023-10-25 15:10:23] INFO: Initializing database migration\n[2023-10-25 15:11:05] ERROR: Migration failed due to schema version mismatch\n[2023-10-25 15:11:06] INFO: Rolling back changes"
            },
            {
                "context": "[2023-10-25 16:45:12] INFO: Starting Kubernetes pod deployment\n[2023-10-25 16:47:33] ERROR: Pod failed to start - insufficient cluster resources\n[2023-10-25 16:47:34] INFO: Removing failed pod deployment"
            },
            {
                "context": "[2023-10-25 17:20:45] INFO: Initiating backup process\n[2023-10-25 17:22:15] ERROR: Backup failed - storage quota exceeded\n[2023-10-25 17:22:16] INFO: Cleaning up partial backup files"
            },
            {
                "context": "[2023-10-25 18:05:30] INFO: Starting application server\n[2023-10-25 18:06:45] ERROR: Application crashed due to unhandled exception in middleware\n[2023-10-25 18:06:46] INFO: Generating crash report"
            }
        ]
    }
    
    print(f"📤 Sending POST to /process_errors")
    print(f"📋 Data: {json.dumps(data, indent=2)}")
    
    # Make synchronous request
    start_time = time.time()
    response = requests.post(f"{BASE_URL}/process_errors", json=data)
    end_time = time.time()
    
    print(f"⏱️  Response time: {end_time - start_time:.2f} seconds")
    print(f"📥 Status: {response.status_code}")
    print(f"📄 Response: {json.dumps(response.json(), indent=2)}")
    print()

def demo_async_post():
    """Demo asynchronous POST request"""
    print("🔄 DEMO 2: Asynchronous POST Request")
    print("=" * 50)
    
    # Test data
    data = {
        "errors": [
            {
                "context": "Kubernetes deployment timeout"
            },
            {
                "context": "Database connection failed"
            }
        ]
    }
    
    print(f"📤 Sending POST to /process_errors_async")
    print(f"📋 Data: {json.dumps(data, indent=2)}")
    
    # Make asynchronous request
    start_time = time.time()
    response = requests.post(f"{BASE_URL}/process_errors_async", json=data)
    end_time = time.time()
    
    print(f"⏱️  Response time: {end_time - start_time:.2f} seconds")
    print(f"📥 Status: {response.status_code}")
    print(f"📄 Response: {json.dumps(response.json(), indent=2)}")
    
    # Get job ID and check status
    if response.status_code == 202:
        job_id = response.json()['job_id']
        print(f"🆔 Job ID: {job_id}")
        
        # Check job status
        print(f"🔍 Checking job status...")
        status_response = requests.get(f"{BASE_URL}/job_status/{job_id}")
        print(f"📊 Job Status: {json.dumps(status_response.json(), indent=2)}")
    
    print()

def main():
    """Run the demo"""
    print("🚀 AI DevOps Agent - POST Request Demo")
    print("=" * 60)
    print()
    
    # Check if server is running
    try:
        health_response = requests.get(f"{BASE_URL}/health")
        if health_response.status_code == 200:
            print("✅ Server is running!")
            print()
        else:
            print("❌ Server health check failed")
            return
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure it's running on localhost:5000")
        return
    
    # Run demos
    demo_sync_post()
    demo_async_post()
    
    print("🎉 Demo completed!")

if __name__ == "__main__":
    main() 