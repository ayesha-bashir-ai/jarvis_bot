import re
import logging
from typing import Dict, List, Any, Optional
from backend.models import Intent, IntentType

logger = logging.getLogger(__name__)

class IntentDetector:
    """Detects user intent from messages"""
    
    def __init__(self):
        self.intent_patterns = {
            IntentType.GREETING: [
                r"hello|hi|hey|greetings|good morning|good afternoon|good evening",
                r"what'?s up|how are you|nice to meet you"
            ],
            IntentType.CALCULATION: [
                r"calculate|compute|what is|solve|math",
                r"\d+\s*[\+\-\*\/]\s*\d+",
                r"plus|minus|times|divided by"
            ],
            IntentType.BROWSER: [
                r"open\s+(youtube|google|github|facebook|twitter|instagram|reddit)",
                r"go to|launch|navigate to",
                r"browse|search for"
            ],
            IntentType.SYSTEM_CONTROL: [
                r"shutdown|restart|reboot|sleep|hibernate",
                r"lock\s+(pc|computer|screen)",
                r"take\s+screenshot|capture screen"
            ],
            IntentType.SEARCH: [
                r"search\s+for|find|look up|google|what is|who is",
                r"tell me about|information about"
            ],
            IntentType.COMMAND: [
                r"open\s+(notepad|calculator|calendar|terminal|cmd)",
                r"run|execute|start",
                r"close|exit|quit"
            ]
        }
        
        self.tool_mapping = {
            "open youtube": "open_youtube",
            "open google": "open_google",
            "open github": "open_github",
            "calculate": "calculator",
            "search": "web_search",
            "screenshot": "take_screenshot",
            "shutdown": "system_shutdown",
            "restart": "system_restart",
            "lock": "lock_screen"
        }
    
    async def detect_intent(self, message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Detect intent from message"""
        message_lower = message.lower()
        
        for intent_type, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, message_lower, re.IGNORECASE):
                    intent = self._create_intent(intent_type, message_lower)
                    return intent
        
        # Default to question intent
        if message.endswith("?"):
            return self._create_intent(IntentType.QUESTION, message_lower)
        
        return self._create_intent(IntentType.UNKNOWN, message_lower)
    
    def _create_intent(self, intent_type: IntentType, message: str) -> Dict[str, Any]:
        """Create intent object"""
        intent = {
            "type": intent_type,
            "name": intent_type.value,
            "confidence": 0.9,
            "requires_tool": False,
            "tools": [],
            "entities": {}
        }
        
        # Check if tool is needed
        for keyword, tool in self.tool_mapping.items():
            if keyword in message:
                intent["requires_tool"] = True
                intent["tools"].append(tool)
        
        # Extract entities
        if intent_type == IntentType.CALCULATION:
            intent["entities"]["expression"] = self._extract_math_expression(message)
        elif intent_type == IntentType.BROWSER:
            intent["entities"]["website"] = self._extract_website(message)
        
        return intent
    
    def _extract_math_expression(self, message: str) -> str:
        """Extract mathematical expression from message"""
        patterns = [
            r"calculate\s+(.+)",
            r"what is\s+(.+)",
            r"(\d+\s*[\+\-\*\/]\s*\d+)"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                return match.group(1)
        return ""
    
    def _extract_website(self, message: str) -> str:
        """Extract website name from message"""
        websites = ["youtube", "google", "github", "facebook", "twitter", "instagram", "reddit"]
        for site in websites:
            if site in message.lower():
                return site
        return ""