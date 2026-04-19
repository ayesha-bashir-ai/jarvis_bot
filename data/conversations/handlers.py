"""
Message Handlers - Process and format conversation messages
"""

import re
from typing import Dict, Any, List, Optional
from datetime import datetime

class MessageHandler:
    """Handles message processing and formatting"""
    
    @staticmethod
    def format_message(content: str, role: str) -> Dict[str, Any]:
        """Format a single message"""
        return {
            "role": role,
            "content": content.strip(),
            "timestamp": datetime.now().isoformat(),
            "formatted": MessageHandler._apply_formatting(content)
        }
    
    @staticmethod
    def _apply_formatting(content: str) -> str:
        """Apply formatting to message content"""
        # Bold text
        content = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', content)
        
        # Italic text
        content = re.sub(r'\*([^*]+)\*', r'<em>\1</em>', content)
        
        # Code blocks
        content = re.sub(r'`([^`]+)`', r'<code>\1</code>', content)
        
        # Links
        content = re.sub(r'(https?://[^\s]+)', r'<a href="\1" target="_blank">\1</a>', content)
        
        # Line breaks
        content = content.replace('\n', '<br>')
        
        return content
    
    @staticmethod
    def extract_entities(text: str) -> Dict[str, List[str]]:
        """Extract entities from message text"""
        entities = {
            "urls": re.findall(r'https?://[^\s]+', text),
            "emails": re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', text),
            "numbers": re.findall(r'\b\d+(?:\.\d+)?\b', text),
            "mentions": re.findall(r'@\w+', text),
            "hashtags": re.findall(r'#\w+', text)
        }
        return entities
    
    @staticmethod
    def truncate_message(content: str, max_length: int = 500) -> str:
        """Truncate message to maximum length"""
        if len(content) <= max_length:
            return content
        return content[:max_length] + "..."
    
    @staticmethod
    def detect_language(text: str) -> str:
        """Detect language of message (simple version)"""
        # Simple language detection based on character sets
        if re.search(r'[\u4e00-\u9fff]', text):
            return "zh"
        elif re.search(r'[\u3040-\u309f\u30a0-\u30ff]', text):
            return "ja"
        elif re.search(r'[\uac00-\ud7af]', text):
            return "ko"
        elif re.search(r'[áéíóúñü]', text):
            return "es"
        elif re.search(r'[äöüß]', text):
            return "de"
        elif re.search(r'[àâçéèêëîïôûù]', text):
            return "fr"
        else:
            return "en"
    
    @staticmethod
    def get_message_type(content: str) -> str:
        """Determine message type"""
        content_lower = content.lower()
        
        if any(word in content_lower for word in ["hello", "hi", "hey", "greetings"]):
            return "greeting"
        elif "?" in content:
            return "question"
        elif any(word in content_lower for word in ["open", "launch", "start"]):
            return "command"
        elif any(word in content_lower for word in ["calculate", "calc", "math"]):
            return "calculation"
        elif any(word in content_lower for word in ["search", "find", "look up"]):
            return "search"
        else:
            return "statement"