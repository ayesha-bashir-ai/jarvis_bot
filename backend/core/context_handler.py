import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class ContextHandler:
    """Handles conversation context and state"""
    
    def __init__(self):
        self.contexts: Dict[str, Dict[str, Any]] = {}
    
    def get_context(self, session_id: str) -> Dict[str, Any]:
        """Get context for a session"""
        if session_id not in self.contexts:
            self.contexts[session_id] = self._create_empty_context()
        
        return self.contexts[session_id]
    
    def update_context(self, session_id: str, updates: Dict[str, Any]):
        """Update context for a session"""
        if session_id not in self.contexts:
            self.contexts[session_id] = self._create_empty_context()
        
        self.contexts[session_id].update(updates)
        self.contexts[session_id]["last_updated"] = datetime.now().isoformat()
    
    def _create_empty_context(self) -> Dict[str, Any]:
        """Create empty context structure"""
        return {
            "session_id": "",
            "user_id": "",
            "current_intent": None,
            "last_message": "",
            "last_response": "",
            "conversation_topic": None,
            "pending_actions": [],
            "entities": {},
            "start_time": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "message_count": 0
        }
    
    def clear_context(self, session_id: str):
        """Clear context for a session"""
        if session_id in self.contexts:
            del self.contexts[session_id]
    
    def add_entity(self, session_id: str, entity_type: str, entity_value: Any):
        """Add an entity to context"""
        context = self.get_context(session_id)
        if "entities" not in context:
            context["entities"] = {}
        context["entities"][entity_type] = entity_value
    
    def get_entity(self, session_id: str, entity_type: str) -> Optional[Any]:
        """Get an entity from context"""
        context = self.get_context(session_id)
        return context.get("entities", {}).get(entity_type)