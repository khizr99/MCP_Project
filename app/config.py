"""
Application Configuration
Manages all application settings and environment variables
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings from environment variables"""
    
    # Application
    APP_NAME: str = "MCP Multi-Agent Orchestration"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./mcp_database.db"
    
    # Agent Configuration
    MAX_AGENTS: int = 10
    AGENT_TIMEOUT: int = 300
    
    # Orchestrator Settings
    MAX_CONCURRENT_WORKFLOWS: int = 5
    WORKFLOW_RETENTION_DAYS: int = 30
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
