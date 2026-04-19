import logging
from fastapi import HTTPException
from backend.api.routes import VoiceCommandRequest
from backend.services.stt_service import STTService
from backend.services.tts_service import TTSService
from backend.core.jarvis_brain import get_brain_instance

logger = logging.getLogger(__name__)

stt_service = STTService()
tts_service = TTSService()

async def handle_voice_command(request: VoiceCommandRequest):
    """Handle voice command"""
    try:
        brain = get_brain_instance()
        
        # If audio data provided, convert to text
        text_command = request.audio_data
        if text_command:
            # Convert speech to text
            text_command = await stt_service.transcribe(request.audio_data)
        
        if not text_command:
            return {
                "success": False,
                "error": "No speech detected",
                "command": "",
                "response": "I couldn't hear you. Please try again."
            }
        
        # Process command through brain
        result = await brain.process_message(
            message=text_command,
            session_id=request.session_id,
            user_id=request.user_id
        )
        
        # Convert response to speech
        audio_response = await tts_service.synthesize(result["message"])
        
        return {
            "success": True,
            "command": text_command,
            "response": result["message"],
            "audio": audio_response,
            "intent": result["intent"]
        }
        
    except Exception as e:
        logger.error(f"Voice command error: {e}")
        return {
            "success": False,
            "error": str(e),
            "command": "",
            "response": "Sorry, I encountered an error processing your voice command."
        }