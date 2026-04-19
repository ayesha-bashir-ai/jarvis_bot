import logging
from fastapi import HTTPException
from backend.api.routes import ToolRequest
from backend.tools import get_tool_registry

logger = logging.getLogger(__name__)

async def handle_tool_execution(request: ToolRequest):
    """Execute a specific tool"""
    try:
        registry = get_tool_registry()
        
        if not registry.has_tool(request.tool_name):
            raise HTTPException(status_code=404, detail=f"Tool '{request.tool_name}' not found")
        
        tool = registry.get_tool(request.tool_name)
        result = await tool.execute(
            parameters=request.parameters,
            session_id=request.session_id
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Tool execution error: {e}")
        raise HTTPException(status_code=500, detail=str(e))