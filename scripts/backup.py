#!/usr/bin/env python3
"""
Database Backup Script for JARVIS AI Assistant
Automated backup management
"""

import os
import sys
import json
import shutil
import argparse
from datetime import datetime
from pathlib import Path
import sqlite3

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.config import settings

class DatabaseBackup:
    def __init__(self, backup_dir="backups"):
        self.db_path = settings.DATABASE_URL.replace("sqlite:///", "")
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)
        
    def create_backup(self, name=None):
        """Create a database backup"""
        if not os.path.exists(self.db_path):
            print(f"❌ Database not found: {self.db_path}")
            return None
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = name or f"jarvis_backup_{timestamp}"
        backup_path = self.backup_dir / f"{backup_name}.db"
        
        try:
            shutil.copy2(self.db_path, backup_path)
            
            # Create metadata file
            metadata = {
                "name": backup_name,
                "timestamp": timestamp,
                "source": str(self.db_path),
                "size": os.path.getsize(backup_path),
                "version": "2.0.0"
            }
            
            metadata_path = self.backup_dir / f"{backup_name}.meta.json"
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            print(f"✅ Backup created: {backup_path}")
            print(f"   Size: {metadata['size'] / 1024:.2f} KB")
            return backup_path
        except Exception as e:
            print(f"❌ Backup failed: {e}")
            return None
    
    def list_backups(self):
        """List all available backups"""
        backups = []
        for file in self.backup_dir.glob("*.db"):
            meta_path = file.with_suffix('.meta.json')
            if meta_path.exists():
                with open(meta_path, 'r') as f:
                    metadata = json.load(f)
                backups.append(metadata)
            else:
                backups.append({
                    "name": file.stem,
                    "timestamp": file.stem.replace("jarvis_backup_", ""),
                    "size": os.path.getsize(file)
                })
        
        return sorted(backups, key=lambda x: x.get('timestamp', ''), reverse=True)
    
    def restore_backup(self, backup_name):
        """Restore a backup"""
        backup_path = self.backup_dir / f"{backup_name}.db"
        
        if not backup_path.exists():
            print(f"❌ Backup not found: {backup_name}")
            return False
        
        # Create backup of current database before restore
        if os.path.exists(self.db_path):
            self.create_backup("pre_restore")
        
        try:
            shutil.copy2(backup_path, self.db_path)
            print(f"✅ Database restored from: {backup_name}")
            return True
        except Exception as e:
            print(f"❌ Restore failed: {e}")
            return False
    
    def clean_old_backups(self, keep_count=10):
        """Remove old backups keeping only the most recent N"""
        backups = self.list_backups()
        
        if len(backups) <= keep_count:
            print(f"Only {len(backups)} backups exist, keeping all")
            return
        
        to_delete = backups[keep_count:]
        for backup in to_delete:
            backup_name = backup['name']
            backup_path = self.backup_dir / f"{backup_name}.db"
            meta_path = self.backup_dir / f"{backup_name}.meta.json"
            
            if backup_path.exists():
                backup_path.unlink()
            if meta_path.exists():
                meta_path.unlink()
            
            print(f"🗑️ Deleted old backup: {backup_name}")
        
        print(f"✅ Cleaned {len(to_delete)} old backups, kept {keep_count}")
    
    def backup_info(self, backup_name):
        """Get detailed information about a backup"""
        backup_path = self.backup_dir / f"{backup_name}.db"
        meta_path = self.backup_dir / f"{backup_name}.meta.json"
        
        if not backup_path.exists():
            print(f"❌ Backup not found: {backup_name}")
            return None
        
        info = {
            "name": backup_name,
            "path": str(backup_path),
            "size": f"{os.path.getsize(backup_path) / 1024:.2f} KB",
            "modified": datetime.fromtimestamp(os.path.getmtime(backup_path)).isoformat()
        }
        
        if meta_path.exists():
            with open(meta_path, 'r') as f:
                metadata = json.load(f)
                info.update(metadata)
        
        # Get database stats
        try:
            conn = sqlite3.connect(backup_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM conversations")
            info['conversations_count'] = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM memories")
            info['memories_count'] = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM user_profiles")
            info['users_count'] = cursor.fetchone()[0]
            
            conn.close()
        except:
            info['error'] = "Could not read database stats"
        
        return info

def main():
    parser = argparse.ArgumentParser(description="JARVIS Database Backup Tool")
    parser.add_argument("action", choices=["create", "list", "restore", "clean", "info"],
                       help="Action to perform")
    parser.add_argument("--name", help="Backup name")
    parser.add_argument("--keep", type=int, default=10, help="Number of backups to keep")
    
    args = parser.parse_args()
    
    backup = DatabaseBackup()
    
    if args.action == "create":
        backup.create_backup(args.name)
    
    elif args.action == "list":
        backups = backup.list_backups()
        print("\n📋 Available Backups:")
        print("-" * 60)
        for b in backups:
            size = b.get('size', 0)
            if isinstance(size, int):
                size_str = f"{size / 1024:.2f} KB"
            else:
                size_str = size
            print(f"  • {b['name']} - {b.get('timestamp', 'Unknown')} - {size_str}")
        print(f"\nTotal: {len(backups)} backups")
    
    elif args.action == "restore":
        if not args.name:
            print("❌ Please specify backup name with --name")
            sys.exit(1)
        backup.restore_backup(args.name)
    
    elif args.action == "clean":
        backup.clean_old_backups(args.keep)
    
    elif args.action == "info":
        if not args.name:
            print("❌ Please specify backup name with --name")
            sys.exit(1)
        info = backup.backup_info(args.name)
        if info:
            print(f"\n📊 Backup Information: {args.name}")
            print("-" * 40)
            for key, value in info.items():
                print(f"  {key}: {value}")

if __name__ == "__main__":
    main()