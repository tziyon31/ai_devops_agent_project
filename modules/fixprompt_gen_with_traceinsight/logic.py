def generate_structured_prompts_from_errors(error_list):
    """
    Takes a list of error dictionaries (from Jenkins log parsing)
    and returns a list of structured prompts formatted for an LLM.
    Each prompt includes role definition, task description, and log context.
    """
    results = []

    for error in error_list:

          structured = f"""You are an expert DevOps assistant specializing in analyzing CI/CD logs and generating structured outputs for failure diagnosis and repair.

Your task:
1. Think step-by-step to understand the failure (internally).
2. Return a structured JSON output for the user.

Internal reasoning:
- Output all your reasoning steps between <trace> and </trace>. Provide at least two Thought lines.
- Directly beneath the first <trace> tag, include a prompt_id composed of the timestamp and a short error topic.
- On the following line, include "# Total steps: X".
- If no timestamp is visible in the log input, use only the error topic for prompt_id.
- The timestamps should reflect the moment of failure as indicated in the log, not the time of this analysis.

Final user output:
- Output ONLY the final JSON inside <start> and <end>.
- Make sure the "error_summary" includes the timestamp (only if visible in the log input) at the beginning of the same line.
  The timestamp should reflect the time of the failure, as shown in the log, not the time of this analysis.

Example:
<trace>
Prompt_id: 2025-08-05 13:21:00 syntax error
# Total steps: 2
Thought: Error line refers to the Groovy compiler, possibly a syntax issue.
Thought: Multiple addError calls suggest a compilation failure.
</trace>
<start>
{{
  "failed_step": "Compile",
  "error_summary": "2025-08-05 13:21:00 Groovy script failed to compile due to syntax error.",
  "suggested_fix_prompt": "Check the syntax in the Jenkinsfile and verify correct usage of Groovy methods."
}}
<end>

Constraints:
- Use only the information visible in the log.
- Do not invent or infer missing details.
- If the log does not contain enough information, return:
  "Not enough information to proceed."

Input log:
<start_log>
{error["context"]}
<end_log>
"""
        results.append(structured)

    return results

# error_list = [{'stage': None, 'error_line': 'at org.codehaus.groovy.control.ErrorCollector.failIfErrors(ErrorCollector.java:309)', 'context': '\nat org.codehaus.groovy.control.ErrorCollector.failIfErrors(ErrorCollector.java:309)\nat org.codehaus.groovy.control.ErrorCollector.addFatalError(ErrorCollector.java:149)\nat org.codehaus.groovy.control.ErrorCollector.addError(ErrorCollector.java:119)\nat org.codehaus.groovy.control.ErrorCollector.addError(ErrorCollector.java:131)'}]

# print(generate_structured_prompts_from_errors(error_list))

