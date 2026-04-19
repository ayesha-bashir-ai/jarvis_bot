import re
from typing import Tuple

def validate_message(message: str) -> Tuple[bool, str]:
    """Validate user message"""
    if not message or not message.strip():
        return False, "Message cannot be empty"
    
    if len(message) > 2000:
        return False, "Message too long (max 2000 characters)"
    
    return True, ""

def sanitize_input(text: str) -> str:
    """Sanitize user input"""
    # Remove potentially dangerous characters
    text = re.sub(r'[<>{}]', '', text)
    
    # Limit length
    text = text[:2000]
    
    return text.strip()

def is_valid_url(url: str) -> bool:
    """Check if URL is valid"""
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    return url_pattern.match(url) is not None