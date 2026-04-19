"""
Memory System Tests for JARVIS AI Assistant
Tests database operations and memory management
"""

import pytest
import asyncio
import json
from datetime import datetime, timedelta
from backend.database import init_db, get_db, engine
from backend.models import Conversation, Memory, UserProfile, ToolUsage

class TestDatabaseModels:
    """Test database models"""
    
    @pytest.mark.asyncio
    async def test_create_conversation(self):
        """Test creating conversation record"""
        async for db in get_db():
            conversation = Conversation(
                id="test-conv-1",
                session_id="test_session",
                user_id="test_user",
                message="Hello JARVIS",
                response="Hello Commander!",
                intent="greeting",
                tools_used=["none"]
            )
            db.add(conversation)
            await db.commit()
            
            # Verify
            result = await db.get(Conversation, "test-conv-1")
            assert result is not None
            assert result.message == "Hello JARVIS"
            assert result.response == "Hello Commander!"
            break
    
    @pytest.mark.asyncio
    async def test_create_memory(self):
        """Test creating memory record"""
        async for db in get_db():
            memory = Memory(
                id="test-mem-1",
                user_id="test_user",
                key="user_name",
                value="John",
                memory_type="long_term"
            )
            db.add(memory)
            await db.commit()
            
            # Verify
            result = await db.get(Memory, "test-mem-1")
            assert result is not None
            assert result.key == "user_name"
            assert result.value == "John"
            break
    
    @pytest.mark.asyncio
    async def test_create_user_profile(self):
        """Test creating user profile"""
        async for db in get_db():
            profile = UserProfile(
                id="test-profile-1",
                user_id="test_user",
                name="Test User",
                preferences=json.dumps({"theme": "dark"}),
                settings=json.dumps({"voice": True})
            )
            db.add(profile)
            await db.commit()
            
            # Verify
            result = await db.get(UserProfile, "test-profile-1")
            assert result is not None
            assert result.name == "Test User"
            break
    
    @pytest.mark.asyncio
    async def test_create_tool_usage(self):
        """Test creating tool usage record"""
        async for db in get_db():
            tool_usage = ToolUsage(
                id="test-tool-1",
                tool_name="calculator",
                session_id="test_session",
                parameters=json.dumps({"expression": "5+3"}),
                result="8",
                success=True,
                execution_time=100
            )
            db.add(tool_usage)
            await db.commit()
            
            # Verify
            result = await db.get(ToolUsage, "test-tool-1")
            assert result is not None
            assert result.tool_name == "calculator"
            assert result.success is True
            break
    
    @pytest.mark.asyncio
    async def test_query_conversations(self):
        """Test querying conversations"""
        async for db in get_db():
            from sqlalchemy import select
            
            # Add multiple conversations
            for i in range(3):
                conv = Conversation(
                    id=f"test-conv-{i}",
                    session_id="query_test",
                    user_id="test_user",
                    message=f"Message {i}",
                    response=f"Response {i}",
                    intent="test"
                )
                db.add(conv)
            await db.commit()
            
            # Query
            stmt = select(Conversation).where(Conversation.session_id == "query_test")
            result = await db.execute(stmt)
            conversations = result.scalars().all()
            
            assert len(conversations) == 3
            break

class TestMemoryOperations:
    """Test memory operations"""
    
    @pytest.mark.asyncio
    async def test_store_and_retrieve_memory(self):
        """Test storing and retrieving memories"""
        async for db in get_db():
            # Store
            memory = Memory(
                id="test-mem-store",
                user_id="memory_user",
                key="test_key",
                value="test_value",
                memory_type="short_term"
            )
            db.add(memory)
            await db.commit()
            
            # Retrieve
            result = await db.get(Memory, "test-mem-store")
            assert result is not None
            assert result.value == "test_value"
            break
    
    @pytest.mark.asyncio
    async def test_update_memory(self):
        """Test updating memory"""
        async for db in get_db():
            # Create
            memory = Memory(
                id="test-mem-update",
                user_id="update_user",
                key="update_key",
                value="old_value",
                memory_type="long_term"
            )
            db.add(memory)
            await db.commit()
            
            # Update
            memory.value = "new_value"
            await db.commit()
            
            # Verify
            result = await db.get(Memory, "test-mem-update")
            assert result.value == "new_value"
            break
    
    @pytest.mark.asyncio
    async def test_delete_memory(self):
        """Test deleting memory"""
        async for db in get_db():
            # Create
            memory = Memory(
                id="test-mem-delete",
                user_id="delete_user",
                key="delete_key",
                value="to_delete",
                memory_type="short_term"
            )
            db.add(memory)
            await db.commit()
            
            # Delete
            await db.delete(memory)
            await db.commit()
            
            # Verify
            result = await db.get(Memory, "test-mem-delete")
            assert result is None
            break

class TestUserProfileOperations:
    """Test user profile operations"""
    
    @pytest.mark.asyncio
    async def test_create_and_find_profile(self):
        """Test creating and finding user profile"""
        async for db in get_db():
            profile = UserProfile(
                id="test-profile-find",
                user_id="find_user",
                name="Finder",
                preferences='{"theme": "light"}',
                settings='{"notifications": true}'
            )
            db.add(profile)
            await db.commit()
            
            # Find by user_id
            from sqlalchemy import select
            stmt = select(UserProfile).where(UserProfile.user_id == "find_user")
            result = await db.execute(stmt)
            found = result.scalar_one()
            
            assert found is not None
            assert found.name == "Finder"
            break
    
    @pytest.mark.asyncio
    async def test_update_profile_preferences(self):
        """Test updating profile preferences"""
        async for db in get_db():
            profile = UserProfile(
                id="test-profile-pref",
                user_id="pref_user",
                name="Pref User",
                preferences='{"theme": "dark"}',
                settings='{}'
            )
            db.add(profile)
            await db.commit()
            
            # Update preferences
            profile.preferences = json.dumps({"theme": "light", "voice": True})
            await db.commit()
            
            # Verify
            prefs = json.loads(profile.preferences)
            assert prefs["theme"] == "light"
            assert prefs["voice"] is True
            break

if __name__ == "__main__":
    pytest.main([__file__, "-v"])