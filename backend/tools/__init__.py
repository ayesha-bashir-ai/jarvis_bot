from backend.tools.base_tool import BaseTool, ToolRegistry
from backend.tools.web_tools import WebTools
from backend.tools.system_tools import SystemTools
from backend.tools.calculator_tool import CalculatorTool
from backend.tools.file_tools import FileTools
from backend.tools.search_tools import SearchTools
from backend.tools.weather_tools import WeatherTools

_tool_registry = None

def get_tool_registry() -> ToolRegistry:
    """Get or create tool registry singleton"""
    global _tool_registry
    if _tool_registry is None:
        _tool_registry = ToolRegistry()
        _tool_registry.register_tools()
    return _tool_registry

__all__ = [
    "BaseTool",
    "ToolRegistry",
    "get_tool_registry",
    "WebTools",
    "SystemTools",
    "CalculatorTool",
    "FileTools",
    "SearchTools",
    "WeatherTools"
]