import logging
from datetime import datetime
from typing import Optional
from fastapi import BackgroundTasks, HTTPException
from backend.api.routes import ChatRequest, ChatResponse
from backend.core.jarvis_brain import get_brain_instance
from backend.database import get_db
from backend.models import Conversation

logger = logging.getLogger(__name__)

async def handle_chat(request: ChatRequest, background_tasks: BackgroundTasks) -> ChatResponse:
    """Handle chat request"""
    try:
        brain = get_brain_instance()
        
        # Process message through brain
        result = await brain.process_message(
            message=request.message,
            session_id=request.session_id,
            user_id=request.user_id
        )
        
        # Store conversation in background
        background_tasks.add_task(
            store_conversation,
            request.session_id,
            request.user_id,
            request.message,
            result["message"],
            result["intent"]
        )
        
        return ChatResponse(
            message=result["message"],
            intent=result["intent"],
            tools_used=result["tools_used"],
            response_time=result["response_time"]
        )
        
    except Exception as e:
        logger.error(f"Chat handler error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def store_conversation(session_id: str, user_id: str, message: str, response: str, intent: str):
    """Store conversation in database"""
    try:
        async for db in get_db():
            conv = Conversation(
                session_id=session_id,
                user_id=user_id,
                message=message,
                response=response,
                intent=intent
            )
            db.add(conv)
            await db.commit()
            break
    except Exception as e:
        logger.error(f"Failed to store conversation: {e}")