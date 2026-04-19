import logging
from typing import Dict, Any
from backend.tools.base_tool import BaseTool

logger = logging.getLogger(__name__)

class SearchTools(BaseTool):
    """Tools for web search"""
    
    def __init__(self):
        super().__init__(
            name="search_tools",
            description="Search the web for information"
        )
    
    async def execute(self, parameters: Dict[str, Any], session_id: str = None) -> Dict[str, Any]:
        """Execute search"""
        query = parameters.get("query", "")
        
        if not query:
            return {
                "success": False,
                "error": "No search query provided"
            }
        
        try:
            # Try to use DuckDuckGo search
            results = await self._duckduckgo_search(query)
            
            return {
                "success": True,
                "result": results,
                "query": query
            }
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return {
                "success": False,
                "error": f"Search failed: {str(e)}",
                "result": f"I found information about: {query}. Please check back later for more details."
            }
    
    async def _duckduckgo_search(self, query: str, max_results: int = 5) -> str:
        """Search using DuckDuckGo"""
        try:
            from duckduckgo_search import DDGS
            
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=max_results))
                
                if not results:
                    return f"No results found for '{query}'"
                
                formatted_results = f"Search results for '{query}':\n\n"
                for i, result in enumerate(results, 1):
                    formatted_results += f"{i}. {result.get('title', 'No title')}\n"
                    formatted_results += f"   {result.get('body', 'No description')}\n\n"
                
                return formatted_results
        except ImportError:
            # Fallback if duckduckgo-search not installed
            return f"I found information about: {query}. For detailed search results, please install duckduckgo-search package."
        except Exception as e:
            logger.error(f"DuckDuckGo search error: {e}")
            raise