from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class BaseTool(ABC):
    """Base class for all tools"""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
    
    @abstractmethod
    async def execute(self, parameters: Dict[str, Any], session_id: str = None) -> Dict[str, Any]:
        """Execute the tool with given parameters"""
        pass
    
    def get_info(self) -> Dict[str, Any]:
        """Get tool information"""
        return {
            "name": self.name,
            "description": self.description
        }

class ToolRegistry:
    """Registry for managing tools"""
    
    def __init__(self):
        self.tools: Dict[str, BaseTool] = {}
    
    def register(self, tool: BaseTool):
        """Register a tool"""
        self.tools[tool.name] = tool
        logger.info(f"Registered tool: {tool.name}")
    
    def get_tool(self, name: str) -> Optional[BaseTool]:
        """Get a tool by name"""
        return self.tools.get(name)
    
    def has_tool(self, name: str) -> bool:
        """Check if tool exists"""
        return name in self.tools
    
    def list_tools(self) -> list:
        """List all registered tools"""
        return [tool.get_info() for tool in self.tools.values()]
    
    def register_tools(self):
        """Register all available tools"""
        from backend.tools.web_tools import WebTools
        from backend.tools.system_tools import SystemTools
        from backend.tools.calculator_tool import CalculatorTool
        from backend.tools.file_tools import FileTools
        from backend.tools.search_tools import SearchTools
        from backend.tools.weather_tools import WeatherTools
        
        self.register(WebTools())
        self.register(SystemTools())
        self.register(CalculatorTool())
        self.register(FileTools())
        self.register(SearchTools())
        self.register(WeatherTools())