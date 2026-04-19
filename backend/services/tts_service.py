import logging
import base64
from typing import Optional
from backend.config import settings

logger = logging.getLogger(__name__)

class TTSService:
    """Text-to-Speech service"""
    
    def __init__(self):
        self.engine = settings.TTS_ENGINE
        self.language = settings.VOICE_LANGUAGE
        
        # Initialize pyttsx3 for offline TTS
        try:
            import pyttsx3
            self.tts_engine = pyttsx3.init()
            self.tts_engine.setProperty('rate', 150)
            self.tts_engine.setProperty('volume', 0.9)
            logger.info("TTS engine initialized")
        except Exception as e:
            logger.error(f"Failed to initialize TTS: {e}")
            self.tts_engine = None
    
    async def synthesize(self, text: str) -> Optional[str]:
        """Convert text to speech and return base64 audio"""
        try:
            if self.tts_engine:
                # Save to temporary file
                import tempfile
                import os
                
                with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmpfile:
                    temp_path = tmpfile.name
                
                self.tts_engine.save_to_file(text, temp_path)
                self.tts_engine.runAndWait()
                
                # Read and encode audio file
                with open(temp_path, 'rb') as f:
                    audio_data = base64.b64encode(f.read()).decode()
                
                # Clean up
                os.unlink(temp_path)
                
                return audio_data
        except Exception as e:
            logger.error(f"TTS synthesis error: {e}")
        
        return None
    
    def speak_sync(self, text: str):
        """Synchronous speech output"""
        if self.tts_engine:
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()