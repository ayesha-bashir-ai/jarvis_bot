from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base, declared_attr
from sqlalchemy import Column, String, Integer, DateTime, Text, JSON, Boolean
from datetime import datetime
import uuid
from backend.config import settings

# Convert sqlite:// to sqlite+aiosqlite://
database_url = settings.DATABASE_URL.replace("sqlite://", "sqlite+aiosqlite://")

engine = create_async_engine(
    database_url,
    echo=settings.DEBUG,
    future=True
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

Base = declarative_base()

class Conversation(Base):
    __tablename__ = "conversations"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(100), index=True)
    user_id = Column(String(100), index=True)
    message = Column(Text)
    response = Column(Text)
    intent = Column(String(50))
    tools_used = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)
    
class Memory(Base):
    __tablename__ = "memories"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(100), index=True)
    key = Column(String(200))
    value = Column(Text)
    memory_type = Column(String(50))  # short_term, long_term, preference
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
class UserProfile(Base):
    __tablename__ = "user_profiles"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(100), unique=True, index=True)
    name = Column(String(100))
    preferences = Column(JSON, default=dict)
    settings = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ToolUsage(Base):
    __tablename__ = "tool_usage"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tool_name = Column(String(100), index=True)
    session_id = Column(String(100), index=True)
    parameters = Column(JSON)
    result = Column(Text)
    success = Column(Boolean, default=True)
    execution_time = Column(Integer)  # milliseconds
    created_at = Column(DateTime, default=datetime.utcnow)

async def init_db():
    """Initialize database tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_db():
    """Get database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

async def close_db():
    """Close database connection"""
    await engine.dispose()