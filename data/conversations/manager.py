"""
Conversation Manager - Core conversation handling logic
"""

import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from collections import deque
from sqlalchemy import select, desc, delete, or_, func
from backend.database import get_db
from backend.models import Conversation

logger = logging.getLogger(__name__)

class ConversationManager:
    """Manages conversations and chat history with caching"""
    
    def __init__(self, max_history: int = 100):
        self.max_history = max_history
        self.active_conversations: Dict[str, deque] = {}
        self.conversation_metadata: Dict[str, Dict] = {}
        
    async def add_message(
        self, 
        session_id: str, 
        user_id: str, 
        message: str, 
        response: str, 
        intent: str = None,
        tools_used: List[str] = None,
        response_time: int = 0
    ) -> Dict[str, Any]:
        """Add a message to conversation history"""
        
        conversation = Conversation(
            session_id=session_id,
            user_id=user_id,
            message=message,
            response=response,
            intent=intent or "general",
            tools_used=tools_used or [],
            response_time=response_time
        )
        
        # Store in database
        async for db in get_db():
            db.add(conversation)
            await db.commit()
            await db.refresh(conversation)
            break
        
        # Store in memory cache
        if session_id not in self.active_conversations:
            self.active_conversations[session_id] = deque(maxlen=self.max_history)
        
        self.active_conversations[session_id].append({
            "id": conversation.id,
            "role": "user",
            "content": message,
            "timestamp": datetime.now().isoformat()
        })
        self.active_conversations[session_id].append({
            "id": conversation.id,
            "role": "assistant",
            "content": response,
            "timestamp": datetime.now().isoformat()
        })
        
        # Update metadata
        self._update_metadata(session_id, message, intent)
        
        return {
            "id": conversation.id,
            "message": message,
            "response": response,
            "intent": intent,
            "created_at": conversation.created_at.isoformat() if conversation.created_at else None
        }
    
    def _update_metadata(self, session_id: str, message: str, intent: str = None):
        """Update conversation metadata"""
        if session_id not in self.conversation_metadata:
            self.conversation_metadata[session_id] = {
                "start_time": datetime.now().isoformat(),
                "message_count": 0,
                "intents": {},
                "last_active": datetime.now().isoformat(),
                "topics": set()
            }
        
        meta = self.conversation_metadata[session_id]
        meta["message_count"] += 1
        meta["last_active"] = datetime.now().isoformat()
        
        if intent:
            meta["intents"][intent] = meta["intents"].get(intent, 0) + 1
        
        # Simple topic extraction
        words = message.lower().split()
        key_words = ["hello", "hi", "time", "date", "weather", "search", "open", "calculate", "calc", "help", "joke", "screenshot"]
        for word in key_words:
            if word in words:
                meta["topics"].add(word)
    
    async def get_history(
        self, 
        session_id: str, 
        limit: int = 50,
        offset: int = 0
    ) -> Dict[str, Any]:
        """Get conversation history"""
        
        # Try memory cache first
        if session_id in self.active_conversations and offset == 0:
            history = list(self.active_conversations[session_id])
            messages = history[-limit:] if limit > 0 else history
            
            return {
                "session_id": session_id,
                "messages": messages,
                "total": len(history),
                "source": "cache"
            }
        
        # Fall back to database
        async for db in get_db():
            # Get total count
            count_stmt = select(func.count()).select_from(Conversation).where(Conversation.session_id == session_id)
            count_result = await db.execute(count_stmt)
            total = count_result.scalar() or 0
            
            # Get paginated messages
            stmt = select(Conversation).where(
                Conversation.session_id == session_id
            ).order_by(desc(Conversation.created_at)).offset(offset).limit(limit)
            
            result = await db.execute(stmt)
            conversations = result.scalars().all()
            
            # Format messages
            messages = []
            for conv in reversed(conversations):
                messages.append({
                    "id": conv.id,
                    "role": "user",
                    "content": conv.message,
                    "timestamp": conv.created_at.isoformat() if conv.created_at else None
                })
                messages.append({
                    "id": conv.id,
                    "role": "assistant",
                    "content": conv.response,
                    "timestamp": conv.created_at.isoformat() if conv.created_at else None
                })
            
            return {
                "session_id": session_id,
                "messages": messages,
                "total": total,
                "offset": offset,
                "limit": limit,
                "source": "database"
            }
        
        return {
            "session_id": session_id,
            "messages": [],
            "total": 0,
            "source": "none"
        }
    
    async def get_by_id(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific conversation by ID"""
        async for db in get_db():
            conversation = await db.get(Conversation, conversation_id)
            if conversation:
                return {
                    "id": conversation.id,
                    "session_id": conversation.session_id,
                    "user_id": conversation.user_id,
                    "message": conversation.message,
                    "response": conversation.response,
                    "intent": conversation.intent,
                    "tools_used": conversation.tools_used,
                    "response_time": conversation.response_time,
                    "created_at": conversation.created_at.isoformat() if conversation.created_at else None
                }
        return None
    
    async def delete_one(self, conversation_id: str) -> bool:
        """Delete a specific conversation"""
        async for db in get_db():
            conversation = await db.get(Conversation, conversation_id)
            if conversation:
                # Remove from cache
                session_id = conversation.session_id
                if session_id in self.active_conversations:
                    self.active_conversations[session_id] = deque(
                        [msg for msg in self.active_conversations[session_id] if msg.get("id") != conversation_id],
                        maxlen=self.max_history
                    )
                
                await db.delete(conversation)
                await db.commit()
                return True
            return False
        return False
    
    async def clear_session(self, session_id: str) -> int:
        """Clear all conversations for a session"""
        # Clear cache
        if session_id in self.active_conversations:
            del self.active_conversations[session_id]
        
        if session_id in self.conversation_metadata:
            del self.conversation_metadata[session_id]
        
        # Delete from database
        async for db in get_db():
            stmt = delete(Conversation).where(Conversation.session_id == session_id)
            result = await db.execute(stmt)
            await db.commit()
            return result.rowcount
        
        return 0
    
    async def get_recent_sessions(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent conversation sessions for a user"""
        async for db in get_db():
            # Get distinct sessions
            stmt = select(Conversation.session_id, func.max(Conversation.created_at).label('last_active')).where(
                Conversation.user_id == user_id
            ).group_by(Conversation.session_id).order_by(desc('last_active')).limit(limit)
            
            result = await db.execute(stmt)
            sessions = result.fetchall()
            
            recent = []
            for session_id, last_active in sessions:
                # Get first message of session
                first_stmt = select(Conversation).where(
                    Conversation.session_id == session_id
                ).order_by(Conversation.created_at).limit(1)
                
                first_result = await db.execute(first_stmt)
                first_conv = first_result.scalar_one_or_none()
                
                # Get message count
                count_stmt = select(func.count()).select_from(Conversation).where(Conversation.session_id == session_id)
                count_result = await db.execute(count_stmt)
                message_count = count_result.scalar() or 0
                
                recent.append({
                    "session_id": session_id,
                    "first_message": first_conv.message[:100] if first_conv else "",
                    "message_count": message_count,
                    "last_active": last_active.isoformat() if last_active else None
                })
            
            return recent
        
        return []