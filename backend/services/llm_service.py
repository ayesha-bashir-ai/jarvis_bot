import logging
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from backend.config import settings

logger = logging.getLogger(__name__)

class LLMService:
    """Service for LLM interactions"""
    
    def __init__(self):
        self.model = settings.DEFAULT_MODEL
        self.temperature = settings.TEMPERATURE
        self.max_tokens = settings.MAX_TOKENS
        self.client = None
        
        # Initialize OpenAI client if API key is provided
        if settings.OPENAI_API_KEY:
            try:
                import openai
                self.client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
                logger.info("OpenAI client initialized")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI: {e}")
    
    async def generate_response(
        self,
        message: str,
        context: Dict[str, Any],
        intent: Dict[str, Any],
        personality: str = "JARVIS"
    ) -> Dict[str, Any]:
        """Generate response using LLM"""
        
        # Build system prompt
        system_prompt = self._build_system_prompt(personality, intent)
        
        # Build conversation context
        conversation = self._build_conversation_context(context, message)
        
        try:
            if self.client:
                response = await self._call_openai(system_prompt, conversation)
            else:
                # Fallback to rule-based responses
                response = self._generate_fallback_response(message, intent)
            
            return {
                "text": response,
                "metadata": {
                    "model": self.model,
                    "timestamp": datetime.now().isoformat()
                }
            }
        except Exception as e:
            logger.error(f"LLM generation error: {e}")
            return {
                "text": self._generate_fallback_response(message, intent),
                "metadata": {"error": str(e)}
            }
    
    def _build_system_prompt(self, personality: str, intent: Dict[str, Any]) -> str:
        """Build system prompt for LLM"""
        return f"""You are {personality}, an advanced AI assistant with the following traits:
- Intelligent and helpful
- Professional but slightly witty
- Efficient and precise
- Familiar with system control, web browsing, calculations, and general knowledge
- Can execute tools when needed

Current intent: {intent.get('name', 'unknown')}
Confidence: {intent.get('confidence', 0.5)}

Provide concise, accurate responses. If a tool is needed, indicate so clearly."""
    
    def _build_conversation_context(self, context: Dict[str, Any], current_message: str) -> List[Dict[str, str]]:
        """Build conversation context for LLM"""
        messages = []
        
        # Add recent conversation history
        recent_messages = context.get("recent_messages", [])
        for msg in recent_messages[-5:]:  # Last 5 messages
            messages.append({
                "role": msg.get("role", "user"),
                "content": msg.get("content", "")
            })
        
        # Add current message
        messages.append({
            "role": "user",
            "content": current_message
        })
        
        return messages
    
    async def _call_openai(self, system_prompt: str, conversation: List[Dict[str, str]]) -> str:
        """Call OpenAI API"""
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    *conversation
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise
    
    def _generate_fallback_response(self, message: str, intent: Dict[str, Any]) -> str:
        """Generate fallback response without LLM"""
        message_lower = message.lower()
        
        # Time responses
        if "time" in message_lower:
            return f"The current time is {datetime.now().strftime('%I:%M %p')}"
        
        # Date responses
        if "date" in message_lower or "today" in message_lower:
            return f"Today is {datetime.now().strftime('%A, %B %d, %Y')}"
        
        # Greeting responses
        if any(g in message_lower for g in ["hello", "hi", "hey"]):
            return "Hello Commander! How can I assist you today?"
        
        # Help response
        if "help" in message_lower:
            return """I can help you with:
- Opening websites (say "open YouTube")
- Calculations (say "calculate 5 + 3")
- System commands (say "take screenshot" or "lock screen")
- Weather information (say "weather in London")
- Web searches (say "search for Python tutorials")
- And much more! What would you like me to do?"""
        
        # Default response
        return f"I understand you're asking about: {message[:50]}... I'm currently in fallback mode. For full AI capabilities, please configure your OpenAI API key."