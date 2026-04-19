from pydantic_settings import BaseSettings
from typing import List
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # API Keys
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
    WEATHER_API_KEY: str = os.getenv("WEATHER_API_KEY", "")
    NEWS_API_KEY: str = os.getenv("NEWS_API_KEY", "")
    SPOTIFY_CLIENT_ID: str = os.getenv("SPOTIFY_CLIENT_ID", "")
    SPOTIFY_CLIENT_SECRET: str = os.getenv("SPOTIFY_CLIENT_SECRET", "")
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///data/jarvis.db")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # Application
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-this")
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "your-jwt-secret-key")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"
    
    # Voice Settings
    WAKE_WORD: str = os.getenv("WAKE_WORD", "jarvis")
    VOICE_LANGUAGE: str = os.getenv("VOICE_LANGUAGE", "en-US")
    TTS_ENGINE: str = os.getenv("TTS_ENGINE", "pyttsx3")
    
    # API Settings
    API_VERSION: str = os.getenv("API_VERSION", "v1")
    CORS_ORIGINS: List[str] = eval(os.getenv("CORS_ORIGINS", '["http://localhost:3000","http://localhost:8000"]'))
    
    # LLM Settings
    DEFAULT_MODEL: str = os.getenv("DEFAULT_MODEL", "gpt-4")
    TEMPERATURE: float = float(os.getenv("TEMPERATURE", "0.7"))
    MAX_TOKENS: int = int(os.getenv("MAX_TOKENS", "2000"))
    
    # Memory Settings
    MEMORY_SIZE: int = int(os.getenv("MEMORY_SIZE", "50"))
    LONG_TERM_MEMORY: bool = os.getenv("LONG_TERM_MEMORY", "true").lower() == "true"
    CONTEXT_WINDOW: int = int(os.getenv("CONTEXT_WINDOW", "10"))
    
    # Plugin Settings
    PLUGINS_ENABLED: bool = os.getenv("PLUGINS_ENABLED", "true").lower() == "true"
    PLUGINS_DIR: str = os.getenv("PLUGINS_DIR", "./backend/plugins")
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()