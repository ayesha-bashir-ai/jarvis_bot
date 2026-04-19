"""
Conversation Analytics - Analyze conversation patterns and statistics
"""

from typing import Dict, List, Any, Optional
from collections import Counter
from datetime import datetime, timedelta

class ConversationAnalytics:
    """Analyze conversation data and generate insights"""
    
    @staticmethod
    async def get_message_stats(conversations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get message statistics"""
        user_messages = [m for m in conversations if m.get("role") == "user"]
        assistant_messages = [m for m in conversations if m.get("role") == "assistant"]
        
        return {
            "total_messages": len(conversations),
            "user_messages": len(user_messages),
            "assistant_messages": len(assistant_messages),
            "user_assistant_ratio": len(user_messages) / max(len(assistant_messages), 1),
            "average_user_length": sum(len(m.get("content", "")) for m in user_messages) / max(len(user_messages), 1),
            "average_assistant_length": sum(len(m.get("content", "")) for m in assistant_messages) / max(len(assistant_messages), 1),
            "total_characters": sum(len(m.get("content", "")) for m in conversations)
        }
    
    @staticmethod
    async def get_time_analysis(conversations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze conversation timing"""
        timestamps = []
        for msg in conversations:
            ts = msg.get("timestamp")
            if ts:
                try:
                    timestamps.append(datetime.fromisoformat(ts))
                except:
                    pass
        
        if not timestamps:
            return {}
        
        # Calculate time differences
        time_diffs = []
        for i in range(1, len(timestamps)):
            diff = (timestamps[i] - timestamps[i-1]).total_seconds()
            time_diffs.append(diff)
        
        return {
            "start_time": min(timestamps).isoformat() if timestamps else None,
            "end_time": max(timestamps).isoformat() if timestamps else None,
            "duration_minutes": (max(timestamps) - min(timestamps)).total_seconds() / 60 if timestamps else 0,
            "average_response_time_seconds": sum(time_diffs) / len(time_diffs) if time_diffs else 0,
            "fastest_response_seconds": min(time_diffs) if time_diffs else 0,
            "slowest_response_seconds": max(time_diffs) if time_diffs else 0
        }
    
    @staticmethod
    async def get_topic_analysis(conversations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze conversation topics"""
        topics = Counter()
        keywords = {
            "greeting": ["hello", "hi", "hey", "good morning", "good afternoon"],
            "time": ["time", "clock", "what time"],
            "date": ["date", "today", "day"],
            "weather": ["weather", "temperature", "forecast", "rain", "sun"],
            "search": ["search", "find", "look up", "google"],
            "calculator": ["calculate", "calc", "math", "plus", "minus", "times", "divide"],
            "browser": ["open", "youtube", "google", "browser", "website"],
            "system": ["shutdown", "restart", "screenshot", "lock"],
            "help": ["help", "what can you do", "capabilities"],
            "joke": ["joke", "funny", "laugh"]
        }
        
        for msg in conversations:
            content = msg.get("content", "").lower()
            for topic, words in keywords.items():
                if any(word in content for word in words):
                    topics[topic] += 1
        
        return {
            "top_topics": topics.most_common(5),
            "topic_distribution": dict(topics),
            "unique_topics": len(topics)
        }
    
    @staticmethod
    async def get_sentiment_analysis(conversations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Simple sentiment analysis (can be enhanced with NLP)"""
        positive_words = ["good", "great", "awesome", "excellent", "happy", "love", "thanks", "thank"]
        negative_words = ["bad", "terrible", "awful", "hate", "dislike", "sorry", "error", "problem"]
        
        positive_count = 0
        negative_count = 0
        
        for msg in conversations:
            content = msg.get("content", "").lower()
            if any(word in content for word in positive_words):
                positive_count += 1
            if any(word in content for word in negative_words):
                negative_count += 1
        
        total = len(conversations)
        
        return {
            "positive_percentage": (positive_count / total * 100) if total > 0 else 0,
            "negative_percentage": (negative_count / total * 100) if total > 0 else 0,
            "neutral_percentage": 100 - ((positive_count + negative_count) / total * 100) if total > 0 else 100,
            "positive_count": positive_count,
            "negative_count": negative_count
        }
    
    @staticmethod
    async def get_user_engagement(conversations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze user engagement metrics"""
        user_messages = [m for m in conversations if m.get("role") == "user"]
        
        # Count questions
        questions = sum(1 for m in user_messages if "?" in m.get("content", ""))
        
        # Count commands
        commands = sum(1 for m in user_messages if any(word in m.get("content", "").lower() 
                      for word in ["open", "calculate", "search", "tell", "show"]))
        
        return {
            "total_sessions": len(set(m.get("session_id") for m in conversations if m.get("session_id"))),
            "questions_asked": questions,
            "commands_given": commands,
            "engagement_score": (questions + commands) / max(len(user_messages), 1) * 100,
            "average_messages_per_session": len(conversations) / max(len(set(m.get("session_id") for m in conversations)), 1)
        }
    
    @staticmethod
    async def generate_report(conversations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate complete analytics report"""
        return {
            "message_stats": await ConversationAnalytics.get_message_stats(conversations),
            "time_analysis": await ConversationAnalytics.get_time_analysis(conversations),
            "topic_analysis": await ConversationAnalytics.get_topic_analysis(conversations),
            "sentiment_analysis": await ConversationAnalytics.get_sentiment_analysis(conversations),
            "user_engagement": await ConversationAnalytics.get_user_engagement(conversations)
        }