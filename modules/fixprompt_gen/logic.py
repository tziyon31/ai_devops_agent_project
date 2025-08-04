def generate_structured_prompts_from_errors(error_list):
    """
    Takes a list of error dictionaries (from Jenkins log parsing)
    and returns a list of structured prompts formatted for an LLM.
    Each prompt includes role definition, task description, and log context.
    """
    results = []

    for error in error_list:

        structured = f"""You are an expert DevOps assistant specializing in analyzing CI/CD logs and generating structured outputs for failure diagnosis and repair.

Your task is to analyze the following Jenkins log snippet and return a structured output in strict JSON format with the following fields:

<start>
{{
  "failed_step": string,              // Name of the pipeline step where the failure occurred (or "unknown")
  "error_summary": string,            // A clear explanation of what caused the failure
  "suggested_fix_prompt": string      // A prompt that can be passed to an LLM to help fix the issue
}}
<end>

Constraints:
- Use only the information visible in the log.
- Do not invent, infer, or assume missing details.
- Return output ONLY in valid JSON format, wrapped in <start> and <end>.
- Do not include any extra commentary or explanation outside the JSON.
- If the log does not contain enough information to generate the required fields, return:
→ "Not enough information to proceed."

Input log:
<start_log>
{error["context"]}
<end_log>"""

        results.append(structured)

    return results

# error_list = [{'stage': None, 'error_line': 'at org.codehaus.groovy.control.ErrorCollector.failIfErrors(ErrorCollector.java:309)', 'context': '\nat org.codehaus.groovy.control.ErrorCollector.failIfErrors(ErrorCollector.java:309)\nat org.codehaus.groovy.control.ErrorCollector.addFatalError(ErrorCollector.java:149)\nat org.codehaus.groovy.control.ErrorCollector.addError(ErrorCollector.java:119)\nat org.codehaus.groovy.control.ErrorCollector.addError(ErrorCollector.java:131)'}]

# print(generate_structured_prompts_from_errors(error_list))

