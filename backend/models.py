from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class ChatMessage(BaseModel):
    role: MessageRole
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Optional[Dict[str, Any]] = None

class ChatRequest(BaseModel):
    message: str
    session_id: str
    user_id: Optional[str] = "default"
    context: Optional[List[ChatMessage]] = None

class ChatResponse(BaseModel):
    message: str
    intent: str
    tools_used: List[str] = []
    response_time: int
    confidence: float = 1.0

class ToolCall(BaseModel):
    tool_name: str
    parameters: Dict[str, Any]
    session_id: str
    user_id: str

class ToolResult(BaseModel):
    success: bool
    result: Any
    error: Optional[str] = None
    execution_time: float

class IntentType(str, Enum):
    GREETING = "greeting"
    QUESTION = "question"
    COMMAND = "command"
    CALCULATION = "calculation"
    SEARCH = "search"
    SYSTEM_CONTROL = "system_control"
    BROWSER = "browser"
    UNKNOWN = "unknown"

class Intent(BaseModel):
    type: IntentType
    name: str
    confidence: float
    requires_tool: bool = False
    tools: List[str] = []
    entities: Dict[str, Any] = {}