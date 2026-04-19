"""
Tool Tests for JARVIS AI Assistant
Tests all tool functionality
"""

import pytest
import asyncio
from unittest.mock import Mock, patch
from backend.tools.calculator_tool import CalculatorTool
from backend.tools.web_tools import WebTools
from backend.tools.system_tools import SystemTools
from backend.tools.search_tools import SearchTools
from backend.tools.base_tool import ToolRegistry

class TestCalculatorTool:
    """Test calculator tool"""
    
    def setup_method(self):
        self.tool = CalculatorTool()
    
    @pytest.mark.asyncio
    async def test_basic_addition(self):
        """Test basic addition"""
        result = await self.tool.execute({"expression": "5 + 3"})
        assert result["success"] is True
        assert "8" in result["result"]
    
    @pytest.mark.asyncio
    async def test_basic_subtraction(self):
        """Test subtraction"""
        result = await self.tool.execute({"expression": "10 - 4"})
        assert result["success"] is True
        assert "6" in result["result"]
    
    @pytest.mark.asyncio
    async def test_multiplication(self):
        """Test multiplication"""
        result = await self.tool.execute({"expression": "7 * 8"})
        assert result["success"] is True
        assert "56" in result["result"]
    
    @pytest.mark.asyncio
    async def test_division(self):
        """Test division"""
        result = await self.tool.execute({"expression": "15 / 3"})
        assert result["success"] is True
        assert "5" in result["result"]
    
    @pytest.mark.asyncio
    async def test_complex_expression(self):
        """Test complex expression"""
        result = await self.tool.execute({"expression": "(10 + 5) * 2"})
        assert result["success"] is True
        assert "30" in result["result"]
    
    @pytest.mark.asyncio
    async def test_invalid_expression(self):
        """Test invalid expression handling"""
        result = await self.tool.execute({"expression": "invalid expression"})
        assert result["success"] is False
        assert "error" in result
    
    @pytest.mark.asyncio
    async def test_empty_expression(self):
        """Test empty expression"""
        result = await self.tool.execute({"expression": ""})
        assert result["success"] is False

class TestWebTools:
    """Test web tools"""
    
    def setup_method(self):
        self.tool = WebTools()
    
    @pytest.mark.asyncio
    async def test_open_website(self):
        """Test opening website"""
        with patch('webbrowser.open') as mock_open:
            result = await self.tool.execute({
                "action": "open",
                "website": "youtube"
            })
            assert result["success"] is True
            mock_open.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_open_unknown_website(self):
        """Test opening unknown website"""
        result = await self.tool.execute({
            "action": "open",
            "website": "unknown_site"
        })
        assert result["success"] is False
    
    @pytest.mark.asyncio
    async def test_search_web(self):
        """Test web search"""
        with patch('webbrowser.open') as mock_open:
            result = await self.tool.execute({
                "action": "search",
                "query": "Python programming"
            })
            assert result["success"] is True
            mock_open.assert_called_once()

class TestSystemTools:
    """Test system tools"""
    
    def setup_method(self):
        self.tool = SystemTools()
    
    @pytest.mark.asyncio
    async def test_take_screenshot(self):
        """Test screenshot functionality"""
        with patch('pyautogui.screenshot') as mock_screenshot:
            mock_screenshot.return_value = Mock()
            result = await self.tool.execute({"action": "screenshot"})
            assert result["success"] is True
            assert "filepath" in result
    
    @pytest.mark.asyncio
    async def test_open_application(self):
        """Test opening application"""
        with patch('subprocess.Popen') as mock_popen:
            result = await self.tool.execute({
                "action": "open_app",
                "app": "notepad"
            })
            assert result["success"] is True
    
    @pytest.mark.asyncio
    async def test_unknown_action(self):
        """Test unknown action"""
        result = await self.tool.execute({"action": "unknown"})
        assert result["success"] is False

class TestSearchTools:
    """Test search tools"""
    
    def setup_method(self):
        self.tool = SearchTools()
    
    @pytest.mark.asyncio
    async def test_search_query(self):
        """Test search functionality"""
        result = await self.tool.execute({"query": "Python"})
        assert "success" in result
        # Search might fail without API key, but should still return result
        assert result is not None
    
    @pytest.mark.asyncio
    async def test_empty_search(self):
        """Test empty search"""
        result = await self.tool.execute({"query": ""})
        assert result["success"] is False

class TestToolRegistry:
    """Test tool registry"""
    
    def setup_method(self):
        self.registry = ToolRegistry()
        self.registry.register_tools()
    
    def test_has_tool(self):
        """Test tool existence check"""
        assert self.registry.has_tool("calculator") is True
        assert self.registry.has_tool("web_tools") is True
        assert self.registry.has_tool("nonexistent") is False
    
    def test_get_tool(self):
        """Test tool retrieval"""
        tool = self.registry.get_tool("calculator")
        assert tool is not None
        assert tool.name == "calculator"
    
    def test_list_tools(self):
        """Test listing all tools"""
        tools = self.registry.list_tools()
        assert len(tools) > 0
        tool_names = [t["name"] for t in tools]
        assert "calculator" in tool_names
        assert "web_tools" in tool_names