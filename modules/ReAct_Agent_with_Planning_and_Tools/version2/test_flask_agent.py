# test_flask_agent.py
# This file demonstrates how to test the Flask agent API endpoints
# Key features demonstrated:
# 1. Health check endpoint testing
# 2. Synchronous error processing
# 3. Asynchronous error processing
# 4. Job status monitoring
# 5. Example error retrieval

import requests
import json
import time
from datetime import datetime

# Configuration - Flask server URL
BASE_URL = "http://localhost:5000"

def test_health_check():
    """
    Test the health check endpoint to verify the Flask service is running
    """
    print("🔍 Testing health check endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed: {data['status']}")
            print(f"   Service: {data['service']}")
            print(f"   Model: {data['model']}")
            print(f"   API Key configured: {data['api_key_configured']}")
            return True
        else:
            print(f"❌ Health check failed with status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to Flask server. Make sure it's running on localhost:5000")
        return False
    except Exception as e:
        print(f"❌ Health check error: {str(e)}")
        return False

def test_get_example_errors():
    """
    Test the example errors endpoint to get sample error scenarios
    """
    print("\n🔍 Testing example errors endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/example_errors")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Retrieved {data['total_examples']} example errors")
            for i, error in enumerate(data['example_errors'], 1):
                print(f"   Example {i}: {error['context'][:100]}...")
            return data['example_errors']
        else:
            print(f"❌ Failed to get example errors: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Error getting examples: {str(e)}")
        return []

def test_sync_error_processing(example_errors):
    """
    Test synchronous error processing endpoint
    """
    print("\n🔍 Testing synchronous error processing...")
    
    # Prepare test data with first 2 examples
    test_data = {
        "errors": example_errors[:2],
        "max_scenarios": 2
    }
    
    try:
        print(f"📤 Sending {len(test_data['errors'])} error scenarios for processing...")
        response = requests.post(
            f"{BASE_URL}/process_errors",
            json=test_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Synchronous processing completed successfully")
            print(f"   Total scenarios: {data['total_scenarios']}")
            print(f"   Successful: {data['successful_scenarios']}")
            print(f"   Failed: {data['failed_scenarios']}")
            print(f"   Total tools executed: {data['total_tools_executed']}")
            
            # Show detailed results
            for result in data['results']:
                status_emoji = "✅" if result['status'] == 'success' else "❌"
                print(f"   {status_emoji} Scenario {result['scenario_id']}: {result['status']}")
                if result['status'] == 'success':
                    print(f"      Tools used: {result['tools_used']}, Iterations: {result['iterations']}")
            
            return True
        else:
            print(f"❌ Synchronous processing failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error in synchronous processing: {str(e)}")
        return False

def test_async_error_processing(example_errors):
    """
    Test asynchronous error processing endpoint
    """
    print("\n🔍 Testing asynchronous error processing...")
    
    # Prepare test data with first 2 examples
    test_data = {
        "errors": example_errors[:2],
        "max_scenarios": 2
    }
    
    try:
        print(f"📤 Starting async processing for {len(test_data['errors'])} error scenarios...")
        response = requests.post(
            f"{BASE_URL}/process_errors_async",
            json=test_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 202:
            data = response.json()
            job_id = data['job_id']
            print(f"✅ Async processing started successfully")
            print(f"   Job ID: {job_id}")
            print(f"   Status endpoint: {data['check_status_endpoint']}")
            
            # Monitor job progress
            print("🔄 Monitoring job progress...")
            max_wait_time = 60  # Maximum wait time in seconds
            start_time = time.time()
            
            while time.time() - start_time < max_wait_time:
                status_response = requests.get(f"{BASE_URL}/job_status/{job_id}")
                
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    current_status = status_data['status']
                    
                    if current_status == 'processing':
                        progress = status_data.get('progress', 0)
                        print(f"   📊 Progress: {progress}%")
                        time.sleep(2)  # Wait 2 seconds before checking again
                    elif current_status == 'completed':
                        print(f"✅ Async processing completed successfully")
                        print(f"   Total scenarios: {status_data['total_scenarios']}")
                        print(f"   Successful: {status_data['successful_scenarios']}")
                        print(f"   Failed: {status_data['failed_scenarios']}")
                        print(f"   Total tools executed: {status_data['total_tools_executed']}")
                        return True
                    elif current_status == 'error':
                        print(f"❌ Async processing failed: {status_data.get('error_message', 'Unknown error')}")
                        return False
                else:
                    print(f"❌ Failed to get job status: {status_response.status_code}")
                    return False
            
            print("⏰ Timeout waiting for async processing to complete")
            return False
            
        else:
            print(f"❌ Failed to start async processing: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error in async processing: {str(e)}")
        return False

def run_all_tests():
    """
    Run all tests in sequence
    """
    print("🚀 Starting Flask Agent API Tests")
    print("=" * 50)
    
    # Test 1: Health check
    if not test_health_check():
        print("\n❌ Health check failed. Cannot proceed with other tests.")
        return False
    
    # Test 2: Get example errors
    example_errors = test_get_example_errors()
    if not example_errors:
        print("\n❌ Failed to get example errors. Cannot proceed with processing tests.")
        return False
    
    # Test 3: Synchronous processing
    sync_success = test_sync_error_processing(example_errors)
    
    # Test 4: Asynchronous processing
    async_success = test_async_error_processing(example_errors)
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    print(f"✅ Health check: {'PASSED' if True else 'FAILED'}")
    print(f"✅ Example errors: {'PASSED' if example_errors else 'FAILED'}")
    print(f"✅ Synchronous processing: {'PASSED' if sync_success else 'FAILED'}")
    print(f"✅ Asynchronous processing: {'PASSED' if async_success else 'FAILED'}")
    
    overall_success = True and example_errors and sync_success and async_success
    print(f"\n🎯 Overall result: {'ALL TESTS PASSED' if overall_success else 'SOME TESTS FAILED'}")
    
    return overall_success

if __name__ == "__main__":
    """
    Main entry point for running all tests
    Make sure the Flask server is running before executing this script
    """
    print("⚠️  Make sure the Flask server is running on localhost:5000 before running tests!")
    print("   Start the server with: python flask_agent_app.py")
    print()
    
    # Wait a moment for user to read the warning
    input("Press Enter to continue with tests...")
    
    # Run all tests
    success = run_all_tests()
    
    if success:
        print("\n🎉 All tests completed successfully!")
    else:
        print("\n💥 Some tests failed. Check the output above for details.")
    
    print("\n📚 API Documentation:")
    print("   GET  /health - Health check")
    print("   POST /process_errors - Process errors synchronously")
    print("   POST /process_errors_async - Process errors asynchronously")
    print("   GET  /job_status/<job_id> - Check async job status")
    print("   GET  /example_errors - Get example error scenarios") 