import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import json
from backend.core.intent_detector import IntentDetector
from backend.core.memory_manager import MemoryManager
from backend.tools import ToolRegistry
from backend.services.llm_service import LLMService
from backend.database import get_db, Conversation, Memory

logger = logging.getLogger(__name__)

class JarvisBrain:
    """Main brain of JARVIS - handles decision making and orchestration"""
    
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service
        self.intent_detector = IntentDetector()
        self.memory_manager = MemoryManager()
        self.tool_registry = ToolRegistry()
        self.context_cache: Dict[str, List[Dict]] = {}
        
    async def process_message(self, message: str, session_id: str, user_id: str = "default") -> Dict[str, Any]:
        """Process user message and generate response"""
        start_time = datetime.now()
        
        try:
            # 1. Get conversation context
            context = await self.get_context(session_id)
            
            # 2. Detect intent
            intent = await self.intent_detector.detect_intent(message, context)
            logger.info(f"Detected intent: {intent}")
            
            # 3. Check if tool execution is needed
            tools_used = []
            if intent.get("requires_tool"):
                tool_result = await self.execute_tools(intent["tools"], message, session_id)
                tools_used = tool_result["tools_used"]
                context["tool_results"] = tool_result["results"]
            
            # 4. Generate response using LLM
            response = await self.llm_service.generate_response(
                message=message,
                context=context,
                intent=intent,
                personality="JARVIS"
            )
            
            # 5. Update memory
            await self.update_memory(session_id, user_id, message, response, intent, tools_used)
            
            # 6. Save to database
            async for db in get_db():
                conversation = Conversation(
                    session_id=session_id,
                    user_id=user_id,
                    message=message,
                    response=response["text"],
                    intent=intent["name"],
                    tools_used=tools_used
                )
                db.add(conversation)
                await db.commit()
                break
            
            # 7. Calculate response time
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            
            return {
                "message": response["text"],
                "intent": intent["name"],
                "tools_used": tools_used,
                "response_time": int(response_time),
                "metadata": response.get("metadata", {})
            }
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return {
                "message": "I apologize, but I encountered an error. Please try again.",
                "intent": "error",
                "tools_used": [],
                "response_time": 0
            }
    
    async def get_context(self, session_id: str) -> Dict[str, Any]:
        """Get conversation context for session"""
        if session_id not in self.context_cache:
            self.context_cache[session_id] = []
        
        # Get recent messages from memory
        recent_messages = self.memory_manager.get_recent_messages(session_id)
        
        return {
            "session_id": session_id,
            "recent_messages": recent_messages,
            "user_preferences": await self.get_user_preferences(session_id),
            "timestamp": datetime.now().isoformat()
        }
    
    async def update_memory(self, session_id: str, user_id: str, message: str, response: str, intent: Dict, tools_used: List):
        """Update memory with new conversation"""
        memory_entry = {
            "role": "user",
            "content": message,
            "timestamp": datetime.now().isoformat()
        }
        
        if session_id not in self.context_cache:
            self.context_cache[session_id] = []
        
        self.context_cache[session_id].append(memory_entry)
        
        # Trim cache if too large
        if len(self.context_cache[session_id]) > 50:
            self.context_cache[session_id] = self.context_cache[session_id][-50:]
        
        # Store in long-term memory if significant
        if self.is_significant_memory(message, response):
            await self.store_long_term_memory(user_id, message, response, intent)
    
    async def execute_tools(self, tools: List[str], message: str, session_id: str) -> Dict[str, Any]:
        """Execute required tools"""
        results = {}
        tools_used = []
        
        for tool_name in tools:
            if self.tool_registry.has_tool(tool_name):
                tool = self.tool_registry.get_tool(tool_name)
                try:
                    result = await tool.execute(message, session_id)
                    results[tool_name] = result
                    tools_used.append(tool_name)
                    logger.info(f"Executed tool: {tool_name}")
                except Exception as e:
                    logger.error(f"Tool execution failed {tool_name}: {e}")
                    results[tool_name] = {"error": str(e)}
        
        return {"results": results, "tools_used": tools_used}
    
    async def get_user_preferences(self, user_id: str) -> Dict:
        """Get user preferences from database"""
        async for db in get_db():
            from backend.database import UserProfile
            profile = await db.execute(
                UserProfile.__table__.select().where(UserProfile.user_id == user_id)
            )
            profile = profile.first()
            if profile:
                return profile.preferences
            return {}
    
    async def store_long_term_memory(self, user_id: str, message: str, response: str, intent: Dict):
        """Store important information in long-term memory"""
        async for db in get_db():
            memory = Memory(
                user_id=user_id,
                key=f"memory_{datetime.now().timestamp()}",
                value=json.dumps({
                    "message": message,
                    "response": response,
                    "intent": intent
                }),
                memory_type="long_term"
            )
            db.add(memory)
            await db.commit()
            break
    
    def is_significant_memory(self, message: str, response: str) -> bool:
        """Determine if conversation should be stored in long-term memory"""
        significant_keywords = ["remember", "my name is", "I like", "I prefer", "important"]
        return any(keyword in message.lower() for keyword in significant_keywords)
    
    async def clear_context(self, session_id: str):
        """Clear conversation context for a session"""
        if session_id in self.context_cache:
            del self.context_cache[session_id]
        await self.memory_manager.clear_session(session_id)

        # Add at the end of the file
_brain_instance = None

def get_brain_instance():
    """Get or create brain instance"""
    global _brain_instance
    if _brain_instance is None:
        from backend.services.llm_service import LLMService
        llm_service = LLMService()
        _brain_instance = JarvisBrain(llm_service)
    return _brain_instance