class JARVISException(Exception):
    """Base exception for JARVIS"""
    pass

class ToolException(JARVISException):
    """Exception raised when tool execution fails"""
    pass

class LLMException(JARVISException):
    """Exception raised when LLM fails"""
    pass

class DatabaseException(JARVISException):
    """Exception raised when database operation fails"""
    pass

class VoiceException(JARVISException):
    """Exception raised when voice service fails"""
    pass