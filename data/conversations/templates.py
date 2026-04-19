"""
Response Templates - Pre-defined response templates for common scenarios
"""

from typing import Dict, Any, Optional
from datetime import datetime
import random

class ResponseTemplates:
    """Collection of response templates for JARVIS"""
    
    GREETINGS = [
        "Hello Commander! How may I assist you today?",
        "Hi there! Ready to help with whatever you need.",
        "Greetings! JARVIS at your service.",
        "Hey! What can I do for you today?",
        "Good to see you, Commander! How can I help?"
    ]
    
    FAREWELLS = [
        "Goodbye, Commander! Call on me anytime.",
        "See you later! I'll be here when you need me.",
        "Farewell! Have a great day.",
        "Until next time, Commander!",
        "Signing off. Stay productive!"
    ]
    
    HELP = """I can help you with:
• 🌐 Opening websites (say "open YouTube")
• ⏰ Time and date information
• 🧮 Calculations (say "calculate 5 + 3")
• 📸 Taking screenshots
• 🔍 Web searches
• 💻 System commands
• 🎭 Telling jokes
• 🌤️ Weather information

What would you like me to do?"""
    
    ERROR = "I apologize, but I encountered an issue. Please try again or rephrase your request."
    
    @classmethod
    def get_greeting(cls, name: Optional[str] = None) -> str:
        """Get a random greeting"""
        greeting = random.choice(cls.GREETINGS)
        if name:
            greeting = greeting.replace("Commander", name)
        return greeting
    
    @classmethod
    def get_farewell(cls) -> str:
        """Get a random farewell"""
        return random.choice(cls.FAREWELLS)
    
    @classmethod
    def get_help(cls) -> str:
        """Get help message"""
        return cls.HELP
    
    @classmethod
    def get_error(cls) -> str:
        """Get error message"""
        return cls.ERROR
    
    @classmethod
    def get_time_response(cls, time: datetime) -> str:
        """Get time response template"""
        formatted_time = time.strftime("%I:%M %p")
        return f"The current time is {formatted_time}, Commander."
    
    @classmethod
    def get_date_response(cls, date: datetime) -> str:
        """Get date response template"""
        formatted_date = date.strftime("%A, %B %d, %Y")
        return f"Today is {formatted_date}."
    
    @classmethod
    def get_calculation_response(cls, expression: str, result: Any) -> str:
        """Get calculation response template"""
        return f"The result of {expression} is {result}."
    
    @classmethod
    def get_website_response(cls, website: str) -> str:
        """Get website opening response"""
        return f"Opening {website} for you, Commander! 🚀"
    
    @classmethod
    def get_search_response(cls, query: str) -> str:
        """Get search response template"""
        return f"Searching for '{query}'... I'll find the best results for you."
    
    @classmethod
    def get_joke_response(cls) -> str:
        """Get a random joke"""
        jokes = [
            "Why don't scientists trust atoms? Because they make up everything!",
            "Why did the scarecrow win an award? He was outstanding in his field!",
            "Why don't eggs tell jokes? They'd crack each other up!",
            "What do you call a fake noodle? An impasta!",
            "Why did the math book look so sad? Because it had too many problems!",
            "What do you call a bear with no teeth? A gummy bear!",
            "Why couldn't the bicycle stand up by itself? It was two-tired!"
        ]
        return random.choice(jokes)
    
    @classmethod
    def get_unknown_response(cls) -> str:
        """Get response for unknown queries"""
        responses = [
            "I'm not sure I understand. Could you rephrase that?",
            "I didn't quite catch that. Can you please clarify?",
            "I'm still learning! Could you explain what you mean?",
            "I'm not certain about that. Try asking something else?",
            "Hmm, I'm not sure how to respond to that. Can you try a different approach?"
        ]
        return random.choice(responses)
    
    @classmethod
    def get_thanks_response(cls) -> str:
        """Get thanks response"""
        thanks = [
            "You're welcome, Commander! Always happy to help.",
            "My pleasure! Anything else I can do for you?",
            "Glad I could help! Let me know if you need anything else.",
            "Anytime, Commander! That's what I'm here for."
        ]
        return random.choice(thanks)
    
    @classmethod
    def get_status_response(cls, status: str) -> str:
        """Get system status response"""
        status_messages = {
            "online": "All systems operational. JARVIS ready for duty.",
            "offline": "Some systems are offline. Please check the connection.",
            "maintenance": "System maintenance in progress. Limited functionality available.",
            "error": "System error detected. Please restart the application."
        }
        return status_messages.get(status, "System status: Unknown")