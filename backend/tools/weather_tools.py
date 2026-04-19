import logging
from typing import Dict, Any
from backend.tools.base_tool import BaseTool

logger = logging.getLogger(__name__)

class WeatherTools(BaseTool):
    """Tools for weather information"""
    
    def __init__(self):
        super().__init__(
            name="weather_tools",
            description="Get weather information"
        )
    
    async def execute(self, parameters: Dict[str, Any], session_id: str = None) -> Dict[str, Any]:
        """Execute weather tool"""
        location = parameters.get("location", "London")
        
        try:
            # Try to get real weather data
            weather_data = await self._get_weather(location)
            
            return {
                "success": True,
                "result": weather_data,
                "location": location
            }
        except Exception as e:
            logger.error(f"Weather API error: {e}")
            # Fallback mock data
            return {
                "success": True,
                "result": f"Weather in {location}: 22°C, Partly Cloudy. (Mock data - API key required for real data)",
                "location": location
            }
    
    async def _get_weather(self, location: str) -> str:
        """Get weather from API (requires API key)"""
        import aiohttp
        
        # This is a placeholder. You need to sign up for a weather API key
        # Recommended: OpenWeatherMap (free tier available)
        api_key = "YOUR_API_KEY_HERE"  # Replace with actual API key
        
        if api_key == "YOUR_API_KEY_HERE":
            # Return mock data if no API key
            return f"Weather in {location}: 22°C, Partly Cloudy. (Get a free API key from OpenWeatherMap for real data)"
        
        url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}&units=metric"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    temp = data['main']['temp']
                    condition = data['weather'][0]['description']
                    return f"Weather in {location}: {temp}°C, {condition}"
                else:
                    return f"Could not fetch weather for {location}"