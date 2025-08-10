# tool_executor.py

import json
import openai
from datetime import datetime
from pathlib import Path
import re

# 👇 Set your OpenAI key and model
openai.api_key = "your-api-key-here"
MODEL = "gpt-4o"

# Folder to save trace logs - maintains existing traceability
TRACE_DIR = Path("./traces")
TRACE_DIR.mkdir(parents=True, exist_ok=True)

# ================================
# Core tool execution logic
# ================================

def run_tool(tool_name, params):
    """
    Executes the actual DevOps tools. This function remains unchanged
    to maintain compatibility with existing tool implementations.
    """
    if tool_name == "read_log":
        print("📖 Reading log...")
        return "timeout detected"
    elif tool_name == "increase_memory":
        print(f"💾 Increasing memory to {params['mb']} MB...")
        return f"memory increased to {params['mb']} MB"
    elif tool_name == "rerun_test":
        print(f"🔁 Rerunning test {params['test_id']}...")
        return "test passed"
    elif tool_name == "increase_timeout":
        print(f"⏱️ Increasing timeout to {params['seconds']} seconds...")
        return "timeout increased"
    elif tool_name == "free_port":
        print(f"🔓 Freeing up port {params['port']}...")
        return f"port {params['port']} freed"
    else:
        print(f"⚠️ Unknown tool: {tool_name}")
        return None

def save_reasoning_trace(messages, tool_calls=None, tool_results=None, ai_responses=None):
    """
    Saves the AI's reasoning process and tool calls for traceability.
    Now captures the ACTUAL AI reasoning from OpenAI responses.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    trace_file = TRACE_DIR / f"trace_{timestamp}.txt"
    
    # Create comprehensive trace log
    trace_content = f"=== AI DevOps Agent Trace ===\n"
    trace_content += f"Timestamp: {timestamp}\n\n"
    
    # Log the full conversation including AI reasoning
    trace_content += "=== Full Conversation Flow ===\n"
    for i, msg in enumerate(messages):
        role = msg['role']
        
        # Clean content to avoid unicode issues but preserve reasoning
        if msg['content']:
            content = str(msg['content'])
            # Only strip unicode for file writing, but preserve reasoning text
            if role == 'assistant':
                # This is AI reasoning - keep it detailed!
                trace_content += f"\n[{i+1}] AI REASONING:\n"
                trace_content += f"{content}\n"
            elif role == 'system':
                trace_content += f"[{i+1}] SYSTEM: Instructions provided\n"
            elif role == 'user':
                trace_content += f"[{i+1}] USER: {content[:100]}...\n"
            elif role == 'tool':
                trace_content += f"[{i+1}] TOOL RESULT: {content}\n"
        trace_content += "\n"
    
    # Log detailed tool analysis
    if tool_calls:
        trace_content += "=== AI Tool Decision Analysis ===\n"
        for i, call in enumerate(tool_calls):
            trace_content += f"Decision {i+1}:\n"
            trace_content += f"  Tool Selected: {call.function.name}\n"
            trace_content += f"  Parameters: {call.function.arguments}\n"
            trace_content += f"  Call ID: {call.id}\n\n"
    
    # Log execution results
    if tool_results:
        trace_content += "=== Tool Execution Results ===\n"
        for i, result in enumerate(tool_results):
            trace_content += f"Execution {i+1}:\n"
            trace_content += f"  Tool: {result.get('name', 'unknown')}\n"
            trace_content += f"  Result: {result.get('content', 'no result')}\n\n"
    
    # Add summary of AI reasoning process
    trace_content += "=== Reasoning Summary ===\n"
    reasoning_steps = [msg for msg in messages if msg['role'] == 'assistant']
    trace_content += f"Total AI reasoning iterations: {len(reasoning_steps)}\n"
    trace_content += f"Tools called: {len(tool_calls) if tool_calls else 0}\n"
    trace_content += f"Tools executed: {len(tool_results) if tool_results else 0}\n"
    
    # Write to file for persistence with UTF-8 encoding
    try:
        trace_file.write_text(trace_content, encoding='utf-8')
        print(f"Comprehensive trace saved to {trace_file}")
    except UnicodeEncodeError:
        # Fallback: clean all unicode and save
        clean_content = trace_content.encode('ascii', 'ignore').decode('ascii')
        trace_file.write_text(clean_content, encoding='utf-8')
        print(f"Trace saved (unicode cleaned) to {trace_file}")
    
    return trace_file

def execute_tool_calls(tool_calls):
    """
    Executes the tools that the AI decided to call.
    Returns results that can be fed back to the AI for further reasoning.
    """
    results = []
    
    for tool_call in tool_calls:
        function_name = tool_call.function.name
        # Parse the arguments from JSON string to dict
        function_args = json.loads(tool_call.function.arguments)
        
        print(f"🔧 Executing tool: {function_name} with args: {function_args}")
        
        # Execute the actual tool
        result = run_tool(function_name, function_args)
        
        # Create result object for OpenAI API
        tool_result = {
            "tool_call_id": tool_call.id,
            "role": "tool", 
            "name": function_name,
            "content": str(result)
        }
        
        results.append(tool_result)
    
    return results

def should_continue_with_tools(response):
    """
    Determines if the AI wants to call more tools based on the response.
    This enables multi-step reasoning and tool chaining.
    """
    return (hasattr(response.choices[0].message, 'tool_calls') and 
            response.choices[0].message.tool_calls is not None)

def handle_llm_plan_with_tools(api_request):
    """
    Main entry point for tool calling approach. Replaces the old
    JSON parsing logic with native OpenAI tool calling.
    """
    # Prepare the conversation with system and user messages
    messages = [
        {"role": "system", "content": api_request["system_prompt"]},
        {"role": "user", "content": api_request["user_message"]}
    ]
    
    # Track all tool calls and results for comprehensive logging
    all_tool_calls = []
    all_tool_results = []
    max_iterations = 5  # Prevent infinite loops
    iteration = 0
    
    while iteration < max_iterations:
        print(f"\n🤖 AI Iteration {iteration + 1}")
        
        # Make API call with tool definitions
        response = openai.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=api_request["tools"],
            tool_choice=api_request["tool_choice"],
            temperature=0
        )
        
        message = response.choices[0].message
        
        # Add AI response to conversation
        messages.append({
            "role": "assistant", 
            "content": message.content,
            "tool_calls": message.tool_calls if hasattr(message, 'tool_calls') else None
        })
        
        # Check if AI wants to use tools
        if should_continue_with_tools(response):
            tool_calls = message.tool_calls
            all_tool_calls.extend(tool_calls)
            
            # Execute the tools
            tool_results = execute_tool_calls(tool_calls)
            all_tool_results.extend(tool_results)
            
            # Add tool results to conversation for AI to see
            messages.extend(tool_results)
            
            iteration += 1
        else:
            # AI is done, break the loop
            print(f"✅ AI completed analysis: {message.content}")
            break
    
    # Save comprehensive trace of the entire interaction
    save_reasoning_trace(messages, all_tool_calls, all_tool_results)
    
    # Return summary of what was accomplished
    return {
        "final_response": messages[-1]["content"] if messages else "No response",
        "tools_used": len(all_tool_calls),
        "iterations": iteration,
        "tool_calls": all_tool_calls,
        "tool_results": all_tool_results
    }

# Legacy function name for backward compatibility
def handle_llm_plan_output(llm_output: str):
    """
    Backward compatibility wrapper. This maintains the old interface
    while redirecting to the new tool calling approach.
    """
    print("⚠️ Using legacy interface. Consider upgrading to handle_llm_plan_with_tools()")
    
    # For now, just save the old-style output as a trace
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    trace_file = TRACE_DIR / f"legacy_trace_{timestamp}.txt"
    trace_file.write_text(llm_output)
    
    return {"message": "Legacy output saved", "trace_file": str(trace_file)}


