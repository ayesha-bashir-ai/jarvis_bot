import logging
from typing import Callable, Optional
from backend.config import settings

logger = logging.getLogger(__name__)

class WakeWordService:
    """Wake word detection service"""
    
    def __init__(self):
        self.wake_word = settings.WAKE_WORD.lower()
        self.is_listening = False
        self.callback = None
        
        # Try to initialize wake word detector
        try:
            # Use simple keyword detection for now
            # For production, use porcupine or similar
            logger.info(f"Wake word service initialized with keyword: {self.wake_word}")
        except Exception as e:
            logger.error(f"Failed to initialize wake word service: {e}")
    
    async def start_detection(self, callback: Callable):
        """Start wake word detection"""
        self.callback = callback
        self.is_listening = True
        logger.info("Wake word detection started")
        
        # For demo purposes, we'll just simulate detection
        # In production, implement actual audio detection
        while self.is_listening:
            await asyncio.sleep(0.1)
    
    async def stop_detection(self):
        """Stop wake word detection"""
        self.is_listening = False
        logger.info("Wake word detection stopped")
    
    def check_wake_word(self, text: str) -> bool:
        """Check if text contains wake word"""
        return self.wake_word in text.lower()