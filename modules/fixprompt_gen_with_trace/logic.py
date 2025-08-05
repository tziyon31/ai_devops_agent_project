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

Final user output:
- Output ONLY the final JSON inside <start> and <end>.

Example:
<trace>
Thought: Error line refers to Groovy compiler, possibly syntax.
Thought: Multiple addError calls suggest a compilation issue.
</trace>
<start>
{
  "failed_step": "Compile",
  "error_summary": "Groovy script failed to compile due to syntax error.",
  "suggested_fix_prompt": "Check the syntax in the Jenkinsfile and verify correct usage of Groovy methods."
}
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

