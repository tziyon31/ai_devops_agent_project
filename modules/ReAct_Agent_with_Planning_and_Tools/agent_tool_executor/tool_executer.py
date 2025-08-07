# tool_executor.py

import json
import openai
from datetime import datetime
from pathlib import Path
import re

# 👇 Set your OpenAI key and model
openai.api_key = "your-api-key-here"
MODEL = "gpt-4o"

# Folder to save trace logs
TRACE_DIR = Path("./traces")
TRACE_DIR.mkdir(parents=True, exist_ok=True)

# ================================
# Core execution logic
# ================================

def is_valid_json_structure(text):
    """
    Checks whether the input text is a valid JSON and contains the required structure.
    """
    try:
        data = json.loads(text)
        if "planned_actions" not in data:
            return False
        for action in data["planned_actions"]:
            if not all(k in action for k in ["tool", "params", "when"]):
                return False
        return True
    except json.JSONDecodeError:
        return False

def fix_malformed_json(text):
    """
    Calls the LLM to fix broken JSON output.
    """
    print("🔁 Using fallback LLM to fix JSON...")
    prompt = f"""
You are a JSON repair assistant.
Fix the following broken JSON and return it as valid, minimal, properly formatted JSON:

<start>
{text}
<end>
"""
    response = openai.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    return response.choices[0].message.content.strip()

def run_tool(tool_name, params):
    """
    Simulates running a tool and returns an observation result.
    """
    if tool_name == "read_log":
        print("📖 Reading log...")
        return "timeout detected"
    elif tool_name == "rerun_test":
        print(f"🔁 Rerunning test {params['test_id']}...")
        return "test passed"
    elif tool_name == "increase_timeout":
        print(f"⏱️ Increasing timeout to {params['seconds']} seconds...")
        return "timeout increased"
    else:
        print(f"⚠️ Unknown tool: {tool_name}")
        return None

def execute_plan(plan: dict, context=None):
    """
    Executes a sequence of planned actions with optional conditional logic.
    """
    for action in plan["planned_actions"]:
        condition = action["when"]
        if condition == "always":
            run_tool(action["tool"], action["params"])
        elif condition == "on_timeout" and context == "timeout detected":
            run_tool(action["tool"], action["params"])
        elif condition == "after_timeout_in_fix" and context == "timeout increased":
            run_tool(action["tool"], action["params"])
        # You can extend with more conditions here

def extract_and_save_trace(raw_text: str):
    """
    Extracts the <trace> block from LLM output and saves it to a local trace file.
    Also returns the filename that was saved.
    """
    try:
        start = raw_text.index("<trace>")
        end = raw_text.index("</trace>") + len("</trace>")
        trace_block = raw_text[start:end]
    except ValueError:
        trace_block = "<trace>No trace found</trace>"

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    trace_file = TRACE_DIR / f"trace_{timestamp}.txt"
    trace_file.write_text(trace_block)

    # Optional: store in Postgres (if needed)
    # import psycopg2
    # conn = psycopg2.connect(...)
    # cursor = conn.cursor()
    # cursor.execute("INSERT INTO traces (timestamp, content) VALUES (%s, %s)", (timestamp, trace_block))
    # conn.commit()

    return trace_file

def extract_json_from_wrapped_output(raw_text: str):
    """
    Extracts and parses the <start>...</end> JSON block from LLM output.
    Handles common formatting variations like double curly braces.
    """
    import json

    try:
        start_tag = "<start>"
        end_tag = "</end>"
        
        start_idx = raw_text.find(start_tag)
        
        # Try different variations of the end tag
        end_idx = raw_text.find(end_tag)
        if end_idx == -1:
            # Try with different line endings
            end_idx = raw_text.find(end_tag + "\n")
        if end_idx == -1:
            end_idx = raw_text.find(end_tag + "\r\n")
        if end_idx == -1:
            # Try without the closing tag
            end_idx = len(raw_text)
        
        if start_idx == -1:
            raise ValueError("❌ JSON <start> or <end> block not found.")
        
        # Extract content between start and end tags
        json_content = raw_text[start_idx + len(start_tag):end_idx].strip()
        
        # Clean the JSON content - remove any trailing content after the closing brace
        last_brace_idx = json_content.rfind('}')
        if last_brace_idx != -1:
            json_content = json_content[:last_brace_idx + 1]
        
        # נתקן סוגריים כפולים אם קיימים (זה לא JSON תקין)
        if json_content.startswith("{{") and json_content.endswith("}}"):
            json_content = json_content[1:-1]  # מסיר סוגריים חיצוניים

        return json.loads(json_content)
    except json.JSONDecodeError as e:
        raise ValueError(f"❌ Failed to parse JSON: {e}")


def handle_llm_plan_output(llm_output: str):
    """
    Main entry point: validates or repairs the LLM plan,
    saves trace, and runs the planned tools accordingly.
    """
    extract_and_save_trace(llm_output)

    try:
        plan = extract_json_from_wrapped_output(llm_output)
    except ValueError as e:
        print(str(e))
        return

    # Validate the structure of the plan
    if "planned_actions" not in plan:
        print("❌ Invalid plan structure: missing 'planned_actions'")
        return
    
    for action in plan["planned_actions"]:
        if not all(k in action for k in ["tool", "params", "when"]):
            print("❌ Invalid action structure: missing required fields")
            return

    first_result = run_tool("read_log", {})
    execute_plan(plan, context=first_result)
    return plan

# For external use from another file:
# from modules.tool_executor import handle_llm_plan_output


