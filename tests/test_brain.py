"""
Brain Logic Tests for JARVIS AI Assistant
Tests intent detection, memory management, and decision making
"""

import pytest
import asyncio
from unittest.mock import Mock, patch
from backend.core.jarvis_brain import JarvisBrain
from backend.core.intent_detector import IntentDetector
from backend.core.memory_manager import MemoryManager
from backend.core.context_handler import ContextHandler

class TestIntentDetector:
    """Test intent detection logic"""
    
    def setup_method(self):
        self.detector = IntentDetector()
    
    @pytest.mark.asyncio
    async def test_greeting_intent(self):
        """Test greeting intent detection"""
        intents = [
            "Hello JARVIS",
            "Hi there",
            "Good morning",
            "Hey JARVIS"
        ]
        
        for message in intents:
            intent = await self.detector.detect_intent(message)
            assert intent["type"].value == "greeting" or intent["name"] == "greeting"
    
    @pytest.mark.asyncio
    async def test_calculation_intent(self):
        """Test calculation intent detection"""
        intent = await self.detector.detect_intent("Calculate 5 + 3")
        assert intent["requires_tool"] is True
        assert "calculator" in intent["tools"]
    
    @pytest.mark.asyncio
    async def test_browser_intent(self):
        """Test browser intent detection"""
        intent = await self.detector.detect_intent("Open YouTube")
        assert intent["requires_tool"] is True
        assert "open_youtube" in intent["tools"]
    
    @pytest.mark.asyncio
    async def test_search_intent(self):
        """Test search intent detection"""
        intent = await self.detector.detect_intent("Search for Python tutorials")
        assert intent["requires_tool"] is True
        assert "web_search" in intent["tools"]
    
    @pytest.mark.asyncio
    async def test_time_intent(self):
        """Test time query detection"""
        intent = await self.detector.detect_intent("What time is it?")
        # Should not require tool, handled by LLM
        assert intent is not None

class TestMemoryManager:
    """Test memory management"""
    
    def setup_method(self):
        self.memory = MemoryManager()
        self.session_id = "test_session"
    
    def test_add_message_to_memory(self):
        """Test adding messages to memory"""
        self.memory.add_message(self.session_id, "user", "Hello JARVIS")
        self.memory.add_message(self.session_id, "assistant", "Hello Commander!")
        
        messages = self.memory.get_recent_messages(self.session_id)
        assert len(messages) == 2
        assert messages[0]["role"] == "user"
        assert messages[1]["role"] == "assistant"
    
    def test_memory_limit(self):
        """Test memory size limit"""
        # Add more than max messages
        for i in range(60):
            self.memory.add_message(self.session_id, "user", f"Message {i}")
        
        messages = self.memory.get_recent_messages(self.session_id)
        assert len(messages) <= 50  # Max size is 50
    
    def test_get_context_string(self):
        """Test context string generation"""
        self.memory.add_message(self.session_id, "user", "Hello")
        self.memory.add_message(self.session_id, "assistant", "Hi there")
        
        context = self.memory.get_context_string(self.session_id)
        assert "User: Hello" in context
        assert "Assistant: Hi there" in context
    
    @pytest.mark.asyncio
    async def test_extract_facts(self):
        """Test fact extraction from messages"""
        facts = await self.memory.extract_facts(
            self.session_id,
            "My name is John and I like Python",
            "Nice to meet you John"
        )
        
        assert len(facts) >= 1
        names = [f for f in facts if f["type"] == "name"]
        assert len(names) > 0

class TestContextHandler:
    """Test context management"""
    
    def setup_method(self):
        self.handler = ContextHandler()
        self.session_id = "test_session"
    
    def test_get_context(self):
        """Test context retrieval"""
        context = self.handler.get_context(self.session_id)
        assert context is not None
        assert "session_id" in context
        assert "message_count" in context
    
    def test_update_context(self):
        """Test context updates"""
        self.handler.update_context(self.session_id, {"current_intent": "greeting"})
        context = self.handler.get_context(self.session_id)
        assert context["current_intent"] == "greeting"
    
    def test_add_entity(self):
        """Test entity management"""
        self.handler.add_entity(self.session_id, "user_name", "John")
        entity = self.handler.get_entity(self.session_id, "user_name")
        assert entity == "John"
    
    def test_clear_context(self):
        """Test context clearing"""
        self.handler.update_context(self.session_id, {"test": "value"})
        self.handler.clear_context(self.session_id)
        
        # Should get fresh context
        context = self.handler.get_context(self.session_id)
        assert context["message_count"] == 0

class TestJarvisBrain:
    """Test JARVIS brain logic"""
    
    @pytest.mark.asyncio
    async def test_process_message(self, mock_llm_service):
        """Test message processing"""
        brain = JarvisBrain(mock_llm_service)
        
        result = await brain.process_message(
            message="Hello JARVIS",
            session_id="test_session",
            user_id="test_user"
        )
        
        assert "message" in result
        assert "intent" in result
        assert "response_time" in result
    
    @pytest.mark.asyncio
    async def test_get_context(self, mock_llm_service):
        """Test context retrieval"""
        brain = JarvisBrain(mock_llm_service)
        
        context = await brain.get_context("test_session")
        assert "session_id" in context
        assert "recent_messages" in context
    
    @pytest.mark.asyncio
    async def test_clear_context(self, mock_llm_service):
        """Test context clearing"""
        brain = JarvisBrain(mock_llm_service)
        
        # Add some context
        await brain.process_message("Hello", "test_session")
        
        # Clear it
        await brain.clear_context("test_session")
        
        # Get new context
        context = await brain.get_context("test_session")
        assert len(context["recent_messages"]) == 0

@pytest.fixture
def mock_llm_service():
    """Mock LLM service for testing"""
    mock = Mock()
    mock.generate_response = Mock(return_value={
        "text": "Mock response",
        "metadata": {}
    })
    return mock