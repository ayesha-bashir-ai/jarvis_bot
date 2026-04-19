"""
API Tests for JARVIS AI Assistant
Tests all API endpoints functionality
"""

import pytest
import asyncio
import json
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

class TestAPI:
    """Test API endpoints"""
    
    def test_root_endpoint(self):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert data["name"] == "JARVIS AI Assistant"
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "services" in data
    
    def test_system_info(self):
        """Test system info endpoint"""
        response = client.get("/info")
        assert response.status_code == 200
        data = response.json()
        assert "model" in data
        assert "voice_enabled" in data
    
    def test_chat_endpoint(self):
        """Test chat endpoint"""
        test_message = "Hello JARVIS"
        response = client.post(
            "/api/v1/chat",
            json={
                "message": test_message,
                "session_id": "test_session",
                "user_id": "test_user"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "intent" in data
        assert "response_time" in data
    
    def test_chat_with_calculation(self):
        """Test chat with calculation"""
        response = client.post(
            "/api/v1/chat",
            json={
                "message": "Calculate 5 + 3",
                "session_id": "test_session",
                "user_id": "test_user"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "calculator" in data.get("tools_used", []) or "calculation" in data["message"].lower()
    
    def test_invalid_chat_request(self):
        """Test invalid chat request"""
        response = client.post("/api/v1/chat", json={})
        assert response.status_code == 422  # Validation error
    
    def test_voice_command_endpoint(self):
        """Test voice command endpoint"""
        response = client.post(
            "/api/v1/voice/command",
            json={
                "session_id": "test_session",
                "user_id": "test_user"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "success" in data or "command" in data
    
    def test_tool_execution(self):
        """Test tool execution endpoint"""
        response = client.post(
            "/api/v1/tools/execute",
            json={
                "tool_name": "calculator",
                "parameters": {"expression": "10 * 5"},
                "session_id": "test_session"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "success" in data or "result" in data
    
    def test_memory_endpoint(self):
        """Test memory retrieval endpoint"""
        response = client.get("/api/v1/memory/test_session?limit=5")
        assert response.status_code in [200, 404]  # 404 if no memory
    
    def test_clear_memory(self):
        """Test clear memory endpoint"""
        response = client.delete("/api/v1/memory/test_session")
        assert response.status_code in [200, 404]

class TestWebSocket:
    """Test WebSocket connections"""
    
    def test_websocket_connection(self):
        """Test WebSocket connection"""
        # This is a placeholder - WebSocket testing requires special setup
        pass

if __name__ == "__main__":
    pytest.main([__file__, "-v"])