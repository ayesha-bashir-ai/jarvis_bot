#!/usr/bin/env python3
"""
Database Migration Script for JARVIS AI Assistant
Handles schema migrations and version upgrades
"""

import asyncio
import sys
import os
import json
import sqlite3
from datetime import datetime
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.config import settings
from backend.database import engine

class DatabaseMigrator:
    def __init__(self):
        self.db_path = settings.DATABASE_URL.replace("sqlite:///", "")
        self.migrations_table = "schema_migrations"
        self.current_version = 0
        
    async def get_current_version(self):
        """Get current database schema version"""
        try:
            async with engine.begin() as conn:
                # Check if migrations table exists
                result = await conn.execute(
                    f"SELECT name FROM sqlite_master WHERE type='table' AND name='{self.migrations_table}'"
                )
                if result.fetchone():
                    result = await conn.execute("SELECT MAX(version) FROM schema_migrations")
                    version = result.scalar()
                    return version or 0
        except:
            pass
        return 0
    
    async def create_migrations_table(self):
        """Create migrations tracking table"""
        async with engine.begin() as conn:
            await conn.execute(f"""
                CREATE TABLE IF NOT EXISTS {self.migrations_table} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    version INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    success BOOLEAN DEFAULT 1
                )
            """)
            await conn.commit()
    
    async def apply_migration(self, version, name, sql):
        """Apply a single migration"""
        print(f"  Applying migration {version}: {name}...")
        try:
            async with engine.begin() as conn:
                await conn.execute(text(sql))
                await conn.execute(
                    f"INSERT INTO {self.migrations_table} (version, name, success) VALUES (?, ?, 1)",
                    (version, name)
                )
                await conn.commit()
            print(f"  ✅ Migration {version} applied successfully")
            return True
        except Exception as e:
            print(f"  ❌ Migration {version} failed: {e}")
            return False
    
    async def migrate_to_v1(self):
        """Migration to version 1 - Initial schema"""
        migrations = [
            """
            CREATE TABLE IF NOT EXISTS conversations (
                id TEXT PRIMARY KEY,
                session_id TEXT,
                user_id TEXT,
                message TEXT,
                response TEXT,
                intent TEXT,
                tools_used TEXT,
                created_at TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS memories (
                id TEXT PRIMARY KEY,
                user_id TEXT,
                key TEXT,
                value TEXT,
                memory_type TEXT,
                created_at TIMESTAMP,
                updated_at TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS user_profiles (
                id TEXT PRIMARY KEY,
                user_id TEXT UNIQUE,
                name TEXT,
                preferences TEXT,
                settings TEXT,
                created_at TIMESTAMP,
                last_active TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS tool_usage (
                id TEXT PRIMARY KEY,
                tool_name TEXT,
                session_id TEXT,
                parameters TEXT,
                result TEXT,
                success BOOLEAN,
                execution_time INTEGER,
                created_at TIMESTAMP
            )
            """
        ]
        
        for sql in migrations:
            async with engine.begin() as conn:
                await conn.execute(text(sql))
                await conn.commit()
        
        return True
    
    async def migrate_to_v2(self):
        """Migration to version 2 - Add indexes and constraints"""
        migrations = [
            "CREATE INDEX IF NOT EXISTS idx_conversations_session ON conversations(session_id)",
            "CREATE INDEX IF NOT EXISTS idx_conversations_user ON conversations(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_conversations_created ON conversations(created_at)",
            "CREATE INDEX IF NOT EXISTS idx_memories_user ON memories(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_memories_type ON memories(memory_type)",
            "CREATE INDEX IF NOT EXISTS idx_tool_usage_name ON tool_usage(tool_name)",
            "CREATE INDEX IF NOT EXISTS idx_tool_usage_session ON tool_usage(session_id)"
        ]
        
        for sql in migrations:
            async with engine.begin() as conn:
                await conn.execute(text(sql))
                await conn.commit()
        
        return True
    
    async def migrate_to_v3(self):
        """Migration to version 3 - Add message metadata"""
        try:
            async with engine.begin() as conn:
                # Check if column exists
                result = await conn.execute("PRAGMA table_info(conversations)")
                columns = [row[1] for row in result.fetchall()]
                
                if 'metadata' not in columns:
                    await conn.execute("ALTER TABLE conversations ADD COLUMN metadata TEXT")
                    await conn.commit()
                    print("  Added metadata column to conversations")
                
                if 'response_time' not in columns:
                    await conn.execute("ALTER TABLE conversations ADD COLUMN response_time INTEGER")
                    await conn.commit()
                    print("  Added response_time column to conversations")
            
            return True
        except Exception as e:
            print(f"  Migration v3 error: {e}")
            return False
    
    async def migrate_to_v4(self):
        """Migration to version 4 - Add conversation summaries"""
        try:
            async with engine.begin() as conn:
                result = await conn.execute("PRAGMA table_info(conversations)")
                columns = [row[1] for row in result.fetchall()]
                
                if 'summary' not in columns:
                    await conn.execute("ALTER TABLE conversations ADD COLUMN summary TEXT")
                    await conn.commit()
                    print("  Added summary column to conversations")
            
            return True
        except Exception as e:
            print(f"  Migration v4 error: {e}")
            return False
    
    async def run_migrations(self):
        """Run all pending migrations"""
        print("🔄 Starting database migrations...")
        
        await self.create_migrations_table()
        self.current_version = await self.get_current_version()
        
        print(f"Current schema version: {self.current_version}")
        
        migrations = [
            (1, "Initial schema", self.migrate_to_v1),
            (2, "Add indexes", self.migrate_to_v2),
            (3, "Add message metadata", self.migrate_to_v3),
            (4, "Add conversation summaries", self.migrate_to_v4)
        ]
        
        for version, name, migration_func in migrations:
            if version > self.current_version:
                print(f"\n📦 Running migration {version}: {name}")
                success = await migration_func()
                if success:
                    self.current_version = version
                else:
                    print(f"❌ Migration {version} failed!")
                    return False
        
        print(f"\n✅ Migrations complete! Current version: {self.current_version}")
        return True

async def main():
    """Main migration function"""
    print("=" * 50)
    print("🗄️ JARVIS Database Migration Tool")
    print("=" * 50)
    
    migrator = DatabaseMigrator()
    success = await migrator.run_migrations()
    
    if success:
        print("\n✅ Database is up to date!")
    else:
        print("\n❌ Migration failed. Please check the logs.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())