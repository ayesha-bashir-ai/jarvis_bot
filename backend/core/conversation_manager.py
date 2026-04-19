"""
Conversation Manager for JARVIS AI Assistant
Handles conversation state, history, and management with database integration
"""

import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from collections import deque
from sqlalchemy import select, desc, delete, or_
from backend.database import get_db
from backend.models import Conversation

logger = logging.getLogger(__name__)

class ConversationManager:
    """Manages conversations and chat history with caching"""
    
    def __init__(self, max_history: int = 100):
        self.max_history = max_history
        self.active_conversations: Dict[str, deque] = {}
        self.conversation_metadata: Dict[str, Dict] = {}
        self._cache_ttl = 3600  # 1 hour cache TTL
        
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
        
        # Create conversation record
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
    
    async def get_conversation_history(
        self, 
        session_id: str, 
        limit: int = 50,
        offset: int = 0,
        include_metadata: bool = False
    ) -> Dict[str, Any]:
        """Get conversation history for a session with pagination"""
        
        # Try memory cache first for recent messages
        if session_id in self.active_conversations and offset == 0:
            history = list(self.active_conversations[session_id])
            messages = history[-limit:] if limit > 0 else history
            
            result = {
                "session_id": session_id,
                "messages": messages,
                "total": len(history),
                "source": "cache"
            }
            
            if include_metadata:
                result["metadata"] = self.conversation_metadata.get(session_id, {})
            
            return result
        
        # Fall back to database for full history
        async for db in get_db():
            # Get total count
            count_stmt = select(Conversation).where(Conversation.session_id == session_id)
            count_result = await db.execute(count_stmt)
            total = len(count_result.scalars().all())
            
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
            
            response = {
                "session_id": session_id,
                "messages": messages,
                "total": total,
                "offset": offset,
                "limit": limit,
                "source": "database"
            }
            
            if include_metadata:
                response["metadata"] = self.conversation_metadata.get(session_id, {})
            
            return response
        
        return {
            "session_id": session_id,
            "messages": [],
            "total": 0,
            "source": "none"
        }
    
    async def get_conversation_by_id(self, conversation_id: str) -> Optional[Dict[str, Any]]:
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
    
    async def search_conversations(
        self, 
        user_id: str, 
        query: str,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Search conversations by content"""
        results = []
        async for db in get_db():
            stmt = select(Conversation).where(
                Conversation.user_id == user_id,
                or_(
                    Conversation.message.contains(query),
                    Conversation.response.contains(query)
                )
            ).order_by(desc(Conversation.created_at)).limit(limit)
            
            result = await db.execute(stmt)
            conversations = result.scalars().all()
            
            for conv in conversations:
                results.append({
                    "id": conv.id,
                    "message": conv.message,
                    "response": conv.response,
                    "intent": conv.intent,
                    "created_at": conv.created_at.isoformat() if conv.created_at else None
                })
            break
        
        return results
    
    async def delete_conversation(self, conversation_id: str) -> bool:
        """Delete a specific conversation"""
        async for db in get_db():
            conversation = await db.get(Conversation, conversation_id)
            if conversation:
                # Remove from cache
                session_id = conversation.session_id
                if session_id in self.active_conversations:
                    # Filter out messages with this ID
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
    
    async def export_conversation(self, session_id: str, format: str = "json") -> str:
        """Export conversation history"""
        history = await self.get_conversation_history(session_id, limit=1000)
        messages = history.get("messages", [])
        
        if format == "json":
            export_data = {
                "session_id": session_id,
                "export_date": datetime.now().isoformat(),
                "total_messages": len(messages),
                "conversations": messages
            }
            return json.dumps(export_data, indent=2)
        
        elif format == "txt":
            lines = [
                "=" * 60,
                f"JARVIS Conversation Export",
                f"Session ID: {session_id}",
                f"Export Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                f"Total Messages: {len(messages)}",
                "=" * 60,
                ""
            ]
            
            for msg in messages:
                role = msg["role"].upper()
                content = msg["content"]
                timestamp = msg.get("timestamp", "")
                lines.append(f"[{timestamp}] {role}:")
                lines.append(content)
                lines.append("-" * 40)
                lines.append("")
            
            return "\n".join(lines)
        
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    async def get_conversation_stats(self, session_id: str) -> Dict[str, Any]:
        """Get statistics for a conversation session"""
        history = await self.get_conversation_history(session_id, limit=1000)
        messages = history.get("messages", [])
        
        user_messages = [m for m in messages if m["role"] == "user"]
        assistant_messages = [m for m in messages if m["role"] == "assistant"]
        
        # Get intent distribution from database
        intent_stats = {}
        async for db in get_db():
            stmt = select(Conversation.intent).where(Conversation.session_id == session_id)
            result = await db.execute(stmt)
            intents = result.scalars().all()
            
            for intent in intents:
                if intent:
                    intent_stats[intent] = intent_stats.get(intent, 0) + 1
            break
        
        metadata = self.conversation_metadata.get(session_id, {})
        
        return {
            "session_id": session_id,
            "total_messages": len(messages),
            "user_messages": len(user_messages),
            "assistant_messages": len(assistant_messages),
            "average_user_length": round(sum(len(m["content"]) for m in user_messages) / max(len(user_messages), 1), 2),
            "average_assistant_length": round(sum(len(m["content"]) for m in assistant_messages) / max(len(assistant_messages), 1), 2),
            "intent_distribution": intent_stats,
            "topics": list(metadata.get("topics", [])),
            "start_time": metadata.get("start_time"),
            "last_active": metadata.get("last_active"),
            "message_count": metadata.get("message_count", 0)
        }
    
    async def get_recent_conversations(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent conversations for a user (unique sessions)"""
        async for db in get_db():
            # Get distinct sessions
            stmt = select(Conversation.session_id, Conversation.created_at).where(
                Conversation.user_id == user_id
            ).order_by(desc(Conversation.created_at)).distinct().limit(limit)
            
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
                count_stmt = select(Conversation).where(Conversation.session_id == session_id)
                count_result = await db.execute(count_stmt)
                message_count = len(count_result.scalars().all())
                
                recent.append({
                    "session_id": session_id,
                    "first_message": first_conv.message[:100] if first_conv else "",
                    "message_count": message_count,
                    "last_active": last_active.isoformat() if last_active else None
                })
            
            return recent
        
        return []
    
    async def update_conversation_metadata(self, session_id: str, key: str, value: Any):
        """Update custom metadata for a conversation"""
        if session_id not in self.conversation_metadata:
            self.conversation_metadata[session_id] = {
                "start_time": datetime.now().isoformat(),
                "message_count": 0,
                "intents": {},
                "last_active": datetime.now().isoformat(),
                "topics": set(),
                "custom": {}
            }
        
        if "custom" not in self.conversation_metadata[session_id]:
            self.conversation_metadata[session_id]["custom"] = {}
        
        self.conversation_metadata[session_id]["custom"][key] = value
    
    async def get_conversation_summary(self, session_id: str) -> str:
        """Generate a human-readable summary of the conversation"""
        stats = await self.get_conversation_stats(session_id)
        history = await self.get_conversation_history(session_id, limit=20)
        messages = history.get("messages", [])
        
        if stats["total_messages"] == 0:
            return "No conversation history available for this session."
        
        # Build summary
        summary_lines = [
            "📊 Conversation Summary",
            "=" * 40,
            f"Session ID: {session_id[:8]}...",
            f"Total Messages: {stats['total_messages']}",
            f"User Messages: {stats['user_messages']}",
            f"Assistant Messages: {stats['assistant_messages']}",
            f"Average Response Length: {stats['average_assistant_length']} characters",
            ""
        ]
        
        if stats["intent_distribution"]:
            summary_lines.append("📋 Intent Distribution:")
            for intent, count in stats["intent_distribution"].items():
                summary_lines.append(f"  • {intent}: {count} times")
            summary_lines.append("")
        
        if stats["topics"]:
            summary_lines.append("🏷️ Topics Discussed:")
            summary_lines.append(f"  {', '.join(stats['topics'])}")
            summary_lines.append("")
        
        # Last few messages
        if messages:
            summary_lines.append("💬 Recent Activity:")
            last_messages = messages[-4:] if len(messages) >= 4 else messages
            for msg in last_messages:
                role = "👤 User" if msg["role"] == "user" else "🤖 JARVIS"
                content = msg["content"][:80] + "..." if len(msg["content"]) > 80 else msg["content"]
                summary_lines.append(f"  {role}: {content}")
        
        return "\n".join(summary_lines)