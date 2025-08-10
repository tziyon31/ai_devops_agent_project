# run_agent_pipeline.py

from plan_generator_from_errors.generate_planned_actions_from_errors import generate_planned_actions_from_errors
from agent_tool_executor.tool_executer import handle_llm_plan_with_tools
import openai
from dotenv import load_dotenv
import os

# Load environment variables - maintains existing configuration
load_dotenv("C:/Users/tziyo/OneDrive/Documents/learning python/variables and datatypes/.vscode/.env")

# Set your API key (or use environment variable)
openai.api_key = os.getenv("OPEN_AI_API_KEY")
MODEL = "gpt-4o"

# Example input: comprehensive list of CI/CD errors for testing
# This extensive list ensures our agent can handle various DevOps scenarios
example_error_list = [
    {
        "context": """
        [12:05:00] Starting deployment...
        [12:05:03] Error: Port 443 already in use
        [12:05:04] Deployment failed
        """
    },
    {
        "context": """
        [13:14:21] Running integration tests...
        [13:14:25] Error: Timeout waiting for response
        """
    },
    {
        "context": """
        [14:22:10] Building Docker image...
        [14:22:15] Error: Out of memory (137)
        [14:22:16] Build process killed
        """
    },
    {
        "context": """
        [15:30:45] Running unit tests...
        [15:30:48] Error: Connection refused on port 5432
        [15:30:49] Database connection failed
        """
    },
    {
        "context": """
        [16:45:12] Deploying to staging...
        [16:45:18] Error: Insufficient disk space
        [16:45:19] Deployment aborted
        """
    },
    {
        "context": """
        [17:20:33] Running security scan...
        [17:20:40] Error: High severity vulnerability detected
        [17:20:41] Security check failed
        """
    },
    {
        "context": """
        [18:10:55] Installing dependencies...
        [18:11:02] Error: Package not found: react@18.2.0
        [18:11:03] npm install failed
        """
    },
    {
        "context": """
        [19:05:27] Running performance tests...
        [19:05:35] Error: Response time exceeded 5 seconds
        [19:05:36] Performance test failed
        """
    },
    {
        "context": """
        [20:15:08] Building frontend assets...
        [20:15:12] Error: JavaScript syntax error in component.js:45
        [20:15:13] Build compilation failed
        """
    },
    {
        "context": """
        [21:30:42] Running API tests...
        [21:30:48] Error: 500 Internal Server Error
        [21:30:49] API endpoint /api/users failed
        """
    },
    {
        "context": """
        [22:45:15] Deploying to production...
        [22:45:22] Error: SSL certificate expired
        [22:45:23] SSL verification failed
        """
    },
    {
        "context": """
        [23:12:33] Running load tests...
        [23:12:40] Error: Memory usage exceeded 90%
        [23:12:41] Load test terminated
        """
    },
    {
        "context": """
        [00:25:18] Running database migrations...
        [00:25:25] Error: Migration failed - table already exists
        [00:25:26] Database migration aborted
        """
    },
    {
        "context": """
        [01:40:52] Building mobile app...
        [01:40:58] Error: iOS build failed - missing provisioning profile
        [01:40:59] Mobile build failed
        """
    },
    {
        "context": """
        [02:55:37] Running accessibility tests...
        [02:55:44] Error: WCAG 2.1 compliance failed
        [02:55:45] Accessibility check failed
        """
    },
    {
        "context": """
        [03:20:11] Deploying microservices...
        [03:20:18] Error: Service discovery failed
        [03:20:19] Microservice deployment failed
        """
    },
    {
        "context": """
        [04:35:29] Running end-to-end tests...
        [04:35:36] Error: Browser automation timeout
        [04:35:37] E2E test suite failed
        """
    },
    {
        "context": """
        [05:50:44] Building backend services...
        [05:50:51] Error: Go module dependency conflict
        [05:50:52] Backend build failed
        """
    },
    {
        "context": """
        [06:15:22] Running smoke tests...
        [06:15:29] Error: Health check endpoint unreachable
        [06:15:30] Smoke test failed
        """
    },
    {
        "context": """
        [07:30:08] Deploying infrastructure...
        [07:30:15] Error: Terraform state lock timeout
        [07:30:16] Infrastructure deployment failed
        """
    },
    {
        "context": """
        [08:45:33] Running code quality checks...
        [08:45:40] Error: Code coverage below 80%
        [08:45:41] Quality gate failed
        """
    },
    {
        "context": """
        [09:20:17] Building container images...
        [09:20:24] Error: Docker daemon not responding
        [09:20:25] Container build failed
        """
    },
    {
        "context": """
        [10:35:49] Running regression tests...
        [10:35:56] Error: Test data corrupted
        [10:35:57] Regression test suite failed
        """
    },
    {
        "context": """
        [11:50:26] Deploying configuration changes...
        [11:50:33] Error: Configuration validation failed
        [11:50:34] Config deployment failed
        """
    },
    {
        "context": """
        [12:05:14] Running backup verification...
        [12:05:21] Error: Backup integrity check failed
        [12:05:22] Backup verification failed
        """
    },
    {
        "context": """
        [13:20:38] Building documentation...
        [13:20:45] Error: Markdown syntax error in README.md
        [13:20:46] Documentation build failed
        """
    },
    {
        "context": """
        [14:35:52] Running compliance checks...
        [14:35:59] Error: GDPR compliance validation failed
        [14:36:00] Compliance check failed
        """
    },
    {
        "context": """
        [15:50:25] Deploying feature flags...
        [15:50:32] Error: Feature flag service unavailable
        [15:50:33] Feature flag deployment failed
        """
    },
    {
        "context": """
        [16:05:41] Running chaos engineering tests...
        [16:05:48] Error: System recovery timeout
        [16:05:49] Chaos test failed
        """
    },
    {
        "context": """
        [17:20:16] Building analytics pipeline...
        [17:20:23] Error: Data pipeline validation failed
        [17:20:24] Analytics build failed
        """
    },
    {
        "context": """
        [18:35:29] Running monitoring setup...
        [18:35:36] Error: Prometheus configuration invalid
        [18:35:37] Monitoring setup failed
        """
    },
    {
        "context": """
        [19:50:43] Deploying API gateway...
        [19:50:50] Error: Gateway routing configuration error
        [19:50:51] API gateway deployment failed
        """
    },
    {
        "context": """
        [20:05:18] Running data migration...
        [20:05:25] Error: Data integrity constraint violation
        [20:05:26] Data migration failed
        """
    },
    {
        "context": """
        [21:20:34] Building machine learning models...
        [21:20:41] Error: Model training timeout
        [21:20:42] ML pipeline failed
        """
    },
    {
        "context": """
        [22:35:47] Running disaster recovery test...
        [22:35:54] Error: Recovery point objective not met
        [22:35:55] DR test failed
        """
    },
    {
        "context": """
        [23:50:12] Deploying webhook endpoints...
        [23:50:19] Error: Webhook signature validation failed
        [23:50:20] Webhook deployment failed
        """
    },
    {
        "context": """
        [00:05:28] Running performance optimization...
        [00:05:35] Error: CPU usage optimization failed
        [00:05:36] Performance optimization failed
        """
    },
    {
        "context": """
        [01:20:45] Building notification service...
        [01:20:52] Error: Email service configuration invalid
        [01:20:53] Notification service build failed
        """
    },
    {
        "context": """
        [02:35:19] Running security audit...
        [02:35:26] Error: OWASP Top 10 vulnerability detected
        [02:35:27] Security audit failed
        """
    },
    {
        "context": """
        [03:50:31] Deploying cache layer...
        [03:50:38] Error: Redis connection pool exhausted
        [03:50:39] Cache deployment failed
        """
    },
    {
        "context": """
        [04:05:54] Running data validation...
        [04:05:61] Error: Data schema validation failed
        [04:05:62] Data validation failed
        """
    },
    {
        "context": """
        [05:20:37] Building search service...
        [05:20:44] Error: Elasticsearch cluster health check failed
        [05:20:45] Search service build failed
        """
    },
    {
        "context": """
        [06:35:23] Running load balancer configuration...
        [06:35:30] Error: Load balancer health check timeout
        [06:35:31] Load balancer config failed
        """
    },
    {
        "context": """
        [07:50:48] Deploying message queue...
        [07:50:55] Error: RabbitMQ cluster formation failed
        [07:50:56] Message queue deployment failed
        """
    },
    {
        "context": """
        [08:05:15] Running API versioning test...
        [08:05:22] Error: API backward compatibility check failed
        [08:05:23] API versioning test failed
        """
    },
    {
        "context": """
        [09:20:39] Building authentication service...
        [09:20:46] Error: OAuth provider configuration invalid
        [09:20:47] Auth service build failed
        """
    },
    {
        "context": """
        [10:35:52] Running database backup...
        [10:35:59] Error: Backup storage quota exceeded
        [10:35:60] Database backup failed
        """
    },
    {
        "context": """
        [11:50:26] Deploying CDN configuration...
        [11:50:33] Error: CDN cache invalidation failed
        [11:50:34] CDN deployment failed
        """
    },
    {
        "context": """
        [12:05:41] Running integration with third-party API...
        [12:05:48] Error: API rate limit exceeded
        [12:05:49] Third-party integration failed
        """
    },
    {
        "context": """
        [13:20:17] Building real-time notification system...
        [13:20:24] Error: WebSocket connection limit reached
        [13:20:25] Real-time system build failed
        """
    },
    {
        "context": """
        [14:35:33] Running automated testing suite...
        [14:35:40] Error: Test environment setup failed
        [14:35:41] Automated testing failed
        """
    },
    {
        "context": """
        [15:50:49] Deploying logging infrastructure...
        [15:50:56] Error: Log aggregation service unavailable
        [15:50:57] Logging deployment failed
        """
    },
    {
        "context": """
        [16:05:22] Running data encryption test...
        [16:05:29] Error: Encryption key rotation failed
        [16:05:30] Data encryption test failed
        """
    },
    {
        "context": """
        [17:20:38] Building content delivery system...
        [17:20:45] Error: Content compression algorithm failed
        [17:20:46] Content delivery build failed
        """
    },
    {
        "context": """
        [18:35:51] Running service mesh configuration...
        [18:35:58] Error: Istio proxy configuration invalid
        [18:35:59] Service mesh config failed
        """
    },
    {
        "context": """
        [19:50:15] Deploying Kubernetes cluster...
        [19:50:22] Error: Node pool scaling failed
        [19:50:23] K8s deployment failed
        """
    },
    {
        "context": """
        [20:05:33] Running blue-green deployment...
        [20:05:40] Error: Traffic switching failed
        [20:05:41] Blue-green deployment failed
        """
    },
    {
        "context": """
        [21:20:47] Building GraphQL API...
        [21:20:54] Error: Schema validation failed
        [21:20:55] GraphQL build failed
        """
    },
    {
        "context": """
        [22:35:19] Running contract tests...
        [22:35:26] Error: API contract mismatch detected
        [22:35:27] Contract testing failed
        """
    },
    {
        "context": """
        [23:50:41] Deploying serverless functions...
        [23:50:48] Error: Function cold start timeout
        [23:50:49] Serverless deployment failed
        """
    },
    {
        "context": """
        [00:15:28] Running penetration testing...
        [00:15:35] Error: Critical security vulnerability found
        [00:15:36] Penetration test failed
        """
    },
    {
        "context": """
        [01:30:52] Building IoT device firmware...
        [01:30:59] Error: Firmware compilation failed
        [01:31:00] IoT build failed
        """
    },
    {
        "context": """
        [02:45:14] Running blockchain deployment...
        [02:45:21] Error: Smart contract validation failed
        [02:45:22] Blockchain deployment failed
        """
    },
    {
        "context": """
        [03:00:37] Building edge computing nodes...
        [03:00:44] Error: Edge node synchronization failed
        [03:00:45] Edge deployment failed
        """
    }
]

def run_agent_pipeline():
    """
    Main pipeline function that orchestrates the entire DevOps agent workflow.
    Now uses tool calling instead of structured prompts for better reliability.
    """
    print("🚀 Starting AI DevOps Agent Pipeline with Tool Calling")
    print(f"📊 Processing {len(example_error_list)} error scenarios")
    
    # Generate API requests using the new tool calling approach
    api_requests = generate_planned_actions_from_errors(example_error_list)
    
    # Track overall statistics
    total_errors = len(api_requests)
    processed_errors = 0
    total_tools_used = 0
    
    # Process each error scenario with the AI agent
    for i, api_request in enumerate(api_requests[:5]):  # Process first 5 for demo
        print(f"\n" + "="*60)
        print(f"🔍 Processing Error Scenario {i+1}/{min(5, total_errors)}")
        print("="*60)
        
        try:
            # Use the new tool calling approach
            result = handle_llm_plan_with_tools(api_request)
            
            # Log the results
            print(f"✅ Analysis completed successfully")
            print(f"🔧 Tools used: {result['tools_used']}")
            print(f"🔄 AI iterations: {result['iterations']}")
            print(f"💬 Final response: {result['final_response']}")
            
            processed_errors += 1
            total_tools_used += result['tools_used']
            
        except Exception as e:
            print(f"❌ Error processing scenario {i+1}: {str(e)}")
            continue
    
    # Print final summary
    print(f"\n" + "="*60)
    print("📈 PIPELINE SUMMARY")
    print("="*60)
    print(f"✅ Successfully processed: {processed_errors}/{min(5, total_errors)} scenarios")
    print(f"🔧 Total tools executed: {total_tools_used}")
    print(f"📁 Trace files saved in: ./traces/")
    print("🎯 Agent performance: Enhanced with native tool calling")

if __name__ == "__main__":
    # Run the improved agent pipeline
    run_agent_pipeline()

