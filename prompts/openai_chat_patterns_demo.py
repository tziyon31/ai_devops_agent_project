"""
Demo: OpenAI Chat, JSON-only, Tool Calling, and ReAct loop patterns
Author: Your Name

What this file shows:
1) Plain text Q&A call
2) JSON-only response via response_format
3) Tool Calling with a single plan tool
4) ReAct-style loop with tool calls and tool results fed back
5) Measuring latency, using temperature/top_p
"""

import os
import time
import json
import openai

# --- Configuration ---
openai.api_key = os.getenv("OPENAI_API_KEY")  # Use env var or load via dotenv
MODEL = "gpt-4o-mini"

# --- Sample tools schema for Tool Calling ---
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "execute_devops_plan",
            "description": "Plan DevOps troubleshooting steps for the given log",
            "parameters": {
                "type": "object",
                "properties": {
                    "planned_actions": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "tool":  {"type": "string"},
                                "params":{"type": "object"},
                                "when":  {"type": "string", "description": "one of: always, on_timeout, on_port_conflict, if_error_code_137, after_timeout_in_fix"}
                            },
                            "required": ["tool", "params", "when"]
                        }
                    }
                },
                "required": ["planned_actions"]
            }
        }
    }
]

def run_tool(name: str, params: dict):
    """Simulated tool runner used by the ReAct loop."""
    # In production: implement your real tools here.
    if name == "read_log":
        print("📖 [TOOL] Reading log...")
        return "timeout detected"
    elif name == "increase_memory":
        mb = params.get("mb", 512)
        print(f"💾 [TOOL] Increasing memory to {mb} MB")
        return f"memory increased to {mb} MB"
    elif name == "increase_timeout":
        sec = params.get("seconds", 60)
        print(f"⏱️ [TOOL] Increasing timeout to {sec} seconds")
        return f"timeout increased to {sec}s"
    elif name == "free_port":
        port = params.get("port", 443)
        print(f"🔓 [TOOL] Freeing port {port}")
        return f"port {port} freed"
    else:
        print(f"⚠️ [TOOL] Unknown tool: {name}")
        return "unknown tool"

def plain_text_qa():
    """1) Plain text Q&A call."""
    t0 = time.perf_counter()
    resp = openai.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "user", "content": "Summarize this log in one sentence: [12:04] timeout in deploy step"}
        ],
        temperature=0.3,  # slight creativity for phrasing
        top_p=1.0
    )
    dt = time.perf_counter() - t0
    print("⏱ latency:", f"{dt:.2f}s")
    print("Ans:", resp.choices[0].message.content)

def json_only_plan(log_text: str):
    """2) JSON-only output via response_format (no parsing needed)."""
    resp = openai.chat.completions.create(
        model=MODEL,
        response_format={"type": "json_object"},  # force valid JSON only
        messages=[
            {"role": "system", "content": "Always reply with a single JSON object with key 'planned_actions'."},
            {"role": "user", "content": f"Plan actions for this log:\n{log_text}"}
        ],
        temperature=0  # deterministic
    )
    json_text = resp.choices[0].message.content
    plan = json.loads(json_text)  # safe because response_format returns pure JSON
    print("JSON-only plan:", plan)
    return plan

def tool_calling_single_plan(log_text: str):
    """3) Tool Calling once: force the model to call the 'execute_devops_plan' function."""
    resp = openai.chat.completions.create(
        model=MODEL,
        messages=[
            {"role":"system","content":"You are a DevOps planning agent. Call the planning function."},
            {"role":"user","content": f"Analyze this Jenkins log and plan actions:\n{log_text}"}
        ],
        tools=TOOLS,
        tool_choice={"type":"function","function":{"name":"execute_devops_plan"}},  # force function call
        temperature=0
    )
    call = resp.choices[0].message.tool_calls[0]  # one function call
    args = json.loads(call.function.arguments)
    print("Tool-calling plan:", args)
    return args

def react_loop_with_tools(log_text: str, max_iterations=3):
    """
    4) ReAct-style loop: the model may call tools, we execute them,
       then we feed results back as role='tool' messages for another turn.
    """
    messages = [
        {"role": "system", "content": "You are a DevOps agent. Use tools as needed to diagnose and fix."},
        {"role": "user", "content": f"Here is the log:\n{log_text}"}
    ]
    it = 0
    while it < max_iterations:
        print(f"\n🤖 Iteration {it+1}")
        resp = openai.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",  # let the model decide to call tools or not
            temperature=0
        )
        msg = resp.choices[0].message

        # Log assistant content (might be None if only tool_calls exist)
        if msg.content:
            print("Assistant says:", msg.content)
        # If the model asks to call tool(s):
        if msg.tool_calls:
            tool_results = []
            for c in msg.tool_calls:
                # Parse name & arguments
                name = c.function.name
                args = json.loads(c.function.arguments)
                # Execute the tool in Python
                result = run_tool(name, args)
                # Add a tool result message back to the conversation
                tool_results.append({
                    "tool_call_id": c.id,   # must match the call ID from the model
                    "role": "tool",
                    "name": name,
                    "content": str(result)
                })
            # Feed tool results back to the model in the next iteration
            messages.append({"role":"assistant","content":msg.content, "tool_calls": msg.tool_calls})
            messages.extend(tool_results)
            it += 1
            continue
        else:
            # No more tool calls; we are done
            print("✅ Done. Final message:", msg.content)
            break

def compare_sampling(prompt: str):
    """5) Demonstrate temperature and top_p differences quickly."""
    print("\n-- temperature comparison --")
    for t in [0, 1]:
        r = openai.chat.completions.create(
            model=MODEL,
            messages=[{"role":"user","content":prompt}],
            temperature=t,
            top_p=1.0
        )
        print(f"temperature={t} -> {r.choices[0].message.content.strip()}")

    print("\n-- top_p comparison (temperature fixed at 0.8) --")
    for p in [1.0, 0.9]:
        r = openai.chat.completions.create(
            model=MODEL,
            messages=[{"role":"user","content":prompt}],
            temperature=0.8,
            top_p=p
        )
        print(f"top_p={p} -> {r.choices[0].message.content.strip()}")

if __name__ == "__main__":
    # 1) Plain text Q&A
    plain_text_qa()

    # 2) JSON-only response (no parsing needed)
    json_only_plan("[12:04] Port 443 already in use; deploy failed")

    # 3) One-shot tool calling for a plan
    tool_calling_single_plan("[13:10] Timeout during integration tests")

    # 4) ReAct loop (tools → results → next reasoning)
    react_loop_with_tools("[14:00] Pipeline failed with error code 137")

    # 5) Sampling knobs demo
    compare_sampling("Suggest one way to reduce CI timeouts in one short sentence.")

