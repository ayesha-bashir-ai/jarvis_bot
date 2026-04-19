"""
Conversation API Endpoints for JARVIS AI Assistant
Provides REST endpoints for conversation management
"""

from fastapi import APIRouter, HTTPException, Query, Path
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from backend.core.conversation_manager import ConversationManager

router = APIRouter(prefix="/conversations", tags=["conversations"])
conversation_manager = ConversationManager()

# Request/Response Models
class MessageResponse(BaseModel):
    id: str
    role: str
    content: str
    timestamp: Optional[str] = None

class ConversationHistoryResponse(BaseModel):
    session_id: str
    messages: List[MessageResponse]
    total: int
    offset: int = 0
    limit: int = 50
    source: str = "database"
    metadata: Optional[Dict[str, Any]] = None

class ConversationStatsResponse(BaseModel):
    session_id: str
    total_messages: int
    user_messages: int
    assistant_messages: int
    average_user_length: float
    average_assistant_length: float
    intent_distribution: Dict[str, int]
    topics: List[str]
    start_time: Optional[str] = None
    last_active: Optional[str] = None
    message_count: int

class DeleteResponse(BaseModel):
    session_id: str
    deleted_count: int
    success: bool

class SearchResult(BaseModel):
    id: str
    message: str
    response: str
    intent: Optional[str] = None
    created_at: Optional[str] = None

class SearchResponse(BaseModel):
    user_id: str
    query: str
    count: int
    results: List[SearchResult]

class RecentConversation(BaseModel):
    session_id: str
    first_message: str
    message_count: int
    last_active: Optional[str] = None

# API Endpoints
@router.get("/{session_id}", response_model=ConversationHistoryResponse)
async def get_conversation_history(
    session_id: str = Path(..., description="Session ID"),
    limit: int = Query(50, ge=1, le=200, description="Number of messages to return"),
    offset: int = Query(0, ge=0, description="Number of messages to skip"),
    include_metadata: bool = Query(False, description="Include metadata in response")
):
    """
    Get conversation history for a session with pagination support.
    Returns messages in chronological order (oldest first).
    """
    try:
        history = await conversation_manager.get_conversation_history(
            session_id, limit, offset, include_metadata
        )
        
        # Format messages for response
        messages = []
        for msg in history.get("messages", []):
            messages.append(MessageResponse(
                id=msg.get("id", ""),
                role=msg.get("role", ""),
                content=msg.get("content", ""),
                timestamp=msg.get("timestamp")
            ))
        
        return ConversationHistoryResponse(
            session_id=session_id,
            messages=messages,
            total=history.get("total", 0),
            offset=offset,
            limit=limit,
            source=history.get("source", "database"),
            metadata=history.get("metadata") if include_metadata else None
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{session_id}/stats", response_model=ConversationStatsResponse)
async def get_conversation_stats(
    session_id: str = Path(..., description="Session ID")
):
    """
    Get detailed statistics for a conversation session including:
    - Message counts
    - Average lengths
    - Intent distribution
    - Topics discussed
    """
    try:
        stats = await conversation_manager.get_conversation_stats(session_id)
        return ConversationStatsResponse(**stats)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{session_id}/summary")
async def get_conversation_summary(
    session_id: str = Path(..., description="Session ID")
):
    """
    Get a human-readable summary of the conversation.
    Returns a text summary with key insights.
    """
    try:
        summary = await conversation_manager.get_conversation_summary(session_id)
        return {
            "session_id": session_id,
            "summary": summary,
            "generated_at": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{session_id}/export")
async def export_conversation(
    session_id: str = Path(..., description="Session ID"),
    format: str = Query("json", regex="^(json|txt)$", description="Export format")
):
    """
    Export conversation history in JSON or TXT format.
    Returns a downloadable file.
    """
    try:
        from fastapi.responses import Response
        
        export_data = await conversation_manager.export_conversation(session_id, format)
        
        content_type = "application/json" if format == "json" else "text/plain"
        filename = f"conversation_{session_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{format}"
        
        return Response(
            content=export_data,
            media_type=content_type,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{session_id}", response_model=DeleteResponse)
async def clear_conversation(
    session_id: str = Path(..., description="Session ID")
):
    """
    Clear all conversations for a session.
    This action cannot be undone.
    """
    try:
        deleted_count = await conversation_manager.clear_session(session_id)
        return DeleteResponse(
            session_id=session_id,
            deleted_count=deleted_count,
            success=deleted_count >= 0
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/message/{conversation_id}")
async def get_conversation_by_id(
    conversation_id: str = Path(..., description="Conversation ID")
):
    """
    Get a specific conversation by its ID.
    """
    try:
        conversation = await conversation_manager.get_conversation_by_id(conversation_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        return conversation
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/message/{conversation_id}")
async def delete_conversation_by_id(
    conversation_id: str = Path(..., description="Conversation ID")
):
    """
    Delete a specific conversation by its ID.
    """
    try:
        deleted = await conversation_manager.delete_conversation(conversation_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Conversation not found")
        return {
            "conversation_id": conversation_id,
            "deleted": True,
            "message": "Conversation deleted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search/{user_id}", response_model=SearchResponse)
async def search_conversations(
    user_id: str = Path(..., description="User ID"),
    query: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(20, ge=1, le=100, description="Maximum results to return")
):
    """
    Search conversations by message or response content.
    """
    try:
        results = await conversation_manager.search_conversations(user_id, query, limit)
        return SearchResponse(
            user_id=user_id,
            query=query,
            count=len(results),
            results=results
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/recent/{user_id}")
async def get_recent_conversations(
    user_id: str = Path(..., description="User ID"),
    limit: int = Query(10, ge=1, le=50, description="Number of recent conversations")
):
    """
    Get recent conversations for a user (unique sessions).
    Returns a list of sessions with their first message and activity.
    """
    try:
        recent = await conversation_manager.get_recent_conversations(user_id, limit)
        return {
            "user_id": user_id,
            "count": len(recent),
            "conversations": recent
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{session_id}/metadata")
async def update_conversation_metadata(
    session_id: str = Path(..., description="Session ID"),
    metadata: Dict[str, Any] = Body(..., description="Metadata to update")
):
    """
    Update custom metadata for a conversation session.
    """
    try:
        for key, value in metadata.items():
            await conversation_manager.update_conversation_metadata(session_id, key, value)
        return {
            "session_id": session_id,
            "updated": True,
            "metadata": metadata
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Additional endpoint to get conversation list with pagination
@router.get("/list/{user_id}")
async def list_user_conversations(
    user_id: str = Path(..., description="User ID"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page")
):
    """
    List all conversation sessions for a user with pagination.
    """
    try:
        recent = await conversation_manager.get_recent_conversations(user_id, page * page_size)
        
        start = (page - 1) * page_size
        end = start + page_size
        paginated = recent[start:end]
        
        return {
            "user_id": user_id,
            "page": page,
            "page_size": page_size,
            "total": len(recent),
            "total_pages": (len(recent) + page_size - 1) // page_size,
            "conversations": paginated
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Add this to your routes in backend/api/routes.py
def include_conversation_routes(app):
    """Include conversation routes in the main app"""
    app.include_router(router)