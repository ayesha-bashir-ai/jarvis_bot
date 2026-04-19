#!/usr/bin/env python3
"""
Database Initialization Script for JARVIS AI Assistant
Creates all necessary tables and initial data
"""

import asyncio
import sys
import os
import json
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import init_db, engine, get_db
from backend.models import Conversation, Memory, UserProfile, ToolUsage
from sqlalchemy import text
from backend.config import settings

async def create_tables():
    """Create all database tables"""
    print("📊 Creating database tables...")
    try:
        await init_db()
        print("✅ Tables created successfully!")
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        raise

async def seed_initial_data():
    """Seed initial data into database"""
    print("🌱 Seeding initial data...")
    
    async with engine.begin() as conn:
        # Create default user profile
        await conn.execute(text("""
            INSERT OR IGNORE INTO user_profiles (id, user_id, name, preferences, settings, created_at)
            VALUES (
                'default-user-id',
                'default',
                'Commander',
                '{"theme": "dark", "voice_enabled": true, "language": "en-US"}',
                '{"notifications": true, "auto_save": true}',
                CURRENT_TIMESTAMP
            )
        """))
        
        # Create system conversation starter
        await conn.execute(text("""
            INSERT OR IGNORE INTO conversations (id, session_id, user_id, message, response, intent, created_at)
            VALUES (
                'system-init',
                'system',
                'system',
                'JARVIS system initialized',
                'System ready and operational',
                'system',
                CURRENT_TIMESTAMP
            )
        """))
        
        # Create initial memory items
        await conn.execute(text("""
            INSERT OR IGNORE INTO memories (id, user_id, key, value, memory_type, created_at)
            VALUES 
                ('mem-1', 'default', 'system_version', '{"version": "2.0.0"}', 'long_term', CURRENT_TIMESTAMP),
                ('mem-2', 'default', 'system_capabilities', '{"capabilities": ["voice", "web_search", "calculations", "system_control"]}', 'long_term', CURRENT_TIMESTAMP)
        """))
        
        await conn.commit()
    
    print("✅ Seed data inserted successfully!")

async def create_indexes():
    """Create database indexes for performance"""
    print("📇 Creating indexes...")
    
    async with engine.begin() as conn:
        await conn.execute(text("CREATE INDEX IF NOT EXISTS idx_conversations_session ON conversations(session_id)"))
        await conn.execute(text("CREATE INDEX IF NOT EXISTS idx_conversations_user ON conversations(user_id)"))
        await conn.execute(text("CREATE INDEX IF NOT EXISTS idx_conversations_created ON conversations(created_at)"))
        await conn.execute(text("CREATE INDEX IF NOT EXISTS idx_memories_user ON memories(user_id)"))
        await conn.execute(text("CREATE INDEX IF NOT EXISTS idx_memories_type ON memories(memory_type)"))
        await conn.execute(text("CREATE INDEX IF NOT EXISTS idx_tool_usage_name ON tool_usage(tool_name)"))
        await conn.execute(text("CREATE INDEX IF NOT EXISTS idx_tool_usage_session ON tool_usage(session_id)"))
        await conn.commit()
    
    print("✅ Indexes created successfully!")

async def verify_database():
    """Verify database setup"""
    print("🔍 Verifying database setup...")
    
    async with engine.begin() as conn:
        # Check tables
        result = await conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
        tables = [row[0] for row in result.fetchall()]
        
        expected_tables = ['conversations', 'memories', 'user_profiles', 'tool_usage']
        
        for table in expected_tables:
            if table in tables:
                print(f"  ✓ {table} table exists")
            else:
                print(f"  ✗ {table} table missing")
        
        # Check default user
        result = await conn.execute(text("SELECT COUNT(*) FROM user_profiles WHERE user_id = 'default'"))
        count = result.scalar()
        print(f"  ✓ Default user profile: {'exists' if count > 0 else 'missing'}")
    
    print("✅ Database verification complete!")

async def backup_database():
    """Backup existing database"""
    import shutil
    from pathlib import Path
    
    db_path = Path(settings.DATABASE_URL.replace("sqlite:///", ""))
    if db_path.exists():
        backup_path = db_path.parent / f"{db_path.stem}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}{db_path.suffix}"
        shutil.copy(db_path, backup_path)
        print(f"💾 Database backed up to: {backup_path}")
        return True
    return False

async def main():
    """Main initialization function"""
    print("=" * 50)
    print("🤖 JARVIS AI Assistant - Database Initialization")
    print("=" * 50)
    
    # Check if database exists and backup
    db_path = settings.DATABASE_URL.replace("sqlite:///", "")
    if os.path.exists(db_path):
        print("📦 Existing database found, creating backup...")
        await backup_database()
    
    # Initialize database
    await create_tables()
    await create_indexes()
    await seed_initial_data()
    await verify_database()
    
    print("\n" + "=" * 50)
    print("✅ JARVIS Database initialization complete!")
    print("=" * 50)
    print("\n📝 Next steps:")
    print("  1. Run 'make up' to start the services")
    print("  2. Open http://localhost:3000 in your browser")
    print("  3. Start chatting with JARVIS!")

if __name__ == "__main__":
    asyncio.run(main())