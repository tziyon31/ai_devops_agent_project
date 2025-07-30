import re

def mask_secrets(text):
    # זיהוי מבוסס Regex לערכים רגישים
    secret_patterns = [
        r'(?i)(aws_secret_access_key\s*=\s*["\']?).+?([\'"\n])',  # AWS Secret Key
        r'(?i)(api_key\s*=\s*["\']?).+?([\'"\n])',
        r'(?i)(password\s*=\s*["\']?).+?([\'"\n])',
        r'(?i)(authorization\s*:\s*Bearer\s+).+?(\n)',
    ]

    for pattern in secret_patterns:
        text = re.sub(pattern, r'\1[REDACTED]\2', text)

    return text
