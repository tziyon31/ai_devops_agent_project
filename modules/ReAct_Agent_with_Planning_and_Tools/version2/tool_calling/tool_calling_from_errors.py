def get_devops_tools():
    """
    Defines the available DevOps tools as OpenAI function schemas.
    This replaces the structured prompt approach with native tool calling.
    """
    return [
        {
            "type": "function",
            "function": {
                "name": "read_log",
                "description": "Read and analyze log files to understand the CI/CD failure",
                "parameters": {
                    "type": "object", 
                    "properties": {},
                    "required": []
                }
            }
        },
        {
            "type": "function", 
            "function": {
                "name": "increase_memory",
                "description": "Increase memory allocation for processes that are running out of memory",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "mb": {
                            "type": "integer",
                            "description": "Memory amount in megabytes to allocate"
                        }
                    },
                    "required": ["mb"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "rerun_test",
                "description": "Rerun a specific test that failed",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "test_id": {
                            "type": "integer",
                            "description": "ID of the test to rerun"
                        }
                    },
                    "required": ["test_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "increase_timeout", 
                "description": "Increase timeout duration for operations that are timing out",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "seconds": {
                            "type": "integer",
                            "description": "Timeout duration in seconds"
                        }
                    },
                    "required": ["seconds"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "free_port",
                "description": "Free up a port that is already in use",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "port": {
                            "type": "integer",
                            "description": "Port number to free up"
                        }
                    },
                    "required": ["port"]
                }
            }
        }
    ]

def generate_devops_system_prompt():
    """
    Creates the system prompt that guides the AI's reasoning process.
    This maintains the trace functionality while using tool calling.
    """
    return """You are an AI DevOps planner and troubleshooter.

Your job is to:
1. Analyze CI/CD failure logs step-by-step
2. Use the available tools to fix the issues

🧠 Analysis Process:
- Think through the problem systematically
- Identify the root cause of the failure
- Determine which tools can help resolve the issue
- Consider the sequence and conditions for tool usage

🛠 Available Actions:
You have access to several DevOps tools via function calling:
- read_log: Analyze log files 
- increase_memory: Allocate more memory for memory issues
- rerun_test: Retry failed tests
- increase_timeout: Extend timeout for slow operations  
- free_port: Release occupied ports

⏱ Conditional Logic:
Consider when each tool should be used:
- Always: Tools that should run immediately
- On specific conditions: Tools that depend on context
- Sequential: Tools that depend on previous tool results

🔍 Analysis Guidelines:
- Base decisions ONLY on information in the logs
- Don't make assumptions beyond what's clearly stated
- If logs are unclear, indicate insufficient information
- Prioritize the most likely solution first"""

def generate_planned_actions_from_errors(error_list):
    """
    Generates system prompts and user messages for tool calling approach.
    Returns structured data for OpenAI API calls instead of text parsing.
    """
    results = []
    
    # Get the tool definitions once
    tools = get_devops_tools()
    system_prompt = generate_devops_system_prompt()
    
    for error in error_list:
        # Create user message with the specific error context
        user_message = f"""Analyze this CI/CD failure and use the appropriate tools to fix it:

🔍 Jenkins Log:
{error["context"]}

Please analyze the error and call the necessary tools to resolve the issue."""

        # Structure the request for OpenAI API
        api_request = {
            "system_prompt": system_prompt,
            "user_message": user_message, 
            "tools": tools,
            "tool_choice": "auto"  # Let AI decide which tools to use
        }
        
        results.append(api_request)
    
    return results

