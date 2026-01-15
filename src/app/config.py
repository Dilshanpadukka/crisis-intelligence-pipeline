"""
Application configuration management.

Supports multiple environments (development, staging, production).
"""

import os
from typing import Literal
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class APIConfig(BaseModel):
    """API server configuration."""
    
    host: str = Field(default="0.0.0.0", description="API host")
    port: int = Field(default=8000, description="API port")
    reload: bool = Field(default=False, description="Enable auto-reload (dev only)")
    workers: int = Field(default=1, description="Number of worker processes")
    log_level: str = Field(default="info", description="Logging level")


class LLMConfig(BaseModel):
    """LLM provider configuration."""
    
    default_provider: Literal["openai", "google", "groq"] = Field(
        default="groq",
        description="Default LLM provider"
    )
    openai_api_key: str = Field(default="", description="OpenAI API key")
    gemini_api_key: str = Field(default="", description="Google Gemini API key")
    groq_api_key: str = Field(default="", description="Groq API key")


class SecurityConfig(BaseModel):
    """Security configuration."""
    
    cors_origins: list[str] = Field(
        default=["*"],
        description="Allowed CORS origins"
    )
    api_key_enabled: bool = Field(
        default=False,
        description="Enable API key authentication"
    )
    api_key: str = Field(default="", description="API key for authentication")
    rate_limit_enabled: bool = Field(
        default=False,
        description="Enable rate limiting"
    )
    rate_limit_requests: int = Field(
        default=100,
        description="Max requests per minute"
    )


class AppConfig(BaseModel):
    """Complete application configuration."""
    
    environment: Literal["development", "staging", "production"] = Field(
        default="development",
        description="Deployment environment"
    )
    api: APIConfig = Field(default_factory=APIConfig)
    llm: LLMConfig = Field(default_factory=LLMConfig)
    security: SecurityConfig = Field(default_factory=SecurityConfig)


def load_config() -> AppConfig:
    """
    Load configuration from environment variables.
    
    Returns:
        AppConfig instance
    """
    environment = os.getenv("ENVIRONMENT", "development")
    
    # API configuration
    api_config = APIConfig(
        host=os.getenv("API_HOST", "0.0.0.0"),
        port=int(os.getenv("API_PORT", "8000")),
        reload=os.getenv("API_RELOAD", "false").lower() == "true",
        workers=int(os.getenv("API_WORKERS", "1")),
        log_level=os.getenv("LOG_LEVEL", "info")
    )
    
    # LLM configuration
    llm_config = LLMConfig(
        default_provider=os.getenv("DEFAULT_PROVIDER", "groq"),  # type: ignore
        openai_api_key=os.getenv("OPENAI_API_KEY", ""),
        gemini_api_key=os.getenv("GEMINI_API_KEY", ""),
        groq_api_key=os.getenv("GROQ_API_KEY", "")
    )
    
    # Security configuration
    cors_origins = os.getenv("CORS_ORIGINS", "*").split(",")
    security_config = SecurityConfig(
        cors_origins=cors_origins,
        api_key_enabled=os.getenv("API_KEY_ENABLED", "false").lower() == "true",
        api_key=os.getenv("API_KEY", ""),
        rate_limit_enabled=os.getenv("RATE_LIMIT_ENABLED", "false").lower() == "true",
        rate_limit_requests=int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
    )
    
    return AppConfig(
        environment=environment,  # type: ignore
        api=api_config,
        llm=llm_config,
        security=security_config
    )


# Global config instance
config = load_config()

