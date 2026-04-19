from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, Dict, Any
import logging
from backend.api.chat import handle_chat
from backend.api.voice import handle_voice_command
from backend.api.tools import handle_tool_execution
from backend.core.jarvis_brain import JarvisBrain
from backend.services.llm_service import LLMService

router = APIRouter()
logger = logging.getLogger(__name__)

class ChatRequest(BaseModel):
    message: str
    session_id: str
    user_id: Optional[str] = "default"

class ChatResponse(BaseModel):
    message: str
    intent: str
    tools_used: list
    response_time: int

class VoiceCommandRequest(BaseModel):
    audio_data: Optional[str] = None
    session_id: str
    user_id: Optional[str] = "default"

class ToolRequest(BaseModel):
    tool_name: str
    parameters: Dict[str, Any]
    session_id: str

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest, background_tasks: BackgroundTasks):
    """Main chat endpoint for JARVIS"""
    try:
        response = await handle_chat(request, background_tasks)
        return response
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/voice/command")
async def voice_command_endpoint(request: VoiceCommandRequest):
    """Handle voice commands"""
    try:
        response = await handle_voice_command(request)
        return response
    except Exception as e:
        logger.error(f"Voice command error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/tools/execute")
async def execute_tool(request: ToolRequest):
    """Execute a specific tool"""
    try:
        result = await handle_tool_execution(request)
        return {"success": True, "result": result}
    except Exception as e:
        logger.error(f"Tool execution error: {e}")
        return {"success": False, "error": str(e)}

@router.get("/memory/{session_id}")
async def get_memory(session_id: str, limit: int = 10):
    """Get conversation memory for a session"""
    # Implementation
    return {"session_id": session_id, "messages": []}

@router.delete("/memory/{session_id}")
async def clear_memory(session_id: str):
    """Clear conversation memory for a session"""
    # Implementation
    return {"status": "cleared", "session_id": session_id}