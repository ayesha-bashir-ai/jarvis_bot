import os
import subprocess
import platform
import logging
from typing import Dict, Any
from backend.tools.base_tool import BaseTool

logger = logging.getLogger(__name__)

class SystemTools(BaseTool):
    """Tools for system control"""
    
    def __init__(self):
        super().__init__(
            name="system_tools",
            description="Control system operations like shutdown, restart, screenshot"
        )
    
    async def execute(self, parameters: Dict[str, Any], session_id: str = None) -> Dict[str, Any]:
        """Execute system tool action"""
        action = parameters.get("action", "")
        
        if action == "shutdown":
            return await self._shutdown()
        elif action == "restart":
            return await self._restart()
        elif action == "lock":
            return await self._lock_screen()
        elif action == "screenshot":
            return await self._take_screenshot()
        elif action == "open_app":
            app = parameters.get("app", "")
            return await self._open_application(app)
        
        return {
            "success": False,
            "error": f"Unknown action: {action}"
        }
    
    async def _shutdown(self) -> Dict[str, Any]:
        """Shutdown the system"""
        try:
            system = platform.system()
            if system == "Windows":
                os.system("shutdown /s /t 5")
            elif system == "Linux" or system == "Darwin":
                os.system("shutdown -h +1")
            
            return {
                "success": True,
                "result": "System will shutdown in 5 seconds"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Shutdown failed: {str(e)}"
            }
    
    async def _restart(self) -> Dict[str, Any]:
        """Restart the system"""
        try:
            system = platform.system()
            if system == "Windows":
                os.system("shutdown /r /t 5")
            elif system == "Linux" or system == "Darwin":
                os.system("shutdown -r +1")
            
            return {
                "success": True,
                "result": "System will restart in 5 seconds"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Restart failed: {str(e)}"
            }
    
    async def _lock_screen(self) -> Dict[str, Any]:
        """Lock the screen"""
        try:
            system = platform.system()
            if system == "Windows":
                import ctypes
                ctypes.windll.user32.LockWorkStation()
            elif system == "Darwin":
                subprocess.run(["osascript", "-e", 'tell application "System Events" to keystroke "q" using {command down, control down}'])
            
            return {
                "success": True,
                "result": "Screen locked"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Lock screen failed: {str(e)}"
            }
    
    async def _take_screenshot(self) -> Dict[str, Any]:
        """Take a screenshot"""
        try:
            import pyautogui
            from datetime import datetime
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.png"
            
            # Create screenshots directory if not exists
            os.makedirs("screenshots", exist_ok=True)
            filepath = os.path.join("screenshots", filename)
            
            screenshot = pyautogui.screenshot()
            screenshot.save(filepath)
            
            return {
                "success": True,
                "result": f"Screenshot saved as {filepath}",
                "filepath": filepath
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Screenshot failed: {str(e)}"
            }
    
    async def _open_application(self, app_name: str) -> Dict[str, Any]:
        """Open an application"""
        try:
            apps = {
                "notepad": "notepad.exe",
                "calculator": "calc.exe",
                "calendar": "calendar:",
                "terminal": "cmd.exe" if platform.system() == "Windows" else "terminal",
                "vscode": "code",
                "chrome": "chrome",
                "firefox": "firefox",
                "spotify": "spotify"
            }
            
            if app_name.lower() in apps:
                command = apps[app_name.lower()]
                subprocess.Popen(command, shell=True)
                return {
                    "success": True,
                    "result": f"Opened {app_name}"
                }
            else:
                return {
                    "success": False,
                    "error": f"Application '{app_name}' not recognized"
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to open application: {str(e)}"
            }