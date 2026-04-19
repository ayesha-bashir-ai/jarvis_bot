import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from collections import deque
from backend.database import get_db
from backend.models import Memory, ChatMessage

logger = logging.getLogger(__name__)

class MemoryManager:
    """Manages conversation memory and context"""
    
    def __init__(self, max_short_term: int = 50):
        self.max_short_term = max_short_term
        self.short_term_memory: Dict[str, deque] = {}
        self.long_term_cache: Dict[str, List[Dict]] = {}
    
    def get_recent_messages(self, session_id: str, limit: int = 10) -> List[Dict]:
        """Get recent messages for a session"""
        if session_id not in self.short_term_memory:
            return []
        
        messages = list(self.short_term_memory[session_id])
        return messages[-limit:]
    
    def add_message(self, session_id: str, role: str, content: str, metadata: Dict = None):
        """Add message to short-term memory"""
        if session_id not in self.short_term_memory:
            self.short_term_memory[session_id] = deque(maxlen=self.max_short_term)
        
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        
        self.short_term_memory[session_id].append(message)
    
    async def get_long_term_memory(self, user_id: str, limit: int = 20) -> List[Dict]:
        """Retrieve long-term memories for a user"""
        if user_id in self.long_term_cache:
            return self.long_term_cache[user_id][:limit]
        
        memories = []
        async for db in get_db():
            from sqlalchemy import select
            stmt = select(Memory).where(
                Memory.user_id == user_id,
                Memory.memory_type == "long_term"
            ).order_by(Memory.created_at.desc()).limit(limit)
            
            result = await db.execute(stmt)
            memories = result.scalars().all()
            
            # Cache results
            self.long_term_cache[user_id] = [
                {"key": m.key, "value": json.loads(m.value) if isinstance(m.value, str) else m.value}
                for m in memories
            ]
            break
        
        return self.long_term_cache.get(user_id, [])[:limit]
    
    async def store_memory(self, user_id: str, key: str, value: Any, memory_type: str = "short_term"):
        """Store memory in database"""
        async for db in get_db():
            memory = Memory(
                user_id=user_id,
                key=key,
                value=json.dumps(value) if not isinstance(value, str) else value,
                memory_type=memory_type
            )
            db.add(memory)
            await db.commit()
            
            # Update cache
            if memory_type == "long_term":
                if user_id not in self.long_term_cache:
                    self.long_term_cache[user_id] = []
                self.long_term_cache[user_id].insert(0, {"key": key, "value": value})
                self.long_term_cache[user_id] = self.long_term_cache[user_id][:100]
            break
    
    async def clear_session(self, session_id: str):
        """Clear all memories for a session"""
        if session_id in self.short_term_memory:
            del self.short_term_memory[session_id]
        
        async for db in get_db():
            from sqlalchemy import delete
            stmt = delete(Memory).where(Memory.key == session_id)
            await db.execute(stmt)
            await db.commit()
            break
    
    def get_context_string(self, session_id: str, include_long_term: bool = False) -> str:
        """Generate context string from memory"""
        recent = self.get_recent_messages(session_id, limit=10)
        
        context_lines = []
        for msg in recent:
            role = "User" if msg["role"] == "user" else "Assistant"
            context_lines.append(f"{role}: {msg['content']}")
        
        return "\n".join(context_lines)
    
    async def extract_facts(self, session_id: str, message: str, response: str) -> List[Dict]:
        """Extract important facts from conversation"""
        facts = []
        
        # Look for personal information
        patterns = {
            "name": r"my name is (\w+)",
            "age": r"i am (\d+) years old",
            "location": r"i live in (\w+)",
            "job": r"i work as a? (\w+)",
            "preference": r"i (like|prefer) (\w+)"
        }
        
        for fact_type, pattern in patterns.items():
            import re
            match = re.search(pattern, message.lower())
            if match:
                facts.append({
                    "type": fact_type,
                    "value": match.group(1),
                    "source": message
                })
        
        return facts