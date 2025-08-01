def jenkins_log_error_identifier(log: str, context_before=4, context_after=2):
    # Split the raw Jenkins log into individual lines
    lines = log.splitlines()

    # List to store detected errors along with context
    results = []

    # Track the current stage (e.g. 'Build', 'Deploy')
    current_stage = None

    # Index pointer
    i = 0

    # Define keywords that indicate errors (case-insensitive)
    error_keywords = ["exception", "error", "failed", "refused", "fatal", "trace"]

    while i < len(lines):
        line = lines[i]

        # Track stage if pipeline format exists
        if "[Pipeline]" in line and "{ (" in line:
            current_stage = line.split("{ (")[-1].strip(")")

        # Detect if the line is the start of an error
        if any(keyword in line.lower() for keyword in error_keywords):
            # Include context before
            start = max(0, i - context_before)
            end = i + 1

            # Include following 'at ...' lines as part of stack trace
            while end < len(lines) and lines[end].lstrip().startswith("at "):
                end += 1

            # Add extra context after
            end = min(len(lines), end + context_after)

            context_block = "\n".join(lines[start:end])
            results.append({
                "stage": current_stage,
                "error_line": line.strip(),
                "context": context_block
            })

            i = end  # Skip ahead
        else:
            i += 1

    return results


