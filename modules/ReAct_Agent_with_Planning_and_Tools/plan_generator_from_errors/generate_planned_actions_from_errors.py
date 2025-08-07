def generate_planned_actions_from_errors(error_list):
    """
    Generates prompts that ask an LLM to return:
    1. Internal reasoning in a <trace> section with prompt_id and thoughts
    2. A valid structured <start> ... <end> JSON response with planned actions

    This format supports agent-level traceability and automation planning.
    """
    results = []

    for error in error_list:

        structured = f"""You are an AI DevOps planner.

Your job is to:
1. Think step-by-step to understand the CI/CD failure in the log.
2. Return a JSON plan of tools to trigger, when, and with what parameters.

🧠 Internal trace:
- Wrap your full reasoning inside <trace> ... </trace>
- First line: Prompt_id = timestamp from the log + short error topic (e.g. "2025-08-07 13:24:00 timeout")
- Second line: "# Total steps: X"
- Then write 2+ reasoning steps as Thought lines
- If no timestamp appears in the log, use just the error topic

📦 Output format for user:
Return ONLY valid JSON inside <start> ... <end> like this:

<start>
{{
  "planned_actions": [
    {{
      "tool": string,      // e.g. "read_log"
      "params": object,    // tool parameters like {{"mb": 512}}
      "when": string       // condition (see below)
    }},
    ...
  ]
}}
<end>

🛠 Available tools:
- "read_log" → params: {{}}
- "increase_memory" → params: {{"mb": number}}
- "rerun_test" → params: {{"test_id": number}}
- "increase_timeout" → params: {{"seconds": number}}
- "free_port" → params: {{"port": number}}

⏱ Supported 'when' conditions:
- "always"
- "on_timeout"
- "on_port_conflict"
- "if_error_code_137"
- "after_timeout_in_fix"

🧪 Examples:

Example 1:
<trace>
Prompt_id: 2025-08-05 13:21:00 timeout
# Total steps: 2
Thought: Log shows delay in container response beyond threshold.
Thought: Timeout suggests process needs more time or resources.
</trace>
<start>
{{
  "planned_actions": [
    {{ "tool": "read_log", "params": {{}}, "when": "always" }},
    {{ "tool": "increase_timeout", "params": {{"seconds": 60}}, "when": "on_timeout" }},
    {{ "tool": "rerun_test", "params": {{"test_id": 102}}, "when": "after_timeout_in_fix" }}
  ]
}}
<end>

⚠️ Constraints:
- Use ONLY data in the log — no guessing!
- Do not output anything outside <trace> or <start>/<end>.
-🚫 Do NOT write anything after </end>. Not even explanations, justifications, or extra text.
- If the log is unclear, return only:
→ "Not enough information to proceed."

🔍 Jenkins Log:
<start_log>
{error["context"]}
<end_log>"""

        results.append(structured)

    return results

