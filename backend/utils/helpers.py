import re
from typing import Dict, Any, Optional
from datetime import datetime

def format_response(text: str, max_length: int = 500) -> str:
    """Format response text"""
    if len(text) > max_length:
        text = text[:max_length] + "..."
    
    # Clean up whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def extract_command(message: str) -> Optional[Dict[str, Any]]:
    """Extract command from message"""
    message_lower = message.lower()
    
    # Command patterns
    patterns = {
        "open": r"open\s+(\w+)",
        "calculate": r"calculate\s+(.+)",
        "search": r"search\s+for\s+(.+)",
        "weather": r"weather\s+in\s+(.+)",
        "time": r"what('?s| is) (the )?time",
        "date": r"what('?s| is) (the )?date"
    }
    
    for cmd_type, pattern in patterns.items():
        match = re.search(pattern, message_lower)
        if match:
            return {
                "type": cmd_type,
                "value": match.group(1) if match.groups() else None,
                "original": message
            }
    
    return None

def generate_session_id() -> str:
    """Generate unique session ID"""
    import uuid
    return str(uuid.uuid4())

def safe_eval(expression: str) -> float:
    """Safely evaluate mathematical expression"""
    allowed_chars = set("0123456789+-*/(). ")
    if not all(c in allowed_chars for c in expression):
        raise ValueError("Invalid characters in expression")
    
    return eval(expression, {"__builtins__": {}}, {})