import os
import shutil
import logging
from typing import Dict, Any
from pathlib import Path
from backend.tools.base_tool import BaseTool

logger = logging.getLogger(__name__)

class FileTools(BaseTool):
    """Tools for file system operations"""
    
    def __init__(self):
        super().__init__(
            name="file_tools",
            description="File system operations like open, create, delete"
        )
    
    async def execute(self, parameters: Dict[str, Any], session_id: str = None) -> Dict[str, Any]:
        """Execute file tool action"""
        action = parameters.get("action", "")
        path = parameters.get("path", "")
        content = parameters.get("content", "")
        
        if action == "open_folder":
            return await self._open_folder(path)
        elif action == "create_file":
            return await self._create_file(path, content)
        elif action == "read_file":
            return await self._read_file(path)
        elif action == "delete_file":
            return await self._delete_file(path)
        elif action == "list_directory":
            return await self._list_directory(path)
        
        return {
            "success": False,
            "error": f"Unknown action: {action}"
        }
    
    async def _open_folder(self, path: str) -> Dict[str, Any]:
        """Open a folder in file explorer"""
        try:
            if not path:
                path = os.getcwd()
            
            if os.path.exists(path):
                os.startfile(path) if os.name == "nt" else os.system(f"open '{path}'")
                return {
                    "success": True,
                    "result": f"Opened folder: {path}"
                }
            else:
                return {
                    "success": False,
                    "error": f"Folder not found: {path}"
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to open folder: {str(e)}"
            }
    
    async def _create_file(self, path: str, content: str) -> Dict[str, Any]:
        """Create a new file"""
        try:
            if os.path.exists(path):
                return {
                    "success": False,
                    "error": f"File already exists: {path}"
                }
            
            with open(path, 'w') as f:
                f.write(content)
            
            return {
                "success": True,
                "result": f"Created file: {path}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to create file: {str(e)}"
            }
    
    async def _read_file(self, path: str) -> Dict[str, Any]:
        """Read file contents"""
        try:
            if not os.path.exists(path):
                return {
                    "success": False,
                    "error": f"File not found: {path}"
                }
            
            with open(path, 'r') as f:
                content = f.read()
            
            return {
                "success": True,
                "result": content,
                "filepath": path
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to read file: {str(e)}"
            }
    
    async def _delete_file(self, path: str) -> Dict[str, Any]:
        """Delete a file"""
        try:
            if not os.path.exists(path):
                return {
                    "success": False,
                    "error": f"File not found: {path}"
                }
            
            os.remove(path)
            return {
                "success": True,
                "result": f"Deleted file: {path}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to delete file: {str(e)}"
            }
    
    async def _list_directory(self, path: str) -> Dict[str, Any]:
        """List directory contents"""
        try:
            if not path:
                path = os.getcwd()
            
            if not os.path.exists(path):
                return {
                    "success": False,
                    "error": f"Directory not found: {path}"
                }
            
            items = os.listdir(path)
            return {
                "success": True,
                "result": items,
                "count": len(items),
                "directory": path
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to list directory: {str(e)}"
            }