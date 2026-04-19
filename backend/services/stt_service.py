import logging
import base64
import tempfile
import os
from typing import Optional
from backend.config import settings

logger = logging.getLogger(__name__)

class STTService:
    """Speech-to-Text service"""
    
    def __init__(self):
        self.language = settings.VOICE_LANGUAGE
        
        # Initialize speech recognition
        try:
            import speech_recognition as sr
            self.recognizer = sr.Recognizer()
            self.microphone = sr.Microphone()
            logger.info("STT service initialized")
        except Exception as e:
            logger.error(f"Failed to initialize STT: {e}")
            self.recognizer = None
    
    async def transcribe(self, audio_data: Optional[str] = None) -> str:
        """Transcribe audio to text"""
        try:
            if audio_data:
                # Decode base64 audio
                audio_bytes = base64.b64decode(audio_data)
                
                # Save to temporary file
                with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmpfile:
                    tmpfile.write(audio_bytes)
                    temp_path = tmpfile.name
                
                # Transcribe using speech_recognition
                import speech_recognition as sr
                with sr.AudioFile(temp_path) as source:
                    audio = self.recognizer.record(source)
                    text = self.recognizer.recognize_google(audio, language=self.language)
                
                # Clean up
                os.unlink(temp_path)
                
                return text
            else:
                # Use microphone for live transcription
                return await self._listen_microphone()
                
        except Exception as e:
            logger.error(f"STT transcription error: {e}")
            return ""
    
    async def _listen_microphone(self) -> str:
        """Listen from microphone"""
        try:
            import speech_recognition as sr
            
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source)
                audio = self.recognizer.listen(source, timeout=5)
                text = self.recognizer.recognize_google(audio, language=self.language)
                return text
        except sr.WaitTimeoutError:
            return ""
        except sr.UnknownValueError:
            return ""
        except Exception as e:
            logger.error(f"Microphone listening error: {e}")
            return ""