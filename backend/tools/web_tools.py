import webbrowser
import logging
from typing import Dict, Any
from backend.tools.base_tool import BaseTool

logger = logging.getLogger(__name__)

class WebTools(BaseTool):
    """Tools for web browser control"""
    
    def __init__(self):
        super().__init__(
            name="web_tools",
            description="Open websites and control browser"
        )
        
        self.websites = {
            "youtube": "https://youtube.com",
            "google": "https://google.com",
            "github": "https://github.com",
            "gmail": "https://gmail.com",
            "reddit": "https://reddit.com",
            "twitter": "https://twitter.com",
            "facebook": "https://facebook.com",
            "instagram": "https://instagram.com",
            "linkedin": "https://linkedin.com",
            "amazon": "https://amazon.com",
            "netflix": "https://netflix.com",
            "spotify": "https://spotify.com"
        }
    
    async def execute(self, parameters: Dict[str, Any], session_id: str = None) -> Dict[str, Any]:
        """Execute web tool action"""
        action = parameters.get("action", "open")
        website = parameters.get("website", "").lower()
        
        if action == "open":
            if website in self.websites:
                webbrowser.open(self.websites[website])
                return {
                    "success": True,
                    "result": f"Opened {website} successfully",
                    "url": self.websites[website]
                }
            else:
                return {
                    "success": False,
                    "error": f"Website '{website}' not recognized"
                }
        
        elif action == "search":
            query = parameters.get("query", "")
            search_url = f"https://google.com/search?q={query.replace(' ', '+')}"
            webbrowser.open(search_url)
            return {
                "success": True,
                "result": f"Searched for: {query}",
                "url": search_url
            }
        
        return {
            "success": False,
            "error": f"Unknown action: {action}"
        }